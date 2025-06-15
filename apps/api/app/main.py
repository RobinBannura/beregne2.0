from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import uvicorn
from sqlalchemy.orm import Session

from .orchestrator import AgentOrchestrator
from .routers import partners, widget, dashboard
from .database import create_tables, get_db
from .models.partner import Partner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Beregne 2.0 API",
    description="AI-Powered Calculator Platform for Norway",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Include routers
app.include_router(partners.router)
app.include_router(widget.router)
app.include_router(dashboard.router)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    partner_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None
    agent_used: str
    routing: Optional[Dict[str, Any]] = None
    calculation_details: Optional[Dict[str, Any]] = None
    materials_list: Optional[list] = None
    estimated_cost: Optional[float] = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Beregne 2.0 API...")
    
    # Create database tables
    create_tables()
    logger.info("📊 Database initialized")
    
    logger.info(f"🤖 Loaded {orchestrator.get_agent_count()} agents")
    
    # List available agents
    agents = orchestrator.get_available_agents()
    for agent in agents:
        logger.info(f"  - {agent['name']} agent loaded")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Beregne 2.0 API",
        "version": "2.0.0",
        "status": "running",
        "agents": orchestrator.get_agent_count()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents": orchestrator.get_available_agents(),
        "agent_count": orchestrator.get_agent_count()
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint for processing user queries.
    Routes queries to appropriate AI agents.
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"Processing query: {request.message[:100]}...")
        
        # Get partner configuration if partner_id is provided
        partner_config = None
        if request.partner_id:
            partner = db.query(Partner).filter(
                Partner.partner_id == request.partner_id,
                Partner.is_active == True
            ).first()
            if partner:
                partner_config = {
                    "enabled_agents": partner.enabled_agents or ["renovation"],
                    "brand_name": partner.brand_name
                }
        
        # Route query to appropriate agent
        result = await orchestrator.route_query(
            query=request.message,
            context=request.context,
            partner_config=partner_config
        )
        
        # Create response
        response = ChatResponse(
            response=result.get("response", "Ingen respons fra agent"),
            session_id=request.session_id,
            agent_used=result.get("agent_used", "unknown"),
            routing=result.get("routing"),
            calculation_details=result.get("calculation_details"),
            materials_list=result.get("materials_list"),
            estimated_cost=result.get("estimated_cost")
        )
        
        logger.info(f"Response from {result.get('agent_used', 'unknown')} agent")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/agents")
async def get_agents():
    """Get information about available agents"""
    return {
        "agents": orchestrator.get_available_agents(),
        "total": orchestrator.get_agent_count()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)