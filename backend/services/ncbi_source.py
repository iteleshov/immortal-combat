from backend.services.http_client import HttpClient

class NcbiSource:
    ESEARCH = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    ESUMMARY = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'

    def __init__(self):
        self.client = HttpClient()

    def fetch(self, gene_symbol: str) -> dict:
        params = {'db': 'gene', 'term': f"{gene_symbol}[Gene Name] AND Homo sapiens[Organism]", 'retmode': 'json'}
        res = self.client.get(self.ESEARCH, params=params)
        out = {'longevity_association': None, 'dna_sequence': None, 'interval_in_dna_sequence': None, 'article': None}
        try:
            ids = res.get('esearchresult', {}).get('idlist', [])
            if not ids:
                return out
            gene_id = ids[0]
            sum_params = {'db': 'gene', 'id': gene_id, 'retmode': 'json'}
            summary = self.client.get(self.ESUMMARY, params=sum_params)
            doc = summary.get('result', {}).get(str(gene_id), {})
            summary_text = doc.get('summary') or doc.get('description')
            if summary_text:
                out['longevity_association'] = summary_text
            out['article'] = f'https://www.ncbi.nlm.nih.gov/gene/{gene_id}'
            ginfo = doc.get('genomicinfo', [])
            if ginfo:
                g0 = ginfo[0]
                chr_from = g0.get('chrstart')
                chr_to = g0.get('chrstop')
                if chr_from is not None and chr_to is not None:
                    try:
                        out['interval_in_dna_sequence'] = (int(chr_from), int(chr_to))
                    except:
                        out['interval_in_dna_sequence'] = None
        except Exception:
            pass
        return out
