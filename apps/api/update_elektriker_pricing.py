#!/usr/bin/env python3
"""
Update pricing database with comprehensive electrician data from Oslo/Viken spring 2025
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_elektriker_pricing():
    """Update with comprehensive electrician pricing from Oslo/Viken 2025"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("⚡ Updating with electrician pricing data (Oslo/Viken spring 2025)")
        print("=" * 70)
        
        # Comprehensive electrician data based on your research
        elektriker_data = [
            # Basic rates and startup costs
            {
                "service": "elektriker_timepris_montor",
                "description": "Timepris elektriker montør",
                "unit": "time",
                "category": "elektriker_arbeid",
                "min_price": 700,
                "max_price": 1100,
                "notes": "Storbyspenn 700-1300 kr; Oslo eksempler 900-1500 kr"
            },
            {
                "service": "elektriker_oppstart_servicebil",
                "description": "Oppstart / servicebil",
                "unit": "fast",
                "category": "elektriker_oppstart",
                "min_price": 500,
                "max_price": 850,
                "notes": "Ofte inkludert én times arbeid i pakkepris"
            },
            
            # Sikringsskap og kurser
            {
                "service": "nytt_sikringsskap_7_14_kurser",
                "description": "Nytt sikringsskap (7-14 kurser, overspenningsvern)",
                "unit": "stk",
                "category": "sikringsskap",
                "min_price": 10000,
                "max_price": 25000,
                "notes": "Snitt ca. 18 000 kr; kampanjeeksempel 8 390 kr ferdig montert"
            },
            {
                "service": "ny_kurs_16a",
                "description": "Én ny kurs fra skap (16 A)",
                "unit": "stk",
                "category": "kurs",
                "min_price": 4000,
                "max_price": 6000,
                "notes": "Fastpris fra 5 290 kr (SpotOn); forumerfaring ~4 000 kr"
            },
            
            # Stikkontakter og punkter
            {
                "service": "ekstra_stikkontakt_dobbel",
                "description": "Ekstra stikkontakt (dobbel)",
                "unit": "stk",
                "category": "punkt",
                "min_price": 700,
                "max_price": 1200,
                "notes": "Material inkludert; 350 kr + arbeid ved mange punkter"
            },
            
            # Belysning
            {
                "service": "downlight_led_ny_installasjon",
                "description": "Downlight (LED) - ny installasjon",
                "unit": "stk",
                "category": "belysning",
                "min_price": 1200,
                "max_price": 2000,
                "notes": "LED-spotter dyrere enn halogen; pakkeløsning gir lavere stykkpris"
            },
            {
                "service": "downlight_utskifting_halogen_led",
                "description": "Downlight - utskifting halogen → LED",
                "unit": "stk",
                "category": "belysning",
                "min_price": 650,
                "max_price": 1000,
                "notes": "Rimeligere siden hull finnes fra før"
            },
            
            # Gulvvarme og spesialinstallasjoner
            {
                "service": "varmekabler_gulv",
                "description": "Varmekabler (gulv)",
                "unit": "m²",
                "category": "gulvvarme",
                "min_price": 900,
                "max_price": 1250,
                "notes": "Inkl. materialer & arbeid; større rom ⇒ lavere kr/m²"
            },
            
            # Kontroll og service
            {
                "service": "el_sjekk_kontroll",
                "description": "El-sjekk / el-kontroll",
                "unit": "fast",
                "category": "kontroll",
                "min_price": 3500,
                "max_price": 5000,
                "notes": "Typisk boligkontroll med rapport"
            },
            
            # Elbillader
            {
                "service": "elbillader_installasjon",
                "description": "Elbillader (inkl. installasjon)",
                "unit": "pakke",
                "category": "elbil",
                "min_price": 10000,
                "max_price": 20000,
                "notes": "Arbeid 3-8 t + 10-15 m kabel; kan stige til 25 000 kr"
            },
            
            # Komplette anlegg
            {
                "service": "fullt_skjult_elanlegg_100m2",
                "description": "Fullt, skjult el-anlegg (100 m² leilighet)",
                "unit": "total",
                "category": "fullt_anlegg",
                "min_price": 110000,
                "max_price": 150000,
                "notes": "≈ 130 000 kr total / ca. 1 300 kr m²; 75-100k for små leil."
            },
            {
                "service": "fullt_skjult_elanlegg_per_m2",
                "description": "Fullt, skjult el-anlegg",
                "unit": "m²",
                "category": "fullt_anlegg",
                "min_price": 1000,
                "max_price": 1500,
                "notes": "1300 kr/m² snitt; 200 m² ≈ 200 000 kr"
            },
            {
                "service": "apent_elanlegg_per_m2",
                "description": "Åpent (utenpåliggende) anlegg",
                "unit": "m²",
                "category": "fullt_anlegg",
                "min_price": 800,
                "max_price": 1200,
                "notes": "≈ 10-25% rimeligere enn skjult; krever synlige kanaler"
            },
            
            # Package deals for efficiency
            {
                "service": "downlight_pakke_10_stk",
                "description": "10 downlights LED inkl. dimmer (pakkeløsning)",
                "unit": "pakke",
                "category": "belysning_pakke",
                "min_price": 12000,
                "max_price": 18000,
                "notes": "Pakkeløsning gir lavere stykkpris enn enkeltvis"
            },
            {
                "service": "stikkontakt_pakke_5_stk",
                "description": "5 ekstra stikkontakter (pakkeløsning)",
                "unit": "pakke",
                "category": "punkt_pakke",
                "min_price": 3000,
                "max_price": 5000,
                "notes": "350 kr + arbeid ved mange punkter - mer effektivt"
            }
        ]
        
        print("📊 Adding comprehensive electrician services and pricing:")
        
        # Add service types and pricing data
        for data in elektriker_data:
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
                PricingData.source == "elektriker_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="elektriker_research_2025",
                    confidence=0.95,  # High confidence from detailed market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']:,.0f}-{data['max_price']:,.0f} NOK/{data['unit']} - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with electrician data")
        
        # Test key electrician scenarios
        print("\n⚡ TESTING ELECTRICIAN SCENARIOS:")
        print("=" * 50)
        
        test_scenarios = [
            {
                "name": "Basic hourly rate",
                "service": "elektriker_timepris_montor",
                "unit": "time",
                "quantity": 4
            },
            {
                "name": "New electrical panel",
                "service": "nytt_sikringsskap_7_14_kurser",
                "unit": "stk",
                "quantity": 1
            },
            {
                "name": "5 extra outlets (package)",
                "service": "stikkontakt_pakke_5_stk",
                "unit": "pakke", 
                "quantity": 1
            },
            {
                "name": "10 downlights (package)",
                "service": "downlight_pakke_10_stk",
                "unit": "pakke",
                "quantity": 1
            },
            {
                "name": "Floor heating 20m²",
                "service": "varmekabler_gulv",
                "unit": "m²",
                "quantity": 20
            },
            {
                "name": "Full electrical system 100m²",
                "service": "fullt_skjult_elanlegg_per_m2",
                "unit": "m²",
                "quantity": 100
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
                    print(f"\n🔧 {scenario['name']}:")
                    print(f"   Cost: {cost:,.0f} NOK eks. mva")
                    print(f"   Incl. VAT: {cost_inc_vat:,.0f} NOK")
                    if scenario["quantity"] > 1:
                        unit_cost = cost / scenario["quantity"]
                        print(f"   Per {scenario['unit']}: {unit_cost:,.0f} NOK")
                
            except Exception as e:
                print(f"   ❌ Error testing {scenario['name']}: {str(e)}")
        
        # Show hidden vs open installation comparison
        print(f"\n💡 HIDDEN vs OPEN INSTALLATION COMPARISON:")
        print("=" * 55)
        
        try:
            hidden_result = pricing_service.get_service_price("fullt_skjult_elanlegg_per_m2", area=100)
            open_result = pricing_service.get_service_price("apent_elanlegg_per_m2", area=100)
            
            hidden_cost = hidden_result.get("total_cost", {}).get("recommended", 0)
            open_cost = open_result.get("total_cost", {}).get("recommended", 0)
            
            if hidden_cost > 0 and open_cost > 0:
                savings = hidden_cost - open_cost
                savings_percent = (savings / hidden_cost) * 100
                
                print(f"100m² apartment electrical installation:")
                print(f"   🔒 Hidden installation: {hidden_cost:,.0f} NOK eks. mva")
                print(f"   📦 Open installation: {open_cost:,.0f} NOK eks. mva")
                print(f"   💰 Savings with open: {savings:,.0f} NOK ({savings_percent:.1f}%)")
                print(f"   📏 Hidden gives cleaner look but higher cost")
        
        except Exception as e:
            print(f"   ❌ Error comparing installation types: {str(e)}")
        
        print(f"\n🎉 Electrician pricing database updated!")
        print(f"📈 Comprehensive Oslo/Viken market data for spring 2025")
        print(f"⚡ Covers: timework, installations, packages, full systems")
        print(f"🔧 Key insight: Package deals significantly reduce per-unit costs")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_elektriker_pricing()