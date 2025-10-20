from fastapi import FastAPI, HTTPException
from backend.services.knowledge_facade import KnowledgeBaseFacade
from backend.models.gene_response import GeneResponse

app = FastAPI(title="Longevity Gene Knowledge API (UniProt + NCBI)")
facade = KnowledgeBaseFacade()

@app.get('/search', response_model=GeneResponse)
def search_gene(gene_name: str):
    try:
        return facade.search(gene_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
