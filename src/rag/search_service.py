import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

app = FastAPI(title="Pure LangChain Read-Only Service")

CONFIG_PATH = "./config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

cfg = load_config()

embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

vector_store = Chroma(
    collection_name=cfg["chroma"]["collection_name"],
    embedding_function=embeddings,
    persist_directory=cfg["chroma"]["persist_directory"]
)

class QueryRequest(BaseModel):
    text: str
    k: int = 3

@app.post("/search")
async def search_context(request: QueryRequest):
    try:
        docs = vector_store.similarity_search(request.text, k=request.k)
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))