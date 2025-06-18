#!/usr/bin/env python3
"""
Update pricing database with comprehensive groundwork data from Oslo/Viken spring 2025
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_grunnarbeider_pricing():
    """Update with comprehensive groundwork pricing from Oslo/Viken 2025"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🏗️ Updating with groundwork pricing data (Oslo/Viken spring 2025)")
        print("=" * 70)
        
        # Comprehensive groundwork data based on your research
        grunnarbeider_data = [
            # Basic excavation and earthwork
            {
                "service": "graving_generell_utgraving",
                "description": "Graving – generell utgraving av tomt",
                "unit": "m²",
                "category": "graving",
                "min_price": 1500,
                "max_price": 3000,
                "notes": "Standard utgraving av tomt, varierer med grunnforhold"
            },
            {
                "service": "graving_ny_bolig_inkl_planering",
                "description": "Graving for ny bolig/hytte (inkl. planering)",
                "unit": "m²",
                "category": "graving",
                "min_price": 2500,
                "max_price": 12000,
                "notes": "Kompleks graving med planering, høy variasjon pga grunnforhold"
            },
            {
                "service": "gravemaskin_med_forer",
                "description": "Gravemaskin m/fører",
                "unit": "time",
                "category": "maskinleie",
                "min_price": 1000,
                "max_price": 2000,
                "notes": "Timepris gravemaskin med operatør"
            },
            {
                "service": "bortkjoring_masser",
                "description": "Bortkjøring av masser",
                "unit": "m³",
                "category": "transport",
                "min_price": 120,
                "max_price": 180,
                "notes": "1-1,5 kr/kg ≈ 120-180 kr/m³ jord"
            },
            
            # Foundation and concrete work
            {
                "service": "grunnmur_betong_leca",
                "description": "Grunnmur (betong/Leca)",
                "unit": "m²",
                "category": "grunnmur",
                "min_price": 1500,
                "max_price": 5000,
                "notes": "Snitt ≈ 2500 kr/m² grunnflate"
            },
            {
                "service": "plate_pa_mark",
                "description": "Plate på mark (betongplate inkl. isolasjon & radonsperre)",
                "unit": "m²",
                "category": "betong",
                "min_price": 1100,
                "max_price": 2200,
                "notes": "Komplett plate løsning med isolasjon"
            },
            {
                "service": "drenering_rundt_grunnmur",
                "description": "Drenering rundt grunnmur",
                "unit": "lm",
                "category": "drenering",
                "min_price": 4500,
                "max_price": 9000,
                "notes": "Per løpemeter rundt bygning"
            },
            
            # Rock blasting and removal
            {
                "service": "sprengning_fjell_store_volumer",
                "description": "Sprengning av fjell (store volumer)",
                "unit": "m³",
                "category": "sprengning",
                "min_price": 200,
                "max_price": 300,
                "notes": "Store volumer, effektiv sprengning"
            },
            {
                "service": "sprengning_fjell_sma_kompliserte",
                "description": "Sprengning av fjell (små/kompliserte jobber)",
                "unit": "m³",
                "category": "sprengning",
                "min_price": 4000,
                "max_price": 5000,
                "notes": "Små/kompliserte jobber, høy enhetspris"
            },
            {
                "service": "fjerning_sprengt_fjell",
                "description": "Fjerning / bortkjøring sprengt fjell",
                "unit": "m³",
                "category": "transport",
                "min_price": 100,
                "max_price": 140,
                "notes": "ca. 120 kr/m³ (opplasting + transport)"
            },
            
            # Complementary services
            {
                "service": "radonsperre_i_plate",
                "description": "Radonsperre i plate",
                "unit": "m²",
                "category": "isolasjon",
                "min_price": 250,
                "max_price": 350,
                "notes": "Spesiell radonmembran under plate"
            },
            {
                "service": "tele_frostsikring_under_sale",
                "description": "Tele-/frostsikring under såle",
                "unit": "m²",
                "category": "isolasjon",
                "min_price": 150,
                "max_price": 300,
                "notes": "Isolasjon mot teleløfting"
            },
            {
                "service": "perimeter_isolasjon_grunnmur",
                "description": "Perimeter-isolasjon grunnmur",
                "unit": "lm",
                "category": "isolasjon",
                "min_price": 150,
                "max_price": 250,
                "notes": "Isolasjon langs grunnmur utvendig"
            },
            
            # Package deals for common scenarios
            {
                "service": "komplett_grunnmur_pakke_120m2",
                "description": "Komplett grunnmur 120m² (pakkeløsning)",
                "unit": "pakke",
                "category": "grunnmur_pakke",
                "min_price": 280000,
                "max_price": 420000,
                "notes": "Graving + grunnmur + drenering for 120m² bolig"
            },
            {
                "service": "komplett_plate_fundamentering_100m2",
                "description": "Komplett plate fundamentering 100m² (pakkeløsning)",
                "unit": "pakke",
                "category": "betong_pakke",
                "min_price": 180000,
                "max_price": 300000,
                "notes": "Graving + plate + isolasjon + radonsperre for 100m²"
            }
        ]
        
        print("📊 Adding comprehensive groundwork services and pricing:")
        
        # Add service types and pricing data
        for data in grunnarbeider_data:
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
                PricingData.source == "grunnarbeider_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="grunnarbeider_research_2025",
                    confidence=0.90,  # High confidence from detailed market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']:,.0f}-{data['max_price']:,.0f} NOK/{data['unit']} - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with groundwork data")
        
        # Test key groundwork scenarios
        print("\n🏗️ TESTING GROUNDWORK SCENARIOS:")
        print("=" * 50)
        
        test_scenarios = [
            {
                "name": "Standard tomt graving 200m²",
                "service": "graving_generell_utgraving",
                "quantity": 200,
                "unit": "m²"
            },
            {
                "name": "Gravemaskin 8 timer",
                "service": "gravemaskin_med_forer",
                "quantity": 8,
                "unit": "timer"
            },
            {
                "name": "Grunnmur 120m² bolig",
                "service": "grunnmur_betong_leca",
                "quantity": 120,
                "unit": "m²"
            },
            {
                "name": "Plate på mark 100m²",
                "service": "plate_pa_mark",
                "quantity": 100,
                "unit": "m²"
            },
            {
                "name": "Drenering 40 løpemeter",
                "service": "drenering_rundt_grunnmur",
                "quantity": 40,
                "unit": "lm"
            },
            {
                "name": "Fjellsprengning 50m³ (stor volum)",
                "service": "sprengning_fjell_store_volumer",
                "quantity": 50,
                "unit": "m³"
            },
            {
                "name": "Komplett grunnmur 120m² (pakke)",
                "service": "komplett_grunnmur_pakke_120m2",
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
                    print(f"\n🏗️ {scenario['name']}:")
                    print(f"   Cost: {cost:,.0f} NOK eks. mva")
                    print(f"   Incl. VAT: {cost_inc_vat:,.0f} NOK")
                    if scenario["quantity"] > 1:
                        unit_cost = cost / scenario["quantity"]
                        print(f"   Per {scenario['unit']}: {unit_cost:,.0f} NOK")
                
            except Exception as e:
                print(f"   ❌ Error testing {scenario['name']}: {str(e)}")
        
        # Show cost breakdown for typical new house foundation
        print(f"\n🏠 TYPICAL NEW HOUSE FOUNDATION BREAKDOWN (120m²):")
        print("=" * 60)
        
        try:
            # Calculate individual components
            components = [
                ("graving_ny_bolig_inkl_planering", 120, "Graving og planering"),
                ("grunnmur_betong_leca", 120, "Grunnmur"),
                ("drenering_rundt_grunnmur", 50, "Drenering (50 lm)"),
                ("perimeter_isolasjon_grunnmur", 50, "Perimeter isolasjon")
            ]
            
            total_individual = 0
            print("Individual component pricing:")
            
            for service_name, quantity, description in components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_individual += cost
                    print(f"   {description}: {cost:,.0f} NOK")
            
            # Compare with package pricing
            package_result = pricing_service.get_service_price("komplett_grunnmur_pakke_120m2")
            if "error" not in package_result:
                package_cost = package_result.get("unit_price", {}).get("recommended_price", 0)
                
                savings = total_individual - package_cost
                savings_percent = (savings / total_individual) * 100 if total_individual > 0 else 0
                
                print(f"\n   📊 Component total: {total_individual:,.0f} NOK")
                print(f"   📦 Package price: {package_cost:,.0f} NOK")
                if savings > 0:
                    print(f"   💰 Package savings: {savings:,.0f} NOK ({savings_percent:.1f}%)")
                else:
                    print(f"   💰 Package premium: {abs(savings):,.0f} NOK ({abs(savings_percent):.1f}%)")
        
        except Exception as e:
            print(f"   ❌ Error calculating foundation breakdown: {str(e)}")
        
        # Show rock blasting cost comparison
        print(f"\n🧨 ROCK BLASTING COST COMPARISON:")
        print("=" * 40)
        
        try:
            small_result = pricing_service.get_service_price("sprengning_fjell_sma_kompliserte", area=10)
            large_result = pricing_service.get_service_price("sprengning_fjell_store_volumer", area=100)
            
            small_cost = small_result.get("total_cost", {}).get("recommended", 0)
            large_cost = large_result.get("total_cost", {}).get("recommended", 0)
            
            if small_cost > 0 and large_cost > 0:
                small_unit = small_cost / 10
                large_unit = large_cost / 100
                
                print(f"10m³ (small/complex): {small_cost:,.0f} NOK ({small_unit:,.0f} NOK/m³)")
                print(f"100m³ (large volume): {large_cost:,.0f} NOK ({large_unit:,.0f} NOK/m³)")
                print(f"Volume discount: {((small_unit - large_unit) / small_unit * 100):.1f}%")
        
        except Exception as e:
            print(f"   ❌ Error comparing blasting costs: {str(e)}")
        
        print(f"\n🎉 Groundwork pricing database updated!")
        print(f"📈 Comprehensive Oslo/Viken market data for spring 2025")
        print(f"🏗️ Covers: excavation, foundation, drainage, rock blasting")
        print(f"🔧 Key insight: Package deals often provide significant savings")
        print(f"⚠️  Large price variations due to ground conditions and access")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_grunnarbeider_pricing()