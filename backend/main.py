from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services.knowledge_facade import KnowledgeBaseFacade
from backend.models.gene_response import GeneResponse

app = FastAPI(title="Longevity Gene Knowledge API (UniProt + NCBI)")

origins = [
    "https://www.gene-lens.site",
    "https://gene-lens.site",
]

# ✅ Подключаем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

facade = KnowledgeBaseFacade()

@app.get('/search', response_model=GeneResponse)
def search_gene(gene_name: str):
    try:
        return facade.search(gene_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
