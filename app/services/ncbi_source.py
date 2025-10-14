from app.services.http_client import HttpClient
from app.models.gene_info import GeneInfo, MutationInfo

class NcbiSource:
    ESEARCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    ESUMMARY = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
    EFETCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'

    def __init__(self):
        self.client = HttpClient()

    def fetch(self, gene_symbol: str) -> GeneInfo:
        params = {'db': 'gene', 'term': f"{gene_symbol}[Gene Name] AND Homo sapiens[Organism]", 'retmode': 'json'}
        res = self.client.get_json(self.ESEARCH, params=params)
        seq = None
        functions = []
        mutations = []
        try:
            ids = res.get('esearchresult', {}).get('idlist', [])
            if ids:
                gene_id = ids[0]
                sum_params = {'db': 'gene', 'id': gene_id, 'retmode': 'json'}
                summary = self.client.get_json(self.ESUMMARY, params=sum_params)
                doc = summary.get('result', {}).get(str(gene_id), {})
                desc = doc.get('summary') or doc.get('description')
                if desc:
                    functions.append(desc)
                mutations.append(MutationInfo(name=f"NCBI_geneID:{gene_id}", position=None, effect=None, reference=None))
        except Exception:
            pass
        return GeneInfo(source='NCBI', gene_symbol=gene_symbol, sequence=seq, functions=functions, mutations=mutations)
