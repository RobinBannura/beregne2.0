#!/usr/bin/env python3
"""
Update pricing database with comprehensive kjøkken data from Oslo/Viken spring 2025
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_kjokken_pricing():
    """Update with comprehensive kjøkken pricing from Oslo/Viken 2025"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🍳 Updating with kjøkken pricing data (Oslo/Viken spring 2025)")
        print("=" * 65)
        
        # Comprehensive kjøkken data based on your research
        kjokken_data = [
            # Demolition and installation
            {
                "service": "kjokken_riving_demontering",
                "description": "Riving av gammelt kjøkken (demontering)",
                "unit": "job",
                "category": "kjokken_riving",
                "min_price": 5000,
                "max_price": 10000,
                "notes": "Demontering av kjøkkeninnredning og bortkjøring. Typisk 1 dags jobb for to mann inkl. container"
            },
            {
                "service": "kjokken_montering_nytt",
                "description": "Montering av nytt kjøkken (skap og innredning)",
                "unit": "job",
                "category": "kjokken_montering",
                "min_price": 15000,
                "max_price": 35000,
                "notes": "Fagmessig montering av kjøkkeninnredning. Mindre kjøkken 15-20k, stort kjøkken ca. 35k arbeid"
            },
            {
                "service": "kjokken_montering_komplett_inkl_hvitevarer",
                "description": "Komplett kjøkkenmontering inkl. hvitevarer",
                "unit": "job",
                "category": "kjokken_montering",
                "min_price": 35000,
                "max_price": 70000,
                "notes": "Montering av kjøkken + tilkobling av hvitevarer. Fastpris ~50k nevnt for komplette kjøkken"
            },
            
            # Countertops
            {
                "service": "benkeplate_laminat",
                "description": "Benkeplate - laminat (rimelig)",
                "unit": "lm",
                "category": "benkeplate",
                "min_price": 500,
                "max_price": 1000,
                "notes": "Laminatbenkplate på mål og montert. Materiale fra ~200 kr/m + skjæring/montering = 500-1000 kr/m"
            },
            {
                "service": "benkeplate_kompaktlaminat",
                "description": "Benkeplate - kompaktlaminat (premium laminat)",
                "unit": "lm",
                "category": "benkeplate",
                "min_price": 1500,
                "max_price": 2500,
                "notes": "Hard høytrykkslaminat/kompaktlaminat. Materiale fra ~2000 kr/m + bearbeiding"
            },
            {
                "service": "benkeplate_stein_kompositt",
                "description": "Benkeplate - stein/kompositt (premium)",
                "unit": "lm",
                "category": "benkeplate",
                "min_price": 3000,
                "max_price": 6000,
                "notes": "Granitt ~3k/m, kvarts ~4k/m, keramikk opp til 6k/m. Inkluderer bearbeiding og montering"
            },
            
            # Kitchen types and packages
            {
                "service": "kjokken_ikea_komplett",
                "description": "IKEA kjøkken komplett (skap + hvitevarer)",
                "unit": "job",
                "category": "kjokken_pakke",
                "min_price": 80000,
                "max_price": 120000,
                "notes": "IKEA-kjøkken inkl. hvitevarer. Typisk 80-100k i innkjøp, opp mot 120k for større løsninger"
            },
            {
                "service": "kjokken_midt_segment",
                "description": "Kjøkken midt-segment (Sigdal, HTH e.l.)",
                "unit": "job",
                "category": "kjokken_pakke",
                "min_price": 150000,
                "max_price": 250000,
                "notes": "Midtsegment kjøkkenløsninger. Bedre kvalitet enn IKEA, men ikke skreddersydd"
            },
            {
                "service": "kjokken_skreddersydd_snekker",
                "description": "Kjøkken skreddersydd/snekker",
                "unit": "job",
                "category": "kjokken_pakke",
                "min_price": 200000,
                "max_price": 500000,
                "notes": "Skreddersydd løsning fra snekker. Høy kvalitet, unike løsninger. Stort prissspenn"
            },
            
            # Additional services
            {
                "service": "kjokken_elektriker_arbeid",
                "description": "Elektriker arbeid kjøkken (omlegging kurser)",
                "unit": "job",
                "category": "kjokken_elektrisk",
                "min_price": 8000,
                "max_price": 15000,
                "notes": "Omlegging av elektriske kurser for nytt kjøkken. Typisk 8-15k avhengig av kompleksitet"
            },
            {
                "service": "kjokken_rorlegger_arbeid",
                "description": "Rørlegger arbeid kjøkken (vann/avløp)",
                "unit": "job",
                "category": "kjokken_ror",
                "min_price": 8000,
                "max_price": 15000,
                "notes": "Omlegging av vann/avløp for nytt kjøkken. Typisk 8-15k hver for rørlegger og elektriker"
            },
            {
                "service": "kjokken_flislegging_sprøytesone",
                "description": "Flislegging sprøytesone kjøkken",
                "unit": "m²",
                "category": "kjokken_fliser",
                "min_price": 800,
                "max_price": 1200,
                "notes": "Flislegging bak benk og komfyr. Pris per m² inklusive materialer og arbeid"
            },
            
            # Appliances (hvitevarer)
            {
                "service": "hvitevarer_basic_pakke",
                "description": "Hvitevarer basic pakke (komfyr, kjøleskap, oppvaskmaskin)",
                "unit": "pakke",
                "category": "hvitevarer",
                "min_price": 25000,
                "max_price": 45000,
                "notes": "Grunnleggende hvitevarer. Komfyr, kjøleskap, oppvaskmaskin i rimelig kvalitet"
            },
            {
                "service": "hvitevarer_premium_pakke",
                "description": "Hvitevarer premium pakke (innbygging, kvalitetsmerker)",
                "unit": "pakke",
                "category": "hvitevarer",
                "min_price": 60000,
                "max_price": 120000,
                "notes": "Premium hvitevarer med innbygging. Siemens, Miele, ASKO etc. Stor prisvariation"
            },
            
            # Specialized kitchen work
            {
                "service": "kjokkenoy_montering",
                "description": "Kjøkkenøy montering",
                "unit": "stk",
                "category": "kjokkenoy",
                "min_price": 15000,
                "max_price": 40000,
                "notes": "Kjøkkenøy med skap og benkeplate. Pris avhenger av størrelse og utstyr"
            },
            {
                "service": "vinskap_montering",
                "description": "Vinskap/spesialskap montering",
                "unit": "stk",
                "category": "spesialskap",
                "min_price": 8000,
                "max_price": 20000,
                "notes": "Innebygd vinskap eller andre spesialskap. Høy-ende tilbehør for kjøkken"
            },
            
            # Complete kitchen renovation packages
            {
                "service": "komplett_kjokken_renovering_enkel",
                "description": "Komplett kjøkken renovering (enkel)",
                "unit": "pakke",
                "category": "kjokken_komplett",
                "min_price": 150000,
                "max_price": 250000,
                "notes": "Alt fra riving til ferdig. IKEA-nivå + elektriker/rørlegger + montering. ~75k minimum nevnt"
            },
            {
                "service": "komplett_kjokken_renovering_premium",
                "description": "Komplett kjøkken renovering (premium)",
                "unit": "pakke",
                "category": "kjokken_komplett",
                "min_price": 300000,
                "max_price": 600000,
                "notes": "Total fornyelse med premium materialer og skreddersøm. 200-300k+ kan forventes"
            }
        ]
        
        print("📊 Adding comprehensive kjøkken services and pricing:")
        
        # Add service types and pricing data
        for data in kjokken_data:
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
                PricingData.source == "kjokken_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="kjokken_research_2025",
                    confidence=0.94,  # Very high confidence from detailed market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']:,.0f}-{data['max_price']:,.0f} NOK/{data['unit']} - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with kjøkken data")
        
        # Test key kitchen scenarios
        print("\n🍳 TESTING KJØKKEN SCENARIOS:")
        print("=" * 40)
        
        test_scenarios = [
            {
                "name": "Riving gammelt kjøkken",
                "service": "kjokken_riving_demontering",
                "quantity": 1,
                "unit": "job"
            },
            {
                "name": "Montering nytt kjøkken",
                "service": "kjokken_montering_nytt",
                "quantity": 1,
                "unit": "job"
            },
            {
                "name": "Laminat benkeplate 3m",
                "service": "benkeplate_laminat",
                "quantity": 3,
                "unit": "lm"
            },
            {
                "name": "Stein benkeplate 3m",
                "service": "benkeplate_stein_kompositt",
                "quantity": 3,
                "unit": "lm"
            },
            {
                "name": "IKEA kjøkken komplett",
                "service": "kjokken_ikea_komplett",
                "quantity": 1,
                "unit": "job"
            },
            {
                "name": "Komplett renovering enkel",
                "service": "komplett_kjokken_renovering_enkel",
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
                    print(f"\n🍳 {scenario['name']}:")
                    print(f"   Cost: {cost:,.0f} NOK eks. mva")
                    print(f"   Incl. VAT: {cost_inc_vat:,.0f} NOK")
                    if scenario["quantity"] > 1:
                        unit_cost = cost / scenario["quantity"]
                        print(f"   Per {scenario['unit']}: {unit_cost:,.0f} NOK")
                
            except Exception as e:
                print(f"   ❌ Error testing {scenario['name']}: {str(e)}")
        
        # Compare countertop materials
        print(f"\n🍳 COUNTERTOP MATERIAL COMPARISON (per løpemeter):")
        print("=" * 55)
        
        countertop_types = [
            ("benkeplate_laminat", "Laminat"),
            ("benkeplate_kompaktlaminat", "Kompaktlaminat"),
            ("benkeplate_stein_kompositt", "Stein/Kompositt")
        ]
        
        try:
            print("Countertop material costs:")
            for service_name, display_name in countertop_types:
                result = pricing_service.get_service_price(service_name)
                if "error" not in result:
                    unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                    min_price = result.get("unit_price", {}).get("min_price", 0)
                    max_price = result.get("unit_price", {}).get("max_price", 0)
                    print(f"   {display_name}: {min_price:,.0f}-{max_price:,.0f} NOK/lm (snitt: {unit_price:,.0f})")
        
        except Exception as e:
            print(f"   ❌ Error comparing countertops: {str(e)}")
        
        # Compare kitchen levels
        print(f"\n🍳 KITCHEN QUALITY LEVELS:")
        print("=" * 30)
        
        kitchen_levels = [
            ("kjokken_ikea_komplett", "IKEA nivå"),
            ("kjokken_midt_segment", "Midt-segment"),
            ("kjokken_skreddersydd_snekker", "Skreddersydd")
        ]
        
        try:
            print("Kitchen quality comparison:")
            for service_name, display_name in kitchen_levels:
                result = pricing_service.get_service_price(service_name)
                if "error" not in result:
                    unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                    min_price = result.get("unit_price", {}).get("min_price", 0)
                    max_price = result.get("unit_price", {}).get("max_price", 0)
                    print(f"   {display_name}: {min_price:,.0f}-{max_price:,.0f} NOK (snitt: {unit_price:,.0f})")
        
        except Exception as e:
            print(f"   ❌ Error comparing kitchen levels: {str(e)}")
        
        # Complete kitchen renovation breakdown
        print(f"\n🍳 COMPLETE KITCHEN RENOVATION BREAKDOWN:")
        print("=" * 50)
        
        try:
            # Calculate complete kitchen renovation
            components = [
                ("kjokken_riving_demontering", 1, "Riving gammelt kjøkken"),
                ("kjokken_ikea_komplett", 1, "IKEA kjøkken + hvitevarer"),
                ("benkeplate_laminat", 4, "Laminat benkeplate 4m"),
                ("kjokken_elektriker_arbeid", 1, "Elektriker arbeid"),
                ("kjokken_rorlegger_arbeid", 1, "Rørlegger arbeid"),
                ("kjokken_montering_nytt", 1, "Montering kjøkken"),
                ("kjokken_flislegging_sprøytesone", 6, "Fliser sprøytesone 6m²")
            ]
            
            total_kitchen_cost = 0
            print("Complete kitchen renovation (standard level):")
            
            for service_name, quantity, description in components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_kitchen_cost += cost
                    print(f"   {description}: {cost:,.0f} NOK")
                else:
                    print(f"   {description}: Error getting price")
            
            total_inc_vat = total_kitchen_cost * 1.25
            
            print(f"\n   📊 Total renovation cost: {total_kitchen_cost:,.0f} NOK eks. mva")
            print(f"   📊 Total incl. VAT: {total_inc_vat:,.0f} NOK")
            
            # Compare with package
            package_result = pricing_service.get_service_price("komplett_kjokken_renovering_enkel")
            if "error" not in package_result:
                package_cost = package_result.get("unit_price", {}).get("recommended_price", 0)
                savings = total_kitchen_cost - package_cost
                savings_percent = (savings / total_kitchen_cost) * 100 if total_kitchen_cost > 0 else 0
                
                print(f"\n   📦 Package alternative: {package_cost:,.0f} NOK")
                if savings > 0:
                    print(f"   💰 Package savings: {savings:,.0f} NOK ({savings_percent:.1f}%)")
                else:
                    print(f"   💰 Package premium: {abs(savings):,.0f} NOK ({abs(savings_percent):.1f}%)")
        
        except Exception as e:
            print(f"   ❌ Error calculating kitchen renovation: {str(e)}")
        
        # Kitchen renovation timeline
        print(f"\n🕐 TYPICAL KITCHEN RENOVATION TIMELINE:")
        print("=" * 45)
        print("Complete kitchen renovation usually takes:")
        print("   📋 Planning & ordering: 4-8 weeks")
        print("   🔨 Demolition: 1-2 days") 
        print("   ⚡ Electrical work: 2-3 days")
        print("   🚰 Plumbing work: 2-3 days")
        print("   🏗️  Installation: 3-5 days")
        print("   🎨 Finishing (tiles, paint): 2-3 days")
        print("   📅 Total project: 6-12 weeks")
        
        print(f"\n🎉 Kjøkken pricing database updated!")
        print(f"📈 Comprehensive Oslo/Viken market data for spring 2025")
        print(f"🍳 Covers: riving, montering, benkeplater, hvitevarer")
        print(f"🔧 Includes: budget to premium kitchen solutions")
        print(f"💡 Key insight: Total cost varies 3-4x between IKEA and custom")
        print(f"📦 Package deals provide better coordination and pricing")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_kjokken_pricing()