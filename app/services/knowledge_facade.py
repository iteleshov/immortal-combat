from app.services.uniprot_source import UniProtSource
from app.services.ncbi_source import NcbiSource

class KnowledgeBaseFacade:
    def __init__(self):
        self.sources = [UniProtSource(), NcbiSource()]

    def search(self, gene_symbol: str) -> dict:
        gene_symbol = gene_symbol.strip()
        results = []
        for s in self.sources:
            try:
                results.append(s.fetch(gene_symbol))
            except Exception as e:
                print(f"Warning: source {s.__class__.__name__} failed: {e}")
        aggregated = self.aggregate(results, gene_symbol)
        return aggregated

    def aggregate(self, results, gene_symbol):
        seq = None
        functions = []
        mutations = []
        seen = set()
        for r in results:
            if not seq and getattr(r, 'sequence', None):
                seq = r.sequence
            if getattr(r, 'functions', None):
                for f in r.functions:
                    if f not in functions:
                        functions.append(f)
            if getattr(r, 'mutations', None):
                for m in r.mutations:
                    key = (m.name, m.position)
                    if key not in seen:
                        seen.add(key)
                        mutations.append({'name': m.name, 'position': m.position, 'effect': m.effect, 'reference': m.reference})
        payload = {
            'gene_symbol': gene_symbol,
            'sequence': seq,
            'functions': functions,
            'mutations': mutations,
            'sources_count': len(results)
        }
        return payload
