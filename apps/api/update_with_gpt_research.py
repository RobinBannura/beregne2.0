#!/usr/bin/env python3
"""
Update pricing database with GPT research data from Oslo/Viken market
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_with_gpt_research():
    """Update with detailed GPT research from Oslo/Viken market"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🔬 Updating with GPT research data (Oslo/Viken 2022-2025)")
        print("=" * 60)
        
        # More detailed and accurate market data from GPT research
        research_data = [
            # Core services with accurate pricing
            {
                "service": "skjotesparkling_inkl_maling",
                "description": "Sparkling av skjøter (gips) inkl. 2 strøk maling",
                "unit": "m²",
                "category": "kombinert_skjøter",
                "min_price": 170,
                "max_price": 200,
                "notes": "Eks. mva, materialer inkl., tom bolig, ny gips med papirremser"
            },
            {
                "service": "helsparkling_kun",
                "description": "Helsparkling av vegg/tak (kun sparkel)",
                "unit": "m²", 
                "category": "sparkling",
                "min_price": 180,
                "max_price": 280,
                "notes": "Fullsparkling hele flaten, høyere ved strietapet/ujevne vegger"
            },
            {
                "service": "helsparkling_inkl_maling",
                "description": "Helsparkling + 2 strøk maling (kombinert)",
                "unit": "m²",
                "category": "kombinert_hel",
                "min_price": 250,
                "max_price": 350,
                "notes": "Eks. mva, tom leilighet, rabatt ved kombinert jobb"
            },
            {
                "service": "innvendig_maling_standard",
                "description": "Innvendig maling vegger/tak (standard)",
                "unit": "m²",
                "category": "maling_innvendig",
                "min_price": 170,
                "max_price": 270,
                "notes": "Inkl. flekksparkling, grunning, 2 strøk maling"
            },
            {
                "service": "innvendig_maling_enkel",
                "description": "Innvendig maling (enkelt, lite forarbeid)",
                "unit": "m²",
                "category": "maling_innvendig",
                "min_price": 50,
                "max_price": 65,
                "notes": "Kun maling, én farge, tom bolig, minimalt forarbeid"
            },
            {
                "service": "utvendig_maling_fasade",
                "description": "Utvendig maling (fasade)",
                "unit": "m²",
                "category": "maling_utvendig", 
                "min_price": 150,
                "max_price": 300,
                "notes": "Varierer med forarbeid, høyde, stillas. Større hus 200-300 kr/m²"
            },
            {
                "service": "listefri_tillegg",
                "description": "Listefri finish (tak/vinduer/dører) - tillegg",
                "unit": "m²",
                "category": "tillegg",
                "min_price": 150,
                "max_price": 200,
                "notes": "35-40% mer tidsbruk, ekstra sparkel/pussearbeid i overganger"
            }
        ]
        
        print("📊 Adding detailed service types and pricing:")
        
        # Add service types and pricing data
        for data in research_data:
            # Check if service type exists
            service = db.query(ServiceType).filter(ServiceType.name == data["service"]).first()
            if not service:
                service = ServiceType(
                    name=data["service"],
                    description=data["description"],
                    unit=data["unit"],
                    category=data["category"]
                )
                db.add(service)
                db.commit()
                print(f"✅ Added service: {data['service']}")
            
            # Add pricing data
            existing_pricing = db.query(PricingData).filter(
                PricingData.service_type_id == service.id,
                PricingData.source == "gpt_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="gpt_research_2025",
                    confidence=0.95,  # High confidence from recent market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']}-{data['max_price']} NOK/m² - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with research data")
        
        # Test key scenarios for house painting
        print("\n🏠 TESTING HOUSE SCENARIOS:")
        
        house_scenarios = [
            {
                "name": "150m² nytt hus - skjøtesparkling + maling",
                "service": "skjotesparkling_inkl_maling",
                "floor_area": 150,
                "paintable_area": 420  # 150 * 2.8
            },
            {
                "name": "150m² renovering - helsparkling + maling", 
                "service": "helsparkling_inkl_maling",
                "floor_area": 150,
                "paintable_area": 420
            },
            {
                "name": "100m² leilighet - standard innvendig maling",
                "service": "innvendig_maling_standard", 
                "floor_area": 100,
                "paintable_area": 280  # 100 * 2.8
            }
        ]
        
        for scenario in house_scenarios:
            result = pricing_service.get_service_price(scenario["service"], area=scenario["paintable_area"])
            
            if "error" not in result:
                base_cost = result.get("total_cost", {}).get("recommended", 0)
                unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                
                # Add realistic rigg og drift
                rigg_cost = max(15000, scenario["floor_area"] * 100)  # 100 NOK/m² gulvflate
                
                total_ex_vat = base_cost + rigg_cost
                total_inc_vat = total_ex_vat * 1.25
                
                print(f"\n🎯 {scenario['name']}:")
                print(f"   {scenario['paintable_area']} m² × {unit_price:.0f} NOK/m² = {base_cost:,.0f} NOK")
                print(f"   + Rigg og drift: {rigg_cost:,.0f} NOK")
                print(f"   = Total eks. mva: {total_ex_vat:,.0f} NOK")
                print(f"   = Total inkl. mva: {total_inc_vat:,.0f} NOK")
        
        print(f"\n🎉 Database updated with accurate Oslo/Viken market research!")
        print(f"📈 Sources: Mittanbud, Maleoppdrag.no, GP Bygg Invest, ByggeBolig (2022-2025)")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_with_gpt_research()