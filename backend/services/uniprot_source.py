from backend.services.http_client import HttpClient

class UniProtSource:
    SEARCH_URL = 'https://rest.uniprot.org/uniprotkb/search'
    ENTRY_URL = 'https://rest.uniprot.org/uniprotkb/{}.json'

    def __init__(self):
        self.client = HttpClient()

    def fetch(self, gene_symbol: str) -> dict:
        params = {'query': f'gene:{gene_symbol} AND organism_id:9606', 'format': 'json', 'size': 1}
        res = self.client.get(self.SEARCH_URL, params=params)
        out = {'protein_sequence': None,
               'function': None,
               'synonyms': [],
               'modification_effects': None,
               'article': None,
               'contribution_of_evolution': None,
               'primaryAccession': None
        }
        hits = res.get('results', []) if isinstance(res, dict) else []
        if not hits:
            return out
        entry = hits[0]
        accession = entry.get('primaryAccession') or entry.get('uniProtkbId')
        out['primaryAccession'] = accession
        if not accession:
            return out
        full = self.client.get(self.ENTRY_URL.format(accession))
        seq_obj = full.get('sequence') or {}
        out['protein_sequence'] = seq_obj.get('value')
        comments = full.get('comments', [])
        fn_texts = []
        for c in comments:
            if c.get('commentType') == 'FUNCTION':
                texts = c.get('texts', [])
                fn_texts.append(' '.join([t.get('value','') for t in texts]))
            if c.get('commentType') == 'SEQUENCE CAUTION' and not out['modification_effects']:
                out['modification_effects'] = ' '.join([t.get('value','') for t in c.get('texts', [])])
        if fn_texts:
            out['function'] = '\n'.join(fn_texts)
        genes = full.get('genes', [])
        syns = []
        if genes:
            for g in genes:
                for s in g.get('synonyms', []):
                    v = s.get('value')
                    if v and v not in syns:
                        syns.append(v)
        out['synonyms'] = syns
        refs = full.get('references', [])
        doi = None
        for r in refs:
            pub = r.get('citation', {})
            doi = pub.get('doi') or doi
            if doi:
                break
        if doi:
            out['article'] = doi
        for c in comments:
            if c.get('commentType') and 'EVOLUTION' in c.get('commentType','').upper():
                out['contribution_of_evolution'] = ' '.join([t.get('value','') for t in c.get('texts', [])])
        return out
