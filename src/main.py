from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.reasoning import HybridReasoner
import uvicorn
import os

app = FastAPI(title="MediGraph Triage", version="1.0.0")

# Initialize Reasoner (Global state)
reasoner = None

@app.on_event("startup")
async def startup_event():
    global reasoner
    try:
        reasoner = HybridReasoner()
        print("HybridReasoner initialized.")
    except Exception as e:
        print(f"Failed to initialize HybridReasoner: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global reasoner
    if reasoner:
        reasoner.close()

class TriageRequest(BaseModel):
    symptoms: str
    history: str = ""

class TriageResponse(BaseModel):
    diagnosis: str
    triage_level: str
    reasoning: str
    latency_ms: float

@app.post("/triage")
async def triage_endpoint(request: TriageRequest):
    if not reasoner:
        raise HTTPException(status_code=503, detail="Reasoner not initialized")
    
    try:
        result = reasoner.triage(request.symptoms, request.history)
        # Parse the JSON string from Gemini
        import json
        
        # Clean up potential markdown code blocks
        text_result = result["result"]
        if text_result.startswith("```json"):
            text_result = text_result[7:]
        if text_result.endswith("```"):
            text_result = text_result[:-3]
            
        parsed_result = json.loads(text_result)
        
        return {
            **parsed_result,
            "latency_ms": result["latency_ms"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
