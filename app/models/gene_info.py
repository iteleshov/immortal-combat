from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class MutationInfo:
    name: str
    position: Optional[int] = None
    effect: Optional[str] = None
    reference: Optional[str] = None

@dataclass
class GeneInfo:
    source: str
    gene_symbol: str
    sequence: Optional[str] = None
    functions: Optional[List[str]] = None
    mutations: Optional[List[MutationInfo]] = None

    def to_dict(self):
        d = asdict(self)
        if d.get('mutations') is not None:
            d['mutations'] = [m for m in d['mutations']]
        return d
