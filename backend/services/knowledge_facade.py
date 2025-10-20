from backend.services.mcp_uniprot_source.uniprot import run_query
from backend.services.uniprot_source import UniProtSource
from backend.services.ncbi_source import NcbiSource
from backend.models.gene_response import GeneResponse

class KnowledgeBaseFacade:
    def __init__(self):
        self.uniprot = UniProtSource()
        self.ncbi = NcbiSource()

    def search(self, gene_symbol: str) -> GeneResponse:
        gene_symbol = gene_symbol.strip()
        u = self.uniprot.fetch(gene_symbol)
        n = self.ncbi.fetch(gene_symbol)
        mcp_uniprot = run_query(gene_symbol)
        print("result mcp_uniprot")
        print(mcp_uniprot)

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
