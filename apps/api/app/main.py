from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import uvicorn
from sqlalchemy.orm import Session

from .orchestrator import AgentOrchestrator
from .routers import partners, widget, dashboard, leads, analytics
from .database import create_tables, get_db, SessionLocal
from .models.partner import Partner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Beregne 2.0 API",
    description="AI-Powered Calculator Platform for Norway",
    version="2.0.9",  # FORCE RAILWAY DEPLOYMENT - EMERGENCY VERSION BUMP
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://beregne2-0-marketing.vercel.app",  # Vercel deployment
        "https://beregne.no",  # Custom domain (når du setter det opp)
        "https://www.beregne.no",
        "https://beregne20-production.up.railway.app"  # Railway backend
    ],
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
app.include_router(leads.router)
app.include_router(analytics.router)

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
    
    # Create database tables (including new conversation tables)
    try:
        create_tables()
        
        # Ensure all model tables exist
        from .models.conversation import ConversationSession, ConversationMessage, ConversationPattern
        from .models.conversation import Base as ConversationBase
        from .models.pricing import ServiceType, PricingData, Contractor
        from .models.pricing import Base as PricingBase
        
        ConversationBase.metadata.create_all(bind=SessionLocal().bind)
        PricingBase.metadata.create_all(bind=SessionLocal().bind)
        
        # Initialize pricing data if missing
        try:
            from .models.pricing import ServiceType, PricingData
            from .services.pricing_service import PricingService
            
            db = SessionLocal()
            pricing_service = PricingService(db)
            
            # Check if bathroom pricing exists
            test_service = db.query(ServiceType).filter(ServiceType.name == "bad_totalrenovering_8m2").first()
            if not test_service:
                logger.info("💰 Initializing bathroom pricing data...")
                
                # Create bathroom service types
                bathroom_services = [
                    {"name": "bad_totalrenovering_4m2", "description": "Totalrenovering 4m² bad", "unit": "stk", "category": "bad_komplett"},
                    {"name": "bad_totalrenovering_8m2", "description": "Totalrenovering 8m² bad", "unit": "stk", "category": "bad_komplett"},
                    {"name": "bad_totalrenovering_12m2", "description": "Totalrenovering 12m² bad", "unit": "stk", "category": "bad_komplett"}
                ]
                
                for service_data in bathroom_services:
                    service = ServiceType(**service_data)
                    db.add(service)
                
                # Commit service types first so they have IDs for foreign key relationships
                db.commit()
                
                # Create bathroom pricing data with correct foreign key relationships
                bathroom_prices = [
                    {"service_name": "bad_totalrenovering_4m2", "region": "Oslo", "min_price": 280000, "max_price": 360000},
                    {"service_name": "bad_totalrenovering_8m2", "region": "Oslo", "min_price": 340000, "max_price": 440000},
                    {"service_name": "bad_totalrenovering_12m2", "region": "Oslo", "min_price": 400000, "max_price": 520000}
                ]
                
                for price_data in bathroom_prices:
                    # Find the service_type by name
                    service_type = db.query(ServiceType).filter(ServiceType.name == price_data["service_name"]).first()
                    if service_type:
                        price = PricingData(
                            service_type_id=service_type.id,
                            region=price_data["region"],
                            min_price=price_data["min_price"],
                            max_price=price_data["max_price"],
                            avg_price=(price_data["min_price"] + price_data["max_price"]) / 2,
                            source="startup_initialization",
                            confidence=0.9
                        )
                        db.add(price)
                
                db.commit()
                db.close()
                logger.info("✅ Bathroom pricing data initialized")
            else:
                logger.info("✅ Bathroom pricing data already exists")
                db.close()
                
        except Exception as e:
            logger.error(f"❌ Error initializing pricing data: {e}")
        
        logger.info("📊 Database initialized with all tables")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Continue anyway - app might still work without conversation learning
    
    # Initialize default partners
    try:
        from .models.partner import Partner
        db = SessionLocal()
        
        # Check if househacker exists
        existing = db.query(Partner).filter(Partner.partner_id == "househacker").first()
        if not existing:
            logger.info("🏗️ Creating househacker partner...")
            househacker = Partner(
                partner_id="househacker",
                name="househacker AS",
                domain="househacker.no",
                brand_name="househacker",
                brand_color="#1f2937",
                logo_url="https://househacker.no/logo.png",
                enabled_agents=["conversational_renovation"],
                agent_display_name="househacker-assistent",
                welcome_message="Hei! Jeg er din househacker-assistent. Har du spørsmål innen oppussing? Eller ønsker du å registrere et prosjekt slik at vi kan hjelpe deg i gang?",
                widget_position="bottom-right",
                widget_theme="light",
                show_branding=True
            )
            db.add(househacker)
            db.commit()
            logger.info("✅ Created househacker partner")
        else:
            logger.info("✅ househacker partner already exists")
        
        db.close()
    except Exception as e:
        logger.error(f"❌ Error creating partner: {e}")
    
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

