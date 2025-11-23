from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.reasoning import HybridReasoner
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

app = FastAPI(title="MediGraph Triage", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "service": "MediGraph Triage API", "docs": "/docs"}

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
        # Optionally re-raise or handle more gracefully if startup must fail
        # raise HTTPException(status_code=500, detail=f"Failed to initialize reasoner: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global reasoner
    if reasoner:
        reasoner.close()

class TriageRequest(BaseModel):
    symptoms: str
    history: str = ""
    session_id: Optional[str] = None
    user_id: Optional[str] = None

# TriageResponse model is no longer needed for streaming endpoint

@app.post("/triage")
async def triage(request: TriageRequest):
    """
    Triage endpoint that streams the assessment.
    """
    if not reasoner:
        raise HTTPException(status_code=503, detail="Reasoner not initialized")
    
    try:
        return StreamingResponse(
            reasoner.triage_stream(
                request.symptoms, 
                request.history,
                session_id=request.session_id,
                user_id=request.user_id
            ),
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
