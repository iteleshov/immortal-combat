from app.services.uniprot_source import UniProtSource
from app.services.ncbi_source import NcbiSource
from app.models.gene_response import GeneResponse

class KnowledgeBaseFacade:
    def __init__(self):
        self.uniprot = UniProtSource()
        self.ncbi = NcbiSource()

    def search(self, gene_symbol: str) -> GeneResponse:
        gene_symbol = gene_symbol.strip()
        u = self.uniprot.fetch(gene_symbol)
        n = self.ncbi.fetch(gene_symbol)

        resp = GeneResponse(
            gene=gene_symbol.upper(),
            function=u.get('function'),
            synonyms=u.get('synonyms') or [],
            longevity_association=n.get('longevity_association'),
            modification_effects=u.get('modification_effects'),
            dna_sequence=n.get('dna_sequence'),
            interval_in_dna_sequence=n.get('interval_in_dna_sequence'),
            protein_sequence=u.get('protein_sequence'),
            interval_in_protein_sequence=None,
            interval_in_sequence=None,
            contribution_of_evolution=u.get('contribution_of_evolution'),
            article=n.get('article') or u.get('article')
        )
        return resp
