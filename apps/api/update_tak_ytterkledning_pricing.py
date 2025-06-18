#!/usr/bin/env python3
"""
Update pricing database with comprehensive tak og ytterkledning data from Oslo/Viken spring 2025
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_tak_ytterkledning_pricing():
    """Update with comprehensive tak og ytterkledning pricing from Oslo/Viken 2025"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🏠 Updating with tak og ytterkledning pricing data (Oslo/Viken spring 2025)")
        print("=" * 75)
        
        # Comprehensive tak og ytterkledning data based on your research
        tak_ytterkledning_data = [
            # Roof work
            {
                "service": "takomlegging_nytt_tak_komplett",
                "description": "Takomlegging (nytt tak) inkl. tekking og beslag",
                "unit": "m²",
                "category": "tak",
                "min_price": 1360,
                "max_price": 2800,
                "notes": "Komplett omlegging av yttertak inkl. riving, undertak, tekking, lekter, takrenner. Snitt ~2300 kr/m²"
            },
            {
                "service": "takrenner_nedlop_nye",
                "description": "Takrenner og nedløp (nye)",
                "unit": "lm",
                "category": "takrenner",
                "min_price": 200,
                "max_price": 500,
                "notes": "Plast i nedre prissjikt (~200 kr/m), metall som sink/stål mot øvre sjikt (~400-500 kr/m)"
            },
            
            # External insulation and cladding
            {
                "service": "etterisolering_utvendig_ny_kledning",
                "description": "Etterisolering utvendig (vegg) inkl. ny kledning",
                "unit": "m²",
                "category": "etterisolering",
                "min_price": 1600,
                "max_price": 3200,
                "notes": "Utvendig etterisolering med bytte av kledning. Typisk 2000-4000 kr/m² inkl. mva (1600-3200 eks. mva)"
            },
            {
                "service": "utvendig_kledning_trepanel_utskifting",
                "description": "Utvendig kledning (trepanel) - utskifting",
                "unit": "m²",
                "category": "kledning",
                "min_price": 1200,
                "max_price": 2800,
                "notes": "Fjerning og ny kledning på vegg. Typisk 1500-3500 kr/m² inkl. mva for trepanel, snitt ~2000 kr/m²"
            },
            
            # Roof materials by type
            {
                "service": "takstein_legging",
                "description": "Takstein legging (betong/tegl)",
                "unit": "m²",
                "category": "taklegging",
                "min_price": 400,
                "max_price": 800,
                "notes": "Kun legging av takstein. Betongtakstein rimeligere enn tegl. Komplekse takformer øker prisen"
            },
            {
                "service": "takshingel_papp_legging",
                "description": "Takshingel/papp legging",
                "unit": "m²",
                "category": "taklegging", 
                "min_price": 200,
                "max_price": 400,
                "notes": "Rimeligste takmateriale. Inkluderer undertak og legging. Kortere levetid enn takstein"
            },
            {
                "service": "skifer_legging_premium",
                "description": "Skifer legging (premium)",
                "unit": "m²",
                "category": "taklegging",
                "min_price": 800,
                "max_price": 1500,
                "notes": "Naturskifer eller skiferlook. Dyreste takløsning, men svært lang levetid og estetikk"
            },
            
            # Insulation work
            {
                "service": "isolasjon_5_10cm_utvendig",
                "description": "Isolasjon 5-10cm utvendig",
                "unit": "m²",
                "category": "isolasjon",
                "min_price": 300,
                "max_price": 600,
                "notes": "5-10 cm isolasjon med vindsperre og lekter. Del av etterisolering, men kan prises separat"
            },
            {
                "service": "vindsperre_montering",
                "description": "Vindsperre montering",
                "unit": "m²",
                "category": "isolasjon",
                "min_price": 50,
                "max_price": 100,
                "notes": "Montering av vindsperre/vindtett membran på yttervegger"
            },
            
            # Scaffolding and access
            {
                "service": "stillas_utleie_takarbeid",
                "description": "Stillas utleie for takarbeid",
                "unit": "m²",
                "category": "stillas",
                "min_price": 150,
                "max_price": 300,
                "notes": "Stillas for takarbeider. Pris per m² takflate per måned. Høyde og kompleksitet påvirker pris"
            },
            
            # Cladding types
            {
                "service": "kledning_gran_furu_standard",
                "description": "Kledning gran/furu standard",
                "unit": "m²",
                "category": "kledning",
                "min_price": 800,
                "max_price": 1500,
                "notes": "Standard trekledning i gran/furu. Rimeligste alternativ. Krever regelmessig vedlikehold"
            },
            {
                "service": "kledning_eksklusive_tresorter",
                "description": "Kledning eksklusive tresorter (eik, seder)",
                "unit": "m²",
                "category": "kledning",
                "min_price": 2500,
                "max_price": 3500,
                "notes": "Eik, sedertre, eller andre eksklusive tresorter. Lang levetid, minimal vedlikehold"
            },
            
            # Package deals
            {
                "service": "komplett_tak_120m2_pakke",
                "description": "Komplett tak 120m² (pakkeløsning)",
                "unit": "pakke",
                "category": "tak_pakke",
                "min_price": 200000,
                "max_price": 350000,
                "notes": "Komplett takomlegging for typisk enebolig. Inkluderer riving, undertak, tekking, renner"
            },
            {
                "service": "komplett_etterisolering_100m2_pakke",
                "description": "Komplett etterisolering 100m² vegg (pakkeløsning)",
                "unit": "pakke",
                "category": "isolering_pakke",
                "min_price": 180000,
                "max_price": 320000,
                "notes": "Komplett etterisolering av yttervegger inkl. ny kledning for 100m² veggflate"
            },
            
            # Specialized roof work
            {
                "service": "takvindu_velux_montering",
                "description": "Takvindu (Velux) montering",
                "unit": "stk",
                "category": "takvindu",
                "min_price": 15000,
                "max_price": 35000,
                "notes": "Takvindu inkl. montering. Standard Velux 20-50k inkl. montering. Størrelse og type påvirker pris"
            },
            {
                "service": "takovergang_gesims_arbeid",
                "description": "Takovergang/gesims arbeid",
                "unit": "lm",
                "category": "takdetaljer",
                "min_price": 300,
                "max_price": 600,
                "notes": "Spesialarbeid på takovergang, gesims og vindskier. Krever høy presisjon"
            }
        ]
        
        print("📊 Adding comprehensive tak og ytterkledning services and pricing:")
        
        # Add service types and pricing data
        for data in tak_ytterkledning_data:
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
                PricingData.source == "tak_ytterkledning_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="tak_ytterkledning_research_2025",
                    confidence=0.91,  # High confidence from detailed market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']:,.0f}-{data['max_price']:,.0f} NOK/{data['unit']} - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with tak og ytterkledning data")
        
        # Test key tak og ytterkledning scenarios
        print("\n🏠 TESTING TAK OG YTTERKLEDNING SCENARIOS:")
        print("=" * 55)
        
        test_scenarios = [
            {
                "name": "Takomlegging 100m² (komplett)",
                "service": "takomlegging_nytt_tak_komplett",
                "quantity": 100,
                "unit": "m²"
            },
            {
                "name": "Takrenner 40 løpemeter",
                "service": "takrenner_nedlop_nye",
                "quantity": 40,
                "unit": "lm"
            },
            {
                "name": "Etterisolering 80m² vegg",
                "service": "etterisolering_utvendig_ny_kledning",
                "quantity": 80,
                "unit": "m²"
            },
            {
                "name": "Ny kledning 60m²",
                "service": "utvendig_kledning_trepanel_utskifting",
                "quantity": 60,
                "unit": "m²"
            },
            {
                "name": "Takvindu montering 2 stk",
                "service": "takvindu_velux_montering",
                "quantity": 2,
                "unit": "stk"
            },
            {
                "name": "Komplett tak pakke 120m²",
                "service": "komplett_tak_120m2_pakke",
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
        
        # Compare different roofing materials
        print(f"\n🏠 ROOFING MATERIAL COMPARISON (per m²):")
        print("=" * 45)
        
        roofing_types = [
            ("takshingel_papp_legging", "Takshingel/papp"),
            ("takstein_legging", "Takstein (betong/tegl)"),
            ("skifer_legging_premium", "Skifer (premium)")
        ]
        
        try:
            print("Roofing material costs (legging only):")
            for service_name, display_name in roofing_types:
                result = pricing_service.get_service_price(service_name)
                if "error" not in result:
                    unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                    min_price = result.get("unit_price", {}).get("min_price", 0)
                    max_price = result.get("unit_price", {}).get("max_price", 0)
                    print(f"   {display_name}: {min_price:,.0f}-{max_price:,.0f} NOK/m² (snitt: {unit_price:,.0f})")
        
        except Exception as e:
            print(f"   ❌ Error comparing roofing types: {str(e)}")
        
        # Compare cladding options
        print(f"\n🏠 CLADDING MATERIAL COMPARISON:")
        print("=" * 35)
        
        try:
            standard_result = pricing_service.get_service_price("kledning_gran_furu_standard")
            premium_result = pricing_service.get_service_price("kledning_eksklusive_tresorter")
            
            if "error" not in standard_result and "error" not in premium_result:
                standard_price = standard_result.get("unit_price", {}).get("recommended_price", 0)
                premium_price = premium_result.get("unit_price", {}).get("recommended_price", 0)
                
                premium_increase = premium_price - standard_price
                increase_percent = (premium_increase / standard_price) * 100 if standard_price > 0 else 0
                
                print(f"Standard gran/furu: {standard_price:,.0f} NOK/m²")
                print(f"Eksklusive tresorter: {premium_price:,.0f} NOK/m²")
                print(f"Premium tillegg: {premium_increase:,.0f} NOK/m² ({increase_percent:.1f}%)")
        
        except Exception as e:
            print(f"   ❌ Error comparing cladding: {str(e)}")
        
        # Complete roof renovation project
        print(f"\n🏠 COMPLETE ROOF RENOVATION (120m² house):")
        print("=" * 50)
        
        try:
            # Calculate complete roof renovation
            components = [
                ("takomlegging_nytt_tak_komplett", 120, "Complete roof replacement"),
                ("takrenner_nedlop_nye", 50, "New gutters 50m"),
                ("takvindu_velux_montering", 2, "2 roof windows"),
                ("stillas_utleie_takarbeid", 120, "Scaffolding")
            ]
            
            total_roof_cost = 0
            print("Complete roof renovation (120m² house):")
            
            for service_name, quantity, description in components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_roof_cost += cost
                    print(f"   {description}: {cost:,.0f} NOK")
                else:
                    print(f"   {description}: Error getting price")
            
            total_inc_vat = total_roof_cost * 1.25
            cost_per_m2 = total_roof_cost / 120
            
            print(f"\n   📊 Total roof cost: {total_roof_cost:,.0f} NOK eks. mva")
            print(f"   📊 Total incl. VAT: {total_inc_vat:,.0f} NOK")
            print(f"   📐 Cost per m²: {cost_per_m2:,.0f} NOK/m²")
            
            # Compare with package
            package_result = pricing_service.get_service_price("komplett_tak_120m2_pakke")
            if "error" not in package_result:
                package_cost = package_result.get("unit_price", {}).get("recommended_price", 0)
                savings = total_roof_cost - package_cost
                savings_percent = (savings / total_roof_cost) * 100 if total_roof_cost > 0 else 0
                
                print(f"\n   📦 Package alternative: {package_cost:,.0f} NOK")
                if savings > 0:
                    print(f"   💰 Package savings: {savings:,.0f} NOK ({savings_percent:.1f}%)")
                else:
                    print(f"   💰 Package premium: {abs(savings):,.0f} NOK ({abs(savings_percent):.1f}%)")
        
        except Exception as e:
            print(f"   ❌ Error calculating roof renovation: {str(e)}")
        
        print(f"\n🎉 Tak og ytterkledning pricing database updated!")
        print(f"📈 Comprehensive Oslo/Viken market data for spring 2025")
        print(f"🏠 Covers: tak, ytterkledning, etterisolering, takrenner")
        print(f"🔧 Includes: material options from budget to premium")
        print(f"💡 Key insight: Material choice greatly affects total project cost")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_tak_ytterkledning_pricing()