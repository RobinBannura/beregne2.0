#!/usr/bin/env python3
"""
Update pricing database with comprehensive flooring data from Oslo/Viken spring 2025
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_gulvarbeider_pricing():
    """Update with comprehensive flooring pricing from Oslo/Viken 2025"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🏠 Updating with flooring pricing data (Oslo/Viken spring 2025)")
        print("=" * 70)
        
        # Comprehensive flooring data based on your research
        gulvarbeider_data = [
            # Parquet flooring
            {
                "service": "parkett_legging_rettmonster",
                "description": "Legging av parkett (rettmønstret)",
                "unit": "m²",
                "category": "gulvlegging",
                "min_price": 300,
                "max_price": 500,
                "notes": "Startpris 300 kr hos Ditt Tregulv; parkett generelt min. 400 kr på Mittanbud"
            },
            {
                "service": "parkett_monstergulv_fiskebein",
                "description": "Parkett – mønstergulv (fiskebein, stav)",
                "unit": "m²",
                "category": "gulvlegging",
                "min_price": 800,
                "max_price": 1000,
                "notes": "≈ 900 kr veiledende pris fra Parketthuset (inkl. mva)"
            },
            
            # Laminate flooring
            {
                "service": "laminat_legging_standard",
                "description": "Legging av laminat",
                "unit": "m²",
                "category": "gulvlegging",
                "min_price": 150,
                "max_price": 400,
                "notes": "Enkleste gulvtyper 150-200 kr; prisguide oppgir 100-500 kr"
            },
            
            # Vinyl and specialty flooring
            {
                "service": "vinylgulv_vatrom_montering",
                "description": "Vinylgulv (våtrom, inkl. montering)",
                "unit": "m²",
                "category": "gulvlegging",
                "min_price": 700,
                "max_price": 1200,
                "notes": "Pris for GVK-sertifisert montør"
            },
            {
                "service": "microsementgulv_komplett",
                "description": "Microsementgulv",
                "unit": "m²",
                "category": "overflate",
                "min_price": 1200,
                "max_price": 1600,
                "notes": "Komplett inkl. material og arbeid"
            },
            {
                "service": "epoksygulv_bolig",
                "description": "Epoksygulv (bolig)",
                "unit": "m²",
                "category": "overflate",
                "min_price": 600,
                "max_price": 900,
                "notes": "Material 100-500 kr; ferdig lagt ca. 700 kr (m/avretting)"
            },
            
            # Surface preparation and installation services
            {
                "service": "gulvavretting_flytsparkel",
                "description": "Gulvavretting / flytsparkel",
                "unit": "m²",
                "category": "avretting",
                "min_price": 300,
                "max_price": 600,
                "notes": "Selv-nivå 310 kr; 40 m²-eksempel ≈ 600 kr/m²"
            },
            {
                "service": "varmekabler_installasjon_gulv",
                "description": "Installasjon av varmekabler",
                "unit": "m²",
                "category": "varme",
                "min_price": 900,
                "max_price": 1250,
                "notes": "Gjennomsnitt 2025-priser inkl. elektriker"
            },
            {
                "service": "gulvsliping_etterbehandling",
                "description": "Gulvsliping + etterbehandling",
                "unit": "m²",
                "category": "overflate",
                "min_price": 250,
                "max_price": 500,
                "notes": "Prisguide 150-300 kr + behandling; bransjeeksempler 250-500 kr"
            },
            
            # Demolition and preparation
            {
                "service": "riving_gammelt_gulv",
                "description": "Riving/demontering av gammelt gulv",
                "unit": "m²",
                "category": "riving",
                "min_price": 170,
                "max_price": 200,
                "notes": "Fjerning av parkett, tregulv el. tilsvarende"
            },
            {
                "service": "betong_sand_screed",
                "description": "Betong-/sand-screed (plate på gulv)",
                "unit": "m²",
                "category": "avretting",
                "min_price": 520,
                "max_price": 590,
                "notes": "0-100 mm tykk sement-sand avretting"
            },
            {
                "service": "isolering_undergulv_trinnlyd",
                "description": "Isolering undergulv / trinnlyd",
                "unit": "m²",
                "category": "isolasjon",
                "min_price": 550,
                "max_price": 650,
                "notes": "≈ 600 kr snitt fra Boligfiks prosjektdatabase"
            },
            
            # Package deals for common scenarios
            {
                "service": "komplett_parkett_30m2_pakke",
                "description": "Komplett parkett 30m² (inkl. avretting)",
                "unit": "pakke",
                "category": "gulv_pakke",
                "min_price": 18000,
                "max_price": 24000,
                "notes": "Avretting + parkett + finish for 30m² rom"
            },
            {
                "service": "komplett_laminat_50m2_pakke",
                "description": "Komplett laminat 50m² (inkl. underlag)",
                "unit": "pakke",
                "category": "gulv_pakke",
                "min_price": 12000,
                "max_price": 18000,
                "notes": "Riving + underlag + laminat for 50m² hus"
            },
            {
                "service": "komplett_bad_vinylgulv_8m2",
                "description": "Komplett bad vinylgulv 8m² (våtrom)",
                "unit": "pakke",
                "category": "gulv_pakke",
                "min_price": 7000,
                "max_price": 11000,
                "notes": "Avretting + GVK-sertifisert vinyl for 8m² bad"
            },
            
            # DIY alternatives for comparison
            {
                "service": "epoksygulv_diy_kit",
                "description": "Epoksygulv (DIY-variant)",
                "unit": "m²",
                "category": "diy_gulv",
                "min_price": 200,
                "max_price": 400,
                "notes": "DIY-kit for selvmontering, ekskl. arbeid"
            },
            {
                "service": "microsement_diy_kit", 
                "description": "Microsement (DIY-variant)",
                "unit": "m²",
                "category": "diy_gulv",
                "min_price": 300,
                "max_price": 500,
                "notes": "DIY-kit for selvmontering, ekskl. arbeid"
            }
        ]
        
        print("📊 Adding comprehensive flooring services and pricing:")
        
        # Add service types and pricing data
        for data in gulvarbeider_data:
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
                PricingData.source == "gulvarbeider_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="gulvarbeider_research_2025",
                    confidence=0.92,  # High confidence from detailed market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']:,.0f}-{data['max_price']:,.0f} NOK/{data['unit']} - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with flooring data")
        
        # Test key flooring scenarios
        print("\n🏠 TESTING FLOORING SCENARIOS:")
        print("=" * 50)
        
        test_scenarios = [
            {
                "name": "Parkett legging 25m² (rettmønster)",
                "service": "parkett_legging_rettmonster",
                "quantity": 25,
                "unit": "m²"
            },
            {
                "name": "Laminat 40m² stue/gang",
                "service": "laminat_legging_standard",
                "quantity": 40,
                "unit": "m²"
            },
            {
                "name": "Vinylgulv bad 6m² (våtrom)",
                "service": "vinylgulv_vatrom_montering",
                "quantity": 6,
                "unit": "m²"
            },
            {
                "name": "Gulvavretting 30m²",
                "service": "gulvavretting_flytsparkel",
                "quantity": 30,
                "unit": "m²"
            },
            {
                "name": "Varmekabler 20m²",
                "service": "varmekabler_installasjon_gulv",
                "quantity": 20,
                "unit": "m²"
            },
            {
                "name": "Komplett parkett 30m² (pakke)",
                "service": "komplett_parkett_30m2_pakke",
                "quantity": 1,
                "unit": "pakke"
            }
        ]
        
        for scenario in test_scenarios:
            try:
                if scenario["quantity"] > 1:
                    result = pricing_service.get_service_price(scenario["service"], area=scenario["quantity"])
                    cost = result.get("total_cost", {}).get("recommended", 0)
                else:
                    result = pricing_service.get_service_price(scenario["service"])
                    cost = result.get("unit_price", {}).get("recommended_price", 0)
                
                if cost > 0:
                    cost_inc_vat = cost * 1.25
                    print(f"\n🏠 {scenario['name']}:")
                    print(f"   Cost: {cost:,.0f} NOK eks. mva")
                    print(f"   Incl. VAT: {cost_inc_vat:,.0f} NOK")
                    if scenario["quantity"] > 1:
                        unit_cost = cost / scenario["quantity"]
                        print(f"   Per {scenario['unit']}: {unit_cost:,.0f} NOK")
                
            except Exception as e:
                print(f"   ❌ Error testing {scenario['name']}: {str(e)}")
        
        # Show cost comparison for different flooring types (per m²)
        print(f"\n📊 FLOORING COST COMPARISON (per m²):")
        print("=" * 50)
        
        flooring_types = [
            ("laminat_legging_standard", "Laminat"),
            ("parkett_legging_rettmonster", "Parkett (rett)"),
            ("parkett_monstergulv_fiskebein", "Parkett (fiskebein)"),
            ("vinylgulv_vatrom_montering", "Vinyl (våtrom)"),
            ("microsementgulv_komplett", "Microsement"),
            ("epoksygulv_bolig", "Epoxy")
        ]
        
        try:
            print("Professional installation prices:")
            for service_name, display_name in flooring_types:
                result = pricing_service.get_service_price(service_name)
                if "error" not in result:
                    unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                    min_price = result.get("unit_price", {}).get("min_price", 0)
                    max_price = result.get("unit_price", {}).get("max_price", 0)
                    print(f"   {display_name}: {min_price:,.0f}-{max_price:,.0f} NOK/m² (snitt: {unit_price:,.0f})")
        
        except Exception as e:
            print(f"   ❌ Error comparing flooring types: {str(e)}")
        
        # Show DIY vs Professional comparison
        print(f"\n💡 DIY vs PROFESSIONAL COMPARISON:")
        print("=" * 40)
        
        try:
            epoxy_pro = pricing_service.get_service_price("epoksygulv_bolig")
            epoxy_diy = pricing_service.get_service_price("epoksygulv_diy_kit")
            
            if "error" not in epoxy_pro and "error" not in epoxy_diy:
                pro_price = epoxy_pro.get("unit_price", {}).get("recommended_price", 0)
                diy_price = epoxy_diy.get("unit_price", {}).get("recommended_price", 0)
                
                savings = pro_price - diy_price
                savings_percent = (savings / pro_price) * 100 if pro_price > 0 else 0
                
                print(f"Epoxy flooring (per m²):")
                print(f"   🔧 Professional: {pro_price:,.0f} NOK/m²")
                print(f"   🛠️  DIY kit: {diy_price:,.0f} NOK/m²")
                print(f"   💰 DIY savings: {savings:,.0f} NOK/m² ({savings_percent:.1f}%)")
        
        except Exception as e:
            print(f"   ❌ Error comparing DIY vs Pro: {str(e)}")
        
        # Show complete flooring project cost
        print(f"\n🏠 COMPLETE FLOORING PROJECT (40m² living room):")
        print("=" * 55)
        
        try:
            # Calculate complete flooring project
            components = [
                ("riving_gammelt_gulv", 40, "Remove old flooring"),
                ("gulvavretting_flytsparkel", 40, "Floor leveling"),
                ("varmekabler_installasjon_gulv", 40, "Floor heating"),
                ("parkett_legging_rettmonster", 40, "Parquet installation")
            ]
            
            total_project_cost = 0
            print("Complete flooring renovation (40m² room):")
            
            for service_name, quantity, description in components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_project_cost += cost
                    print(f"   {description}: {cost:,.0f} NOK")
                else:
                    print(f"   {description}: Error getting price")
            
            total_inc_vat = total_project_cost * 1.25
            cost_per_m2 = total_project_cost / 40
            
            print(f"\n   📊 Total project cost: {total_project_cost:,.0f} NOK eks. mva")
            print(f"   📊 Total incl. VAT: {total_inc_vat:,.0f} NOK")
            print(f"   📐 Cost per m²: {cost_per_m2:,.0f} NOK/m²")
        
        except Exception as e:
            print(f"   ❌ Error calculating project: {str(e)}")
        
        print(f"\n🎉 Flooring pricing database updated!")
        print(f"📈 Comprehensive Oslo/Viken market data for spring 2025")
        print(f"🏠 Covers: parquet, laminate, vinyl, specialty surfaces")
        print(f"🔧 Includes: installation, preparation, heating, DIY options")
        print(f"💡 Key insight: DIY can save 40-60% but requires skill and time")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_gulvarbeider_pricing()