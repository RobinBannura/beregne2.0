from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.pricing import ServiceType, PricingData, MarketRate, Contractor
from ..database import get_db

class PricingService:
    """Service for håndtering av markedspriser og kostnadsestimater"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_service_price(self, service_name: str, area: float = None, region: str = "Oslo") -> Dict:
        """Henter markedspris for en tjeneste"""
        
        # Finn service type
        service = self.db.query(ServiceType).filter(
            ServiceType.name == service_name
        ).first()
        
        if not service:
            return {"error": f"Service '{service_name}' not found"}
        
        # Hent markedsrate
        market_rate = self.db.query(MarketRate).filter(
            MarketRate.service_type_id == service.id,
            MarketRate.region == region
        ).first()
        
        if not market_rate:
            # Fallback: beregn fra tilgjengelige data
            pricing_data = self.db.query(PricingData).filter(
                PricingData.service_type_id == service.id,
                PricingData.region == region
            ).all()
            
            if not pricing_data:
                return {"error": f"No pricing data for '{service_name}' in {region}"}
            
            # Beregn gjennomsnittsrater
            avg_min = sum(p.min_price for p in pricing_data) / len(pricing_data)
            avg_max = sum(p.max_price for p in pricing_data) / len(pricing_data)
            market_rate = {
                "market_min": avg_min,
                "market_max": avg_max,
                "market_avg": (avg_min + avg_max) / 2,
                "sample_size": len(pricing_data)
            }
        else:
            market_rate = {
                "market_min": market_rate.market_min,
                "market_max": market_rate.market_max,
                "market_avg": market_rate.market_avg,
                "recommended_price": market_rate.recommended_price,
                "sample_size": market_rate.sample_size,
                "confidence": market_rate.confidence_score
            }
        
        # Beregn totalkostnad hvis area er oppgitt
        if area and market_rate:
            total_min = market_rate["market_min"] * area
            total_max = market_rate["market_max"] * area
            total_avg = market_rate["market_avg"] * area
            
            return {
                "service": service_name,
                "unit": service.unit,
                "area": area,
                "unit_price": market_rate,
                "total_cost": {
                    "min": total_min,
                    "max": total_max,
                    "avg": total_avg,
                    "recommended": market_rate.get("recommended_price", total_avg) * area if area else None
                },
                "region": region
            }
        
        return {
            "service": service_name,
            "unit": service.unit,
            "unit_price": market_rate,
            "region": region
        }
    
    def add_pricing_data(self, service_name: str, contractor_name: str = None, 
                        min_price: float = None, max_price: float = None,
                        region: str = "Oslo", source: str = "manual") -> bool:
        """Legger til ny prisdata"""
        
        # Finn eller opprett service type
        service = self.db.query(ServiceType).filter(
            ServiceType.name == service_name
        ).first()
        
        if not service:
            return False
        
        # Finn contractor hvis oppgitt
        contractor = None
        if contractor_name:
            contractor = self.db.query(Contractor).filter(
                Contractor.name == contractor_name
            ).first()
        
        # Opprett pricing data
        pricing = PricingData(
            service_type_id=service.id,
            contractor_id=contractor.id if contractor else None,
            min_price=min_price,
            max_price=max_price,
            avg_price=(min_price + max_price) / 2 if min_price and max_price else None,
            region=region,
            source=source,
            confidence=0.8  # Default confidence for manual entries
        )
        
        self.db.add(pricing)
        self.db.commit()
        return True
    
    def update_market_rates(self, region: str = "Oslo"):
        """Oppdaterer beregnede markedsrater basert på alle tilgjengelige data"""
        
        services = self.db.query(ServiceType).all()
        
        for service in services:
            # Hent all pricing data for denne tjenesten
            pricing_data = self.db.query(PricingData).filter(
                PricingData.service_type_id == service.id,
                PricingData.region == region
            ).all()
            
            if not pricing_data:
                continue
            
            # Beregn markedsrater
            min_prices = [p.min_price for p in pricing_data if p.min_price]
            max_prices = [p.max_price for p in pricing_data if p.max_price]
            
            if not min_prices or not max_prices:
                continue
            
            market_min = min(min_prices)
            market_max = max(max_prices)
            market_avg = (sum(min_prices) + sum(max_prices)) / (len(min_prices) + len(max_prices))
            
            # Beregn anbefalt pris (litt over gjennomsnittet)
            recommended = market_avg * 1.1
            
            # Sjekk om market rate allerede eksisterer
            existing = self.db.query(MarketRate).filter(
                MarketRate.service_type_id == service.id,
                MarketRate.region == region
            ).first()
            
            if existing:
                existing.market_min = market_min
                existing.market_max = market_max
                existing.market_avg = market_avg
                existing.recommended_price = recommended
                existing.sample_size = len(pricing_data)
                existing.confidence_score = min(0.9, len(pricing_data) / 10)  # Mer data = høyere confidence
            else:
                market_rate = MarketRate(
                    service_type_id=service.id,
                    market_min=market_min,
                    market_max=market_max,
                    market_avg=market_avg,
                    recommended_price=recommended,
                    sample_size=len(pricing_data),
                    confidence_score=min(0.9, len(pricing_data) / 10),
                    region=region
                )
                self.db.add(market_rate)
        
        self.db.commit()
    
    def get_contractors_by_service(self, service_name: str, region: str = "Oslo") -> List[Dict]:
        """Henter kontraktører som tilbyr en spesifikk tjeneste"""
        
        service = self.db.query(ServiceType).filter(
            ServiceType.name == service_name
        ).first()
        
        if not service:
            return []
        
        contractors = self.db.query(Contractor).join(PricingData).filter(
            PricingData.service_type_id == service.id,
            Contractor.location.like(f"%{region}%")
        ).all()
        
        result = []
        for contractor in contractors:
            pricing = self.db.query(PricingData).filter(
                PricingData.service_type_id == service.id,
                PricingData.contractor_id == contractor.id
            ).first()
            
            result.append({
                "name": contractor.name,
                "company_type": contractor.company_type,
                "location": contractor.location,
                "website": contractor.website,
                "phone": contractor.phone,
                "price_range": f"{pricing.min_price}-{pricing.max_price} kr/{service.unit}" if pricing else "Kontakt for pris"
            })
        
        return result