@app.post("/api/admin/fix-agent-config")
async def fix_agent_config(db: Session = Depends(get_db)):
    """Fix househacker agent configuration to use conversational_renovation"""
    try:
        partner = db.query(Partner).filter(Partner.partner_id == "househacker").first()
        if partner:
            old_agents = partner.enabled_agents
            partner.enabled_agents = ["conversational_renovation"]
            db.commit()
            return {
                "status": "success",
                "message": "Updated househacker agent configuration",
                "old_agents": old_agents,
                "new_agents": partner.enabled_agents
            }
        else:
            return {"status": "error", "message": "househacker partner not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/admin/initialize-bathroom-pricing")
async def initialize_bathroom_pricing(db: Session = Depends(get_db)):
    """Manually initialize bathroom pricing data"""
    try:
        from .models.pricing import ServiceType, PricingData
        
        # Create bathroom service types
        bathroom_services = [
            {"name": "bad_totalrenovering_4m2", "description": "Totalrenovering 4m² bad", "unit": "stk", "category": "bad_komplett"},
            {"name": "bad_totalrenovering_8m2", "description": "Totalrenovering 8m² bad", "unit": "stk", "category": "bad_komplett"},
            {"name": "bad_totalrenovering_12m2", "description": "Totalrenovering 12m² bad", "unit": "stk", "category": "bad_komplett"}
        ]
        
        services_added = 0
        for service_data in bathroom_services:
            existing = db.query(ServiceType).filter(ServiceType.name == service_data["name"]).first()
            if not existing:
                service = ServiceType(**service_data)
                db.add(service)
                services_added += 1
        
        db.commit()
        
        # Create bathroom pricing data
        bathroom_prices = [
            {"service_name": "bad_totalrenovering_4m2", "region": "Oslo", "min_price": 280000, "max_price": 360000},
            {"service_name": "bad_totalrenovering_8m2", "region": "Oslo", "min_price": 340000, "max_price": 440000},
            {"service_name": "bad_totalrenovering_12m2", "region": "Oslo", "min_price": 400000, "max_price": 520000}
        ]
        
        prices_added = 0
        for price_data in bathroom_prices:
            service_type = db.query(ServiceType).filter(ServiceType.name == price_data["service_name"]).first()
            if service_type:
                existing_price = db.query(PricingData).filter(
                    PricingData.service_type_id == service_type.id,
                    PricingData.source == "admin_initialization"
                ).first()
                
                if not existing_price:
                    price = PricingData(
                        service_type_id=service_type.id,
                        region=price_data["region"],
                        min_price=price_data["min_price"],
                        max_price=price_data["max_price"],
                        avg_price=(price_data["min_price"] + price_data["max_price"]) / 2,
                        source="admin_initialization",
                        confidence=0.9
                    )
                    db.add(price)
                    prices_added += 1
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Bathroom pricing initialized",
            "services_added": services_added,
            "prices_added": prices_added
        }
        
    except Exception as e:
        import traceback
        return {
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/api/debug/database")
async def debug_database(db: Session = Depends(get_db)):
    """Debug database and pricing service functionality"""
    try:
        from .services.pricing_service import PricingService
        from .services.ai_query_analyzer import AIQueryAnalyzer
        import os
        
        # Check what tables exist first
        from sqlalchemy import text
        tables_result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        existing_tables = [row[0] for row in tables_result.fetchall()]
        
        # Only test pricing service if tables exist
        if "service_types" in existing_tables and "pricing_data" in existing_tables:
            pricing_service = PricingService(db)
            try:
                bathroom_price = pricing_service.get_service_price("bad_totalrenovering_8m2")
            except Exception as e:
                bathroom_price = {"error": str(e)}
        else:
            bathroom_price = {"error": "Pricing tables missing"}
        
        ai_analyzer = AIQueryAnalyzer(agent_name="renovation")
        
        # Test AI analyzer
        test_analysis = await ai_analyzer.analyze_query("standard kvalitet og 5 kvm")
        
        return {
            "status": "success",
            "database_connected": True,
            "existing_tables": existing_tables,
            "pricing_service": {
                "bathroom_8m2_price": bathroom_price,
                "working": "error" not in bathroom_price
            },
            "ai_analyzer": {
                "api_key_available": ai_analyzer.api_key is not None,
                "test_analysis": {
                    "project_type": test_analysis.get("project_type"),
                    "area": test_analysis.get("area"),
                    "type": test_analysis.get("type")
                }
            },
            "environment": {
                "database_url": os.getenv("DATABASE_URL", "Not set")[:20] + "...",
                "openai_key_available": bool(os.getenv("OPENAI_API_KEY_RENOVATION"))
            }
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)