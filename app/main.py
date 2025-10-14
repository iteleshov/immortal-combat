from fastapi import FastAPI, HTTPException
from app.services.knowledge_facade import KnowledgeBaseFacade

app = FastAPI(title="Longevity Gene Knowledge API (Aggregated)")
facade = KnowledgeBaseFacade()

@app.get("/search")
def search_gene(gene_name: str):
    """Return aggregated gene information from multiple sources (UniProt + NCBI)."""
    try:
        result = facade.search(gene_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
