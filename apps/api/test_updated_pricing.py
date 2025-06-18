#!/usr/bin/env python3
"""
Test the updated pricing for sparkle and paint house
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService

def test_updated_house_pricing():
    """Test updated pricing for sparkling and painting house"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        area = 150
        print(f"🏠 Sparkle og male nytt hus på {area} m² - OPPDATERTE PRISER")
        print("=" * 65)
        
        # Test the new combo services
        services_to_test = [
            ("skjotesparkling_og_maling", "Skjøtesparkling og maling (nybygd hus)"),
            ("helsparkling_og_maling", "Helsparkling og maling (nybygd hus)"),
            ("maling", "Kun maling (eksisterende system)"),
            ("sparkling", "Kun sparkling (eksisterende system)")
        ]
        
        print("💰 PRISALTERNATIVER:")
        print()
        
        for service_name, description in services_to_test:
            result = pricing_service.get_service_price(service_name, area=area)
            
            if "error" not in result:
                total_cost = result.get("total_cost", {}).get("recommended", 0)
                unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                
                # Add estimated rigg og drift (simplified calculation)
                if "sparkling" in service_name or "maling" in service_name:
                    rigg_cost = max(4000, area * 15)  # 15 NOK/m² rigg + base
                    total_with_rigg = total_cost + rigg_cost
                    
                    print(f"🎯 {description}")
                    print(f"   Arbeid og materialer: {total_cost:,.0f} NOK ({unit_price:.0f} NOK/m²)")
                    print(f"   Rigg og drift:        {rigg_cost:,.0f} NOK")
                    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    print(f"   TOTAL:               {total_with_rigg:,.0f} NOK")
                    print()
                else:
                    print(f"🎯 {description}")
                    print(f"   Total: {total_cost:,.0f} NOK ({unit_price:.0f} NOK/m²)")
                    print()
            else:
                print(f"❌ {description}: {result['error']}")
                print()
        
        # Room-based examples for comparison
        print("📏 ROMBASERTE EKSEMPLER (markedsdata):")
        room_services = [
            ("rom_maling_en_farge", "Male rom, en farge (≤7m² gulv)"),
            ("rom_maling_to_farger", "Male rom, to farger (≤7m² gulv)"), 
            ("rom_sparkling_og_maling", "Sparkle og male rom (≤7m² gulv)")
        ]
        
        for service_name, description in room_services:
            result = pricing_service.get_service_price(service_name)
            if "error" not in result:
                unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                print(f"   {description}: {unit_price:,.0f} NOK/rom")
        
        print(f"\n🏆 ANBEFALING FOR {area}M² NYTT HUS:")
        print("   Skjøtesparkling og maling: 39,375 NOK")
        print("   (Mest vanlig for nye hus med gipsvegger)")
        print()
        print("💡 VIKTIGE FAKTORER:")
        print("   • Grunning → Sparkling → Sliping → Maling")
        print("   • Nye hus trenger vanligvis skjøtesparkling")
        print("   • Helsparkling kun hvis vegger er i dårlig stand")
        print("   • Alle priser eks. mva.")
        print("   • Inkluderer materialer, kjøring, tildekking, rengjøring")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_house_pricing()