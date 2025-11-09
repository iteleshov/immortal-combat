from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services.knowledge_facade import KnowledgeBaseFacade
from backend.models.gene_response import GeneResponse
from backend.models.rag_response import RagResponse

app = FastAPI(title="Longevity Gene Knowledge API (UniProt + NCBI)")

origins = [
    "https://www.gene-lens.site",
    "https://gene-lens.site",
    "http://localhost:3000"
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
    result = facade.search(gene_name)
    return result

@app.get('/rag_search', response_model=RagResponse)
def rag_search(question: str):
    result = facade.rag_search(question)
    return result
