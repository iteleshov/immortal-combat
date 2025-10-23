from backend.services.aggregation import agg
from backend.services.mcp_uniprot_source import uniprot
from backend.services.kegg_source import kegg
from backend.services.open_genes_source import opengenes
from backend.services.uniprot_source import UniProtSource
from backend.services.ncbi_source import NcbiSource
from backend.services.gnomad_source import gnomad
from backend.services.ncbi_mcp_source import ncbi_mcp
from backend.models.gene_response import GeneResponse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class KnowledgeBaseFacade:
    def __init__(self):
        self.uniprot = UniProtSource()
        self.ncbi = NcbiSource()
        self._cache = {}              # gene_symbol -> article
        self._cache_lock = threading.Lock()

    def _agentic_pipeline(self, gene_symbol: str) -> str:
        """Run UniProt, KEGG, gnomAD and OpenGenes in parallel and aggregate results."""
        start = time.perf_counter()
        funcs = [uniprot.run_query, kegg.run_query, opengenes.run_query, gnomad.run_query, self.ncbi.fetch]
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

        elapsed = time.perf_counter() - start
        print(f"Generated article for {gene_symbol} in {elapsed:.2f}s")
        return article

    def search(self, gene_symbol: str) -> GeneResponse:
        gene_symbol = gene_symbol.strip().upper()

        # --- CACHE CHECK ---
        with self._cache_lock:
            if gene_symbol in self._cache:
                print(f"[CACHE HIT] {gene_symbol}")
                article = self._cache[gene_symbol]
            else:
                print(f"[CACHE MISS] {gene_symbol}")
                article = self._agentic_pipeline(gene_symbol)
                self._cache[gene_symbol] = article

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
