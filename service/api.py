from fastapi import FastAPI
from pydantic import BaseModel
try:
    from service.main import app as workflow_app
except:
    from main import app as workflow_app

app = FastAPI(title="ML Data Generation & Search Service")

class GenerateRequest(BaseModel):
    topic: str
    num_rows: int = 10

class SearchRequest(BaseModel):
    topic: str
    query_text: str
    top_k: int = 5


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Datagen API"
    }

@app.post("/generate")
def generate_data(request: GenerateRequest):
    state = {
        "intent": "generate",
        "topic": request.topic,
        "num_rows": request.num_rows,
        "generated_data": [],
        "embeddings": []
    }
    result = workflow_app.invoke(state)
    return {"status": "success", "count": len(result['generated_data']) , "Generated data " : result['generated_data']}

@app.post("/search")
def search_embeddings(request: SearchRequest):
    state = {
        "intent": "search",
        "query_text": request.query_text,
        "topic": request.topic,
        "top_k": request.top_k,
        "query_results": []
    }
    result = workflow_app.invoke(state)
    return {"results": result['query_results']}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)