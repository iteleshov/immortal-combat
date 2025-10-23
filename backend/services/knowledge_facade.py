from backend.services.aggregation import agg
from backend.services.mcp_uniprot_source import uniprot
from backend.services.kegg_source import kegg
from backend.services.open_genes_source import opengenes
from backend.services.uniprot_source import UniProtSource
from backend.services.ncbi_source import NcbiSource
from backend.services.gnomad_source import gnomad
from backend.services.ncbi_mcp_source import ncbi_mcp
from backend.models.gene_response import GeneResponse
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import psycopg2
from psycopg2.extras import execute_values

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
        self._cache = {}
        self._cache_lock = threading.Lock()

        self._ensure_table()

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
            cur.execute(
            "SELECT article FROM gene_articles WHERE gene_symbol = %s",
            (gene_symbol,))
        row = cur.fetchone()
        return row[0] if row else None

    def _agentic_pipeline(self, gene_symbol: str) -> str:
        start = time.perf_counter()
        funcs = [uniprot.run_query, kegg.run_query, opengenes.run_query, gnomad.run_query, ncbi_mcp.final_process]
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
                except SystemExit:
                    results[i] = None

        uniprot_output, kegg_output, opengenes_output, gnomad_output, ncbi_output = results
        try:
            article = agg.run_query(uniprot_output, kegg_output, opengenes_output, gnomad_output, ncbi_output)
        except Exception as e:
            article = f"Article creation failed: {e}"

        # сохраняем в PostgreSQL
        self._save_to_db(gene_symbol, article)

        elapsed = time.perf_counter() - start
        print(f"Generated article for {gene_symbol} in {elapsed:.2f}s")
        return article

    def search(self, gene_symbol: str) -> GeneResponse:
        gene_symbol = gene_symbol.strip().upper()

        with self._cache_lock:
            # --- DB CHECK ---
            article = self._load_from_db(gene_symbol)
            if article:
                print(f"[DB HIT] {gene_symbol}")
            else:
                print(f"[CACHE & DB MISS] {gene_symbol}")
                article = self._agentic_pipeline(gene_symbol)

        # --- FETCH BASE DATA ---
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

        resp = GeneResponse(
            gene=gene_symbol,
            function=u.get("function"),
            synonyms=u.get("synonyms") or [],
            longevity_association=n.get("longevity_association"),
            modification_effects=u.get("modification_effects"),
            dna_sequence=n.get("dna_sequence"),
            interval_in_dna_sequence=n.get("interval_in_dna_sequence"),
            protein_sequence=u.get("protein_sequence"),
            article=article,
            externalLink=n.get('article') or u.get('article')
        )
        return resp
