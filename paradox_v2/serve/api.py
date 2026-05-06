"""
Paradox v2 — FastAPI Production Server
========================================
REST API for interacting with the Paradox AGI.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import os

from ..config import CONFIG
from ..llm.backbone import ParadoxBackbone
from ..llm.generator import ParadoxGenerator
from ..brain.regions import BrainRouter
from ..brain.emotions import EmotionEngine
from ..brain.memory import ConversationMemory
from ..retrieval.vector_store import ParadoxVectorStore
from ..retrieval.embedder import ParadoxEmbedder

app = FastAPI(title="Paradox AGI API", version="2.0.0")

# Lazy globals
backbone = None
generator = None
router = BrainRouter()
emotions = EmotionEngine()
memory = ConversationMemory()
vector_store = ParadoxVectorStore()
embedder = ParadoxEmbedder()

class QueryRequest(BaseModel):
    query: str
    region: Optional[str] = None # Auto-routed if None
    history_limit: int = 5

class QueryResponse(BaseModel):
    response: str
    region: str
    emotion_state: Dict[str, float]
    confidence: float

@app.on_event("startup")
async def startup_event():
    global backbone, generator
    print("[API] Initializing Paradox AGI...")
    backbone = ParadoxBackbone()
    
    # Check for fine-tuned adapter
    adapter_path = os.path.join(CONFIG.training.output_dir, "final_adapter")
    if os.path.exists(adapter_path):
        backbone.load_adapter(adapter_path)
        
    generator = ParadoxGenerator(backbone=backbone)
    vector_store.load()
    print("[API] Paradox AGI Ready.")

@app.post("/query", response_model=QueryResponse)
async def query_paradox(request: QueryRequest):
    try:
        # 1. Routing
        region, confidence = router.route_with_confidence(request.query)
        target_region = request.region or region
        
        # 2. Retrieval
        q_emb = embedder.encode_query(request.query)
        context = vector_store.search(q_emb, top_k=CONFIG.retrieval.top_k, region_filter=target_region)
        context_texts = [c[0]["text"] for c in context]
        
        # 3. Generation
        history = memory.get_recent_messages(n_turns=request.history_limit)
        gen_meta = generator.generate_with_metadata(
            query=request.query,
            context_chunks=context_texts,
            region=target_region,
            conversation_history=history,
            emotion_state=emotions.state
        )
        
        # 4. State Update
        emotions.stimulate_curiosity(len(request.query))
        emotions.apply_decay()
        memory.add_turn(request.query, gen_meta["response"], target_region, len(context_texts), emotions.state)
        
        return QueryResponse(
            response=gen_meta["response"],
            region=target_region,
            emotion_state=emotions.state,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_server(host="0.0.0.0", port=8000):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
