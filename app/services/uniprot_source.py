from app.services.http_client import HttpClient
from app.models.gene_info import GeneInfo, MutationInfo

class UniProtSource:
    BASE = "https://rest.uniprot.org/uniprotkb/search"

    def __init__(self):
        self.client = HttpClient()

    def fetch(self, gene_symbol: str) -> GeneInfo:
        params = {"query": f"gene:{gene_symbol} AND organism_id:9606", "format": "json", "size": 1}
        res = self.client.get_json(self.BASE, params=params)

        sequence = None
        functions = []
        mutations = []
        try:
            hits = res.get('results', [])
            if hits:
                entry = hits[0]
                accession = entry.get('primaryAccession') or entry.get('uniProtkbId')
                if accession:
                    entry_url = f"https://rest.uniprot.org/uniprotkb/{accession}.json"
                    full = self.client.get_json(entry_url)
                    seq_obj = full.get('sequence') or {}
                    sequence = seq_obj.get('value')
                    comments = full.get('comments') or []
                    for c in comments:
                        if c.get('commentType') == 'FUNCTION':
                            txt = ' '.join([t.get('value','') for t in c.get('texts', [])])
                            functions.append(txt)
                    for feat in full.get('features', []):
                        if feat.get('type') in ('VARIANT','MODIFICATION'):
                            name = feat.get('description') or feat.get('variation') or feat.get('type')
                            pos = None
                            loc = feat.get('location', {})
                            if loc:
                                begin = loc.get('start', {}).get('value') if isinstance(loc.get('start'), dict) else None
                                if begin:
                                    try:
                                        pos = int(begin)
                                    except:
                                        pos = None
                            mutations.append(MutationInfo(name=name, position=pos, effect=None, reference=None))
        except Exception:
            pass

        return GeneInfo(source='UniProt', gene_symbol=gene_symbol, sequence=sequence, functions=functions, mutations=mutations)
