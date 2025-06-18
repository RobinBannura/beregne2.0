#!/usr/bin/env python3
"""
Update pricing database with real market data from competitors
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_market_pricing():
    """Update with real market pricing from competitors"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🔄 Updating pricing database with real market data...")
        print("=" * 50)
        
        # Market pricing from competitor analysis
        market_updates = [
            # Combo services (most common)
            {
                "service": "skjotesparkling_og_maling",
                "description": "Skjøtesparkling og maling av gipsvegger (nybygd hus)",
                "unit": "m²",
                "category": "kombinert",
                "min_price": 200,
                "max_price": 250,
                "source": "market_competitor_analysis"
            },
            {
                "service": "helsparkling_og_maling", 
                "description": "Helsparkling og maling av gipsvegger (nybygd hus)",
                "unit": "m²",
                "category": "kombinert",
                "min_price": 250,
                "max_price": 300,
                "source": "market_competitor_analysis"
            },
            {
                "service": "maling_panel",
                "description": "Maling av veggpanel/takpanel",
                "unit": "m²", 
                "category": "overflatebehandling",
                "min_price": 120,
                "max_price": 180,
                "source": "market_competitor_analysis"
            },
            
            # Room-based pricing examples
            {
                "service": "rom_maling_en_farge",
                "description": "Male rom vegger og tak samme farge (opp til 7m² gulv)",
                "unit": "rom",
                "category": "rom_basert",
                "min_price": 6000,
                "max_price": 8000,
                "source": "market_competitor_analysis"
            },
            {
                "service": "rom_maling_to_farger",
                "description": "Male rom vegger og tak forskjellige farger (opp til 7m² gulv)",
                "unit": "rom",
                "category": "rom_basert", 
                "min_price": 8000,
                "max_price": 10000,
                "source": "market_competitor_analysis"
            },
            {
                "service": "rom_sparkling_og_maling",
                "description": "Sparkling (skjøter) og maling av rom (opp til 7m² gulv)",
                "unit": "rom",
                "category": "rom_basert",
                "min_price": 16000,
                "max_price": 20000,
                "source": "market_competitor_analysis"
            }
        ]
        
        # Add new service types if they don't exist
        for update in market_updates:
            service = db.query(ServiceType).filter(ServiceType.name == update["service"]).first()
            if not service:
                service = ServiceType(
                    name=update["service"],
                    description=update["description"],
                    unit=update["unit"],
                    category=update["category"]
                )
                db.add(service)
                db.commit()
                print(f"✅ Added new service type: {update['service']}")
            
            # Add pricing data
            existing_pricing = db.query(PricingData).filter(
                PricingData.service_type_id == service.id,
                PricingData.source == update["source"]
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=update["min_price"],
                    max_price=update["max_price"],
                    avg_price=(update["min_price"] + update["max_price"]) / 2,
                    region="Oslo",
                    source=update["source"],
                    confidence=0.9  # High confidence from competitor analysis
                )
                db.add(pricing_data)
                print(f"✅ Added pricing for {update['service']}: {update['min_price']}-{update['max_price']} NOK/{update['unit']}")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated")
        
        # Test some of the new pricing
        print("\n📊 Testing updated pricing:")
        
        test_services = [
            ("skjotesparkling_og_maling", 150),
            ("helsparkling_og_maling", 150), 
            ("maling_panel", 100)
        ]
        
        for service_name, area in test_services:
            result = pricing_service.get_service_price(service_name, area=area)
            if "error" not in result:
                total = result.get("total_cost", {}).get("recommended", 0)
                unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                print(f"   {service_name}: {total:,.0f} NOK ({unit_price:.0f} NOK/m² for {area}m²)")
            else:
                print(f"   {service_name}: {result['error']}")
        
        db.close()
        print("\n🎉 Pricing database updated with market data!")
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_market_pricing()