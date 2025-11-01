from pydantic import BaseModel
from typing import List, Optional, Tuple

class GeneResponse(BaseModel):
    gene: str
    primaryAccession: str
    status: str
    function: Optional[str] = None
    synonyms: List[str] = []
    longevity_association: Optional[str] = None
    modification_effects: Optional[str] = None
    dna_sequence: Optional[str] = None
    interval_in_dna_sequence: Optional[Tuple[int, int]] = None
    protein_sequence: Optional[str] = None
    interval_in_protein_sequence: Optional[Tuple[int, int]] = None
    interval_in_sequence: Optional[Tuple[int, int]] = None
    contribution_of_evolution: Optional[str] = None
    article: Optional[str] = None
    externalLink: Optional[str] = None
    queue_size: Optional[int] = 0
