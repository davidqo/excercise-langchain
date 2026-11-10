import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import uvicorn

app = FastAPI(title="Pure LangChain Read-Only Service")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

cfg = load_config()

embedding_cache_dir = os.path.abspath(
    cfg["embeddings"].get("cache_dir", "./.cache/huggingface")
)
os.makedirs(embedding_cache_dir, exist_ok=True)

embeddings = HuggingFaceEmbeddings(
    model_name=cfg["embeddings"]["model_name"],
    cache_folder=embedding_cache_dir,
)

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

if __name__ == "__main__":
    server_cfg = cfg["server"]
    uvicorn.run(app, host=server_cfg["host"], port=int(server_cfg["port"]))
