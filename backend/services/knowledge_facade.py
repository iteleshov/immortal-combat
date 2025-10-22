from backend.services.aggregation import agg
from backend.services.mcp_uniprot_source import uniprot
from backend.services.kegg_source import kegg
from backend.services.open_genes_source import opengenes
from backend.services.uniprot_source import UniProtSource
from backend.services.ncbi_source import NcbiSource
from backend.models.gene_response import GeneResponse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class KnowledgeBaseFacade:
    def __init__(self):
        self.uniprot = UniProtSource()
        self.ncbi = NcbiSource()

    def search(self, gene_symbol: str) -> GeneResponse:
        def agentic_pipeline(gene_or_protein):
            """
            Executes UniProt, KEGG, and OpenGenes queries in parallel for a given gene or protein.
                Handles exceptions so one failure doesn't stop the pipeline.
            """
            start = time.perf_counter()
            funcs = [uniprot.run_query, kegg.run_query, opengenes.run_query]

            with ThreadPoolExecutor(max_workers=3) as ex:
                futures = {ex.submit(f, gene_or_protein): i for i, f in enumerate(funcs)}
                for fut in as_completed(futures):
                    i = futures[fut]
                    try:
                        results[i] = fut.result()
                    except Exception:
                        results[i] = 'Agent failed. No data retrieved'
                
            uniprot_output, kegg_output, opengenes_output = results
            try:
                article = agg.run_query(uniprot_output, kegg_output, opengenes_output)
            except Exception:
                article = 'Article creation failed. Try again'
            article = agg.run_query(r1, r2, r3)
            elapsed = time.perf_counter() - start
            print(f"Completed in: {elapsed:.2f} seconds ({elapsed/60:.1f} min)")
            return article

        gene_symbol = gene_symbol.strip()
        u = self.uniprot.fetch(gene_symbol)
        n = self.ncbi.fetch(gene_symbol)
        article = agentic_pipeline(gene_symbol)
        print("result article")
        print(article)

        resp = GeneResponse(
            gene=gene_symbol.upper(),
            function=u.get('function'),
            synonyms=u.get('synonyms') or [],
            longevity_association=n.get('longevity_association'),
            modification_effects=u.get('modification_effects'),
            dna_sequence=n.get('dna_sequence'),
            interval_in_dna_sequence=n.get('interval_in_dna_sequence'),
            protein_sequence=u.get('protein_sequence'),
            # interval_in_protein_sequence=mcp_uniprot.get('interval_in_protein_sequence'),
            # interval_in_sequence=mcp_uniprot.get('interval_in_sequence'),
            # contribution_of_evolution=mcp_uniprot.get('contribution_of_evolution'),
            article=n.get('article') or u.get('article')
        )
        return resp
