#!/usr/bin/env python3
"""
Update pricing database with detailed bathroom renovation data from Oslo/Viken 2024-25
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_bathroom_pricing():
    """Update with detailed bathroom renovation research from Oslo/Viken"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🛁 Updating with bathroom renovation data (Oslo/Viken 2024-25)")
        print("=" * 65)
        
        # Detailed bathroom renovation data
        bathroom_data = [
            # Complete bathroom packages
            {
                "service": "bad_totalrenovering_4m2",
                "description": "Totalrenovering 4m² bad (nøkkelferdig)",
                "unit": "stk",
                "category": "bad_komplett",
                "min_price": 280000,
                "max_price": 360000,
                "notes": "Pakkepriser 4m² bad, høyest kr/m² pga teknikk"
            },
            {
                "service": "bad_totalrenovering_8m2", 
                "description": "Totalrenovering 8m² bad (nøkkelferdig)",
                "unit": "stk",
                "category": "bad_komplett",
                "min_price": 340000,
                "max_price": 440000,
                "notes": "Pakkepriser 8m² bad"
            },
            {
                "service": "bad_totalrenovering_12m2",
                "description": "Totalrenovering 12m² bad (nøkkelferdig)",
                "unit": "stk", 
                "category": "bad_komplett",
                "min_price": 400000,
                "max_price": 520000,
                "notes": "Pakkepriser 12m² bad, lavest kr/m²"
            },
            
            # Individual components per m²
            {
                "service": "bad_riving_avfall",
                "description": "Riving + avfallshåndtering",
                "unit": "m²",
                "category": "bad_riving",
                "min_price": 2000,
                "max_price": 5000,
                "notes": "10-25k kr for 5m² bad"
            },
            {
                "service": "bad_membran",
                "description": "Membran (arbeid + material)",
                "unit": "m²", 
                "category": "bad_membran",
                "min_price": 2000,
                "max_price": 4000,
                "notes": "10-20k kr for 5m². Material: duk ≈100 kr/m², smøre 50-70 kr/m²"
            },
            {
                "service": "bad_flislegging_arbeid",
                "description": "Flislegging (arbeid, ekskl. fliser)",
                "unit": "m²",
                "category": "bad_flislegging", 
                "min_price": 12000,
                "max_price": 22000,
                "notes": "Snitt rundt 16000 kr/m²"
            },
            {
                "service": "bad_fliser_material",
                "description": "Fliser (material)",
                "unit": "m²",
                "category": "bad_material",
                "min_price": 100,
                "max_price": 2000,
                "notes": "Vanlig standard ca. 500 kr/m²"
            },
            {
                "service": "bad_elektriker",
                "description": "Elektriker (bad)",
                "unit": "m²",
                "category": "bad_elektro",
                "min_price": 6000,
                "max_price": 10000,
                "notes": "30-50k kr for 5m² bad"
            },
            {
                "service": "bad_rorlegger",
                "description": "Rørlegger (bad)", 
                "unit": "m²",
                "category": "bad_ror",
                "min_price": 8000,
                "max_price": 15000,
                "notes": "40-75k kr for 5m² bad"
            },
            {
                "service": "bad_maler_vatrom",
                "description": "Maler (våtrom)",
                "unit": "m²",
                "category": "bad_maling",
                "min_price": 1000,
                "max_price": 3000,
                "notes": "5-15k kr for 5m² bad"
            },
            {
                "service": "bad_vinyl_belegg",
                "description": "Vinyl/belegg (material-alternativ til flis)",
                "unit": "m²",
                "category": "bad_material",
                "min_price": 300,
                "max_price": 700,
                "notes": "Enklere, raskere montering enn fliser"
            }
        ]
        
        print("📊 Adding detailed bathroom services and pricing:")
        
        # Add service types and pricing data
        for data in bathroom_data:
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
                PricingData.source == "bathroom_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="bathroom_research_2025",
                    confidence=0.95,  # High confidence from recent market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']:,.0f}-{data['max_price']:,.0f} NOK/{data['unit']} - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with bathroom data")
        
        # Test bathroom scenarios
        print("\n🛁 TESTING BATHROOM SCENARIOS:")
        
        bathroom_scenarios = [
            {
                "name": "4m² bad (totalrenovering)",
                "service": "bad_totalrenovering_4m2",
                "area": 4,
                "unit": "stk"
            },
            {
                "name": "8m² bad (totalrenovering)",
                "service": "bad_totalrenovering_8m2", 
                "area": 8,
                "unit": "stk"
            },
            {
                "name": "5m² bad - komponentbasert beregning",
                "components": [
                    ("bad_riving_avfall", 5),
                    ("bad_membran", 5),
                    ("bad_flislegging_arbeid", 5),
                    ("bad_fliser_material", 5),
                    ("bad_elektriker", 5),
                    ("bad_rorlegger", 5),
                    ("bad_maler_vatrom", 5)
                ]
            }
        ]
        
        for scenario in bathroom_scenarios:
            if "service" in scenario:
                # Package pricing
                result = pricing_service.get_service_price(scenario["service"])
                if "error" not in result:
                    price = result.get("unit_price", {}).get("recommended_price", 0)
                    price_inc_vat = price * 1.25
                    price_per_m2 = price / scenario["area"]
                    
                    print(f"\n🎯 {scenario['name']}:")
                    print(f"   Pakke: {price:,.0f} NOK eks. mva")
                    print(f"   Inkl. mva: {price_inc_vat:,.0f} NOK")
                    print(f"   Per m²: {price_per_m2:,.0f} NOK/m²")
            
            elif "components" in scenario:
                # Component-based calculation
                total_cost = 0
                print(f"\n🎯 {scenario['name']}:")
                
                for service_name, area in scenario["components"]:
                    result = pricing_service.get_service_price(service_name, area=area)
                    if "error" not in result:
                        cost = result.get("total_cost", {}).get("recommended", 0) if area > 1 else result.get("unit_price", {}).get("recommended_price", 0)
                        total_cost += cost
                        print(f"   {service_name}: {cost:,.0f} NOK")
                
                total_inc_vat = total_cost * 1.25
                print(f"   ────────────────────────────────")
                print(f"   Total eks. mva: {total_cost:,.0f} NOK")
                print(f"   Total inkl. mva: {total_inc_vat:,.0f} NOK")
        
        print(f"\n🎉 Bathroom pricing database updated!")
        print(f"📈 Complete renovation packages + individual components")
        print(f"💡 Key insight: Small bathrooms = higher NOK/m² due to technical overhead")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_bathroom_pricing()