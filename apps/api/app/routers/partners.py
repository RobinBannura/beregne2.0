from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from ..models.partner import Partner, PartnerCreate, PartnerResponse, PartnerConfig
from ..database import get_db

router = APIRouter(prefix="/api/partners", tags=["partners"])

@router.post("/", response_model=PartnerResponse)
async def create_partner(partner: PartnerCreate, db: Session = Depends(get_db)):
    """Opprett ny partner"""
    # Sjekk om partner_id allerede eksisterer
    existing = db.query(Partner).filter(Partner.partner_id == partner.partner_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Partner ID already exists")
    
    db_partner = Partner(**partner.dict())
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    return db_partner

@router.get("/", response_model=List[PartnerResponse])
async def list_partners(db: Session = Depends(get_db)):
    """List alle partnere"""
    return db.query(Partner).filter(Partner.is_active == True).all()

@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(partner_id: str, db: Session = Depends(get_db)):
    """Hent partner detaljer"""
    partner = db.query(Partner).filter(
        Partner.partner_id == partner_id, 
        Partner.is_active == True
    ).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner

@router.get("/{partner_id}/config", response_model=PartnerConfig)
async def get_partner_config(partner_id: str, db: Session = Depends(get_db)):
    """Hent partner konfigurasjon for widget"""
    partner = db.query(Partner).filter(
        Partner.partner_id == partner_id, 
        Partner.is_active == True
    ).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    return PartnerConfig(
        partner_id=partner.partner_id,
        brand_name=partner.brand_name,
        brand_color=partner.brand_color,
        logo_url=partner.logo_url,
        agent_display_name=partner.agent_display_name,
        welcome_message=partner.welcome_message,
        widget_position=partner.widget_position,
        widget_theme=partner.widget_theme,
        show_branding=partner.show_branding,
        enabled_agents=partner.enabled_agents or ["renovation"]
    )

@router.put("/{partner_id}", response_model=PartnerResponse)
async def update_partner(partner_id: str, partner: PartnerCreate, db: Session = Depends(get_db)):
    """Oppdater partner"""
    db_partner = db.query(Partner).filter(Partner.partner_id == partner_id).first()
    if not db_partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    for field, value in partner.dict().items():
        setattr(db_partner, field, value)
    
    db.commit()
    db.refresh(db_partner)
    return db_partner

@router.delete("/{partner_id}")
async def delete_partner(partner_id: str, db: Session = Depends(get_db)):
    """Deaktiver partner"""
    partner = db.query(Partner).filter(Partner.partner_id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    partner.is_active = False
    db.commit()
    return {"message": "Partner deactivated successfully"}