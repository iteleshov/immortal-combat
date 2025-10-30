import hashlib
import os
import time
import threading
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed
import psycopg2

from backend.services.aggregation import agg
from backend.services.mcp_uniprot_source import uniprot
from backend.services.kegg_source import kegg
from backend.services.open_genes_source import opengenes
from backend.services.uniprot_source import UniProtSource
from backend.services.ncbi_source import NcbiSource
from backend.services.gnomad_source import gnomad
from backend.services.ncbi_mcp_server import ncbi_mcp_server
from backend.models.gene_response import GeneResponse

class KnowledgeBaseFacade:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.environ["PG_HOST"],
            port=os.environ.get("PG_PORT", 5432),
            dbname=os.environ["PG_DB"],
            user=os.environ["PG_USER"],
            password=os.environ["PG_PASSWORD"]
        )
        self.uniprot = UniProtSource()
        self.ncbi = NcbiSource()
        self._cache_lock = threading.Lock()

        self._ensure_table()

        self._queue = Queue()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        print("[QUEUE] Worker thread started")
    def _ensure_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS gene_articles (
                gene_symbol TEXT PRIMARY KEY,
                article TEXT
            )
            """)
            self.conn.commit()

    def _save_to_db(self, gene_symbol: str, article: str):
        with self.conn.cursor() as cur:
            cur.execute("""
            INSERT INTO gene_articles (gene_symbol, article)
            VALUES (%s, %s)
            ON CONFLICT (gene_symbol) DO UPDATE
            SET article = EXCLUDED.article
            """, (gene_symbol, article))
            self.conn.commit()

    def _load_from_db(self, gene_symbol: str) -> str | None:
        with self.conn.cursor() as cur:
            cur.execute("SELECT article FROM gene_articles WHERE gene_symbol = %s", (gene_symbol,))
            row = cur.fetchone()
            return row[0] if row else None

    def _worker_loop(self):
        while True:
            try:
                gene_symbol = self._queue.get(timeout=1)
            except Empty:
                continue

            try:
                print(f"[QUEUE] Processing gene: {gene_symbol}")
                self._agentic_pipeline(gene_symbol)
            except Exception as e:
                print(f"[ERROR] Failed processing {gene_symbol}: {e}")
            finally:
                self._queue.task_done()

    def _agentic_pipeline(self, gene_symbol: str) -> str:
        start = time.perf_counter()
        key = int(hashlib.sha256(gene_symbol.encode()).hexdigest(), 16) % (2**31)

        with psycopg2.connect(
                host=os.environ["PG_HOST"],
                port=os.environ.get("PG_PORT", 5432),
                dbname=os.environ["PG_DB"],
                user=os.environ["PG_USER"],
                password=os.environ["PG_PASSWORD"]
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_try_advisory_lock(%s)", (key,))
                locked = cur.fetchone()[0]

                if not locked:
                    print(f"[LOCK] Another process is already generating article for {gene_symbol}")
                    return f"Article generation for {gene_symbol} is already in progress."

                try:
                    funcs = [
                        uniprot.run_query,
                        kegg.run_query,
                        opengenes.run_query,
                        gnomad.run_query,
                        ncbi_mcp_server.run_query
                    ]
                    results = [None] * len(funcs)

                    with ThreadPoolExecutor(max_workers=len(funcs)) as ex:
                        futures = {ex.submit(f, gene_symbol): i for i, f in enumerate(funcs)}
                        for fut in as_completed(futures):
                            i = futures[fut]
                            try:
                                results[i] = fut.result()
                            except TimeoutError:
                                results[i] = "Agent timed out"
                            except Exception as e:
                                results[i] = f"Agent failed: {e}"

                    uniprot_output, kegg_output, opengenes_output, gnomad_output, ncbi_output = results

                    try:
                        article = agg.run_query(
                            uniprot_output,
                            kegg_output,
                            opengenes_output,
                            gnomad_output,
                            ncbi_output
                        )
                    except Exception as e:
                        article = f"Article creation failed: {e}"

                    with conn.cursor() as cur2:
                        cur2.execute("""
                            INSERT INTO gene_articles (gene_symbol, article)
                            VALUES (%s, %s)
                            ON CONFLICT (gene_symbol) DO UPDATE
                            SET article = EXCLUDED.article
                        """, (gene_symbol, article))
                        conn.commit()

                finally:
                    cur.execute("SELECT pg_advisory_unlock(%s)", (key,))

        elapsed = time.perf_counter() - start
        print(f"[DONE] Generated article for {gene_symbol} in {elapsed:.2f}s")
        return article

    def search(self, gene_symbol: str) -> GeneResponse:
        gene_symbol = gene_symbol.strip().upper()

        with self._cache_lock:
            article = self._load_from_db(gene_symbol)
            if article:
                try:
                    u = self.uniprot.fetch(gene_symbol)
                except Exception as e:
                    print(f"UniProt fetch failed: {e}")
                    u = {}

                try:
                    n = self.ncbi.fetch(gene_symbol)
                except Exception as e:
                    print(f"NCBI fetch failed: {e}")
                    n = {}

                print(f"[DB HIT] {gene_symbol}")
                return GeneResponse(
                    gene=gene_symbol,
                    article=article,
                    status="ready",
                    function=u.get("function"),
                    synonyms=u.get("synonyms") or [],
                    longevity_association=n.get("longevity_association"),
                    modification_effects=u.get("modification_effects"),
                    dna_sequence=n.get("dna_sequence"),
                    interval_in_dna_sequence=n.get("interval_in_dna_sequence"),
                    protein_sequence=u.get("protein_sequence"),
                    externalLink=n.get("external_link") or u.get("external_link"),
                )

            print(f"[QUEUE ADD] Added {gene_symbol} to processing queue")
            self._queue.put(gene_symbol)

            return GeneResponse(
                gene=gene_symbol,
                article=(
                    "Your request has been received and is queued for processing. Please check back later."
                ),
                status="processing",
                queue_size = self.get_queue_size()
            )

    def get_queue_size(self) -> int:
        return self._queue.qsize()
