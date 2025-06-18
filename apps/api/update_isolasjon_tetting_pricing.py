#!/usr/bin/env python3
"""
Update pricing database with comprehensive isolasjon og tetting data from Oslo/Viken spring 2025
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_isolasjon_tetting_pricing():
    """Update with comprehensive isolasjon og tetting pricing from Oslo/Viken 2025"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🏠 Updating with isolasjon og tetting pricing data (Oslo/Viken spring 2025)")
        print("=" * 75)
        
        # Comprehensive isolasjon og tetting data based on your research
        isolasjon_tetting_data = [
            # Blown insulation
            {
                "service": "blaseisolasjon_loft_20cm",
                "description": "Blåseisolasjon (loft) 20cm tykkelse",
                "unit": "m²",
                "category": "blaseisolasjon",
                "min_price": 150,
                "max_price": 200,
                "notes": "Innblåsing av mineralull/trefiberisolasjon på kaldloft. 20cm eksempel: 15k for 100m² (150 kr/m²)"
            },
            {
                "service": "blaseisolasjon_loft_30cm",
                "description": "Blåseisolasjon (loft) 30cm tykkelse",
                "unit": "m²",
                "category": "blaseisolasjon",
                "min_price": 225,
                "max_price": 300,
                "notes": "Tykkere lag øker prisen proporsjonalt. 30cm = 1.5x av 20cm pris"
            },
            {
                "service": "blaseisolasjon_loft_40cm",
                "description": "Blåseisolasjon (loft) 40cm tykkelse", 
                "unit": "m²",
                "category": "blaseisolasjon",
                "min_price": 300,
                "max_price": 400,
                "notes": "Maksimal tykkelse for best energieffekt. 40cm = 2x av 20cm grunnpris"
            },
            
            # Vapor barrier
            {
                "service": "dampsperre_montering",
                "description": "Dampsperre (plast) - montering",
                "unit": "m²",
                "category": "dampsperre",
                "min_price": 50,
                "max_price": 100,
                "notes": "Montering av PE-dampsperre på varm side av isolasjon. Krever nøyaktig utførelse og taping"
            },
            
            # Thermal bridge breaking
            {
                "service": "kuldebrobrytere_balkong",
                "description": "Kuldebrobrytere (termisk brudd balkong)",
                "unit": "stk",
                "category": "kuldebrobrytere",
                "min_price": 5000,
                "max_price": 15000,
                "notes": "Isolerte balkongfester (Isokorb o.l.). Kostbare spesialelementer, pris avhenger av dimensjon"
            },
            {
                "service": "kuldebrobrytere_sma_punkter",
                "description": "Kuldebrobrytere (små punkter)",
                "unit": "job",
                "category": "kuldebrobrytere",
                "min_price": 2000,
                "max_price": 5000,
                "notes": "Isolasjonsbrikker, ekspanderende skum i småpunkter. Beskjeden materialkostnad"
            },
            
            # Wall insulation
            {
                "service": "vegg_isolasjon_10cm_innvendig",
                "description": "Veggisolasjon 10cm innvendig",
                "unit": "m²",
                "category": "veggisolasjon",
                "min_price": 400,
                "max_price": 700,
                "notes": "Innvendig isolasjon av yttervegger. Inkluderer dampsperre og ny gips"
            },
            {
                "service": "vegg_isolasjon_15cm_innvendig",
                "description": "Veggisolasjon 15cm innvendig",
                "unit": "m²",
                "category": "veggisolasjon",
                "min_price": 500,
                "max_price": 850,
                "notes": "Tykkere isolasjon gir bedre energieffekt men tar mer innvendig plass"
            },
            
            # Air sealing and draft proofing
            {
                "service": "lufttetting_generell",
                "description": "Lufttetting generell (fuging vinduer/dører)",
                "unit": "time",
                "category": "lufttetting",
                "min_price": 600,
                "max_price": 800,
                "notes": "Timepris for tetting av luftlekkasjer. Fuging rundt vinduer, dører, gjennomføringer"
            },
            {
                "service": "lufttetting_komplett_hus",
                "description": "Lufttetting komplett hus",
                "unit": "job",
                "category": "lufttetting",
                "min_price": 15000,
                "max_price": 35000,
                "notes": "Komplett lufttetting av enebolig. Inkluderer blower door test og systematisk tetting"
            },
            
            # Foundation insulation
            {
                "service": "grunnmur_isolasjon_utvendig",
                "description": "Grunnmur isolasjon utvendig (perimeter)",
                "unit": "m²",
                "category": "grunnmur_isolasjon",
                "min_price": 300,
                "max_price": 500,
                "notes": "Isolasjon av grunnmur utvendig. Krever graving og vanntetting"
            },
            {
                "service": "kjeller_isolasjon_innvendig",
                "description": "Kjeller isolasjon innvendig",
                "unit": "m²",
                "category": "kjeller_isolasjon",
                "min_price": 250,
                "max_price": 450,
                "notes": "Innvendig isolasjon av kjellervegger. Enklere tilkomst enn utvendig"
            },
            
            # Specialized insulation
            {
                "service": "lyddemping_vegg",
                "description": "Lyddemping vegg (spesial isolasjon)",
                "unit": "m²",
                "category": "lydisolasjon",
                "min_price": 400,
                "max_price": 800,
                "notes": "Spesial lydisolasjon mellom rom. Krever kvalitetsmaterialer og nøyaktig utførelse"
            },
            {
                "service": "brannisolasjon",
                "description": "Brannisolasjon (spesial)",
                "unit": "m²",
                "category": "brannisolasjon",
                "min_price": 300,
                "max_price": 600,
                "notes": "Brannisolasjon rundt ildsted, skorstein eller andre varmekilder"
            },
            
            # Package deals
            {
                "service": "komplett_loft_isolasjon_100m2",
                "description": "Komplett loft isolasjon 100m² (pakkeløsning)",
                "unit": "pakke",
                "category": "isolasjon_pakke",
                "min_price": 25000,
                "max_price": 40000,
                "notes": "Komplett løsning: blåseisolasjon 30cm + dampsperre + eventuell lufttetting"
            },
            {
                "service": "komplett_energioppgradering_hus",
                "description": "Komplett energioppgradering hus (pakkeløsning)",
                "unit": "pakke",
                "category": "energioppgradering",
                "min_price": 150000,
                "max_price": 300000,
                "notes": "Total energioppgradering: loft, vegger, kjeller, lufttetting. Kvalifiserer for Enova-støtte"
            },
            
            # Hourly rates for insulation work
            {
                "service": "isolator_timepris",
                "description": "Isolatør timepris",
                "unit": "time",
                "category": "timearbeid",
                "min_price": 550,
                "max_price": 750,
                "notes": "Spesialist på isolasjonsarbeid. Noe lavere enn tømrer/elektriker"
            }
        ]
        
        print("📊 Adding comprehensive isolasjon og tetting services and pricing:")
        
        # Add service types and pricing data
        for data in isolasjon_tetting_data:
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
                PricingData.source == "isolasjon_tetting_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="isolasjon_tetting_research_2025",
                    confidence=0.89,  # High confidence from detailed market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']:,.0f}-{data['max_price']:,.0f} NOK/{data['unit']} - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with isolasjon og tetting data")
        
        # Test key insulation scenarios
        print("\n🏠 TESTING ISOLASJON OG TETTING SCENARIOS:")
        print("=" * 55)
        
        test_scenarios = [
            {
                "name": "Blåseisolasjon loft 80m² (30cm)",
                "service": "blaseisolasjon_loft_30cm",
                "quantity": 80,
                "unit": "m²"
            },
            {
                "name": "Dampsperre 60m²",
                "service": "dampsperre_montering",
                "quantity": 60,
                "unit": "m²"
            },
            {
                "name": "Veggisolasjon innvendig 40m²",
                "service": "vegg_isolasjon_10cm_innvendig",
                "quantity": 40,
                "unit": "m²"
            },
            {
                "name": "Lufttetting komplett hus",
                "service": "lufttetting_komplett_hus",
                "quantity": 1,
                "unit": "job"
            },
            {
                "name": "Isolatør 12 timer",
                "service": "isolator_timepris",
                "quantity": 12,
                "unit": "timer"
            },
            {
                "name": "Komplett loft isolasjon pakke",
                "service": "komplett_loft_isolasjon_100m2",
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
        
        # Compare insulation thickness options
        print(f"\n🏠 INSULATION THICKNESS COMPARISON (loft, per m²):")
        print("=" * 55)
        
        thickness_options = [
            ("blaseisolasjon_loft_20cm", "20cm (minimum)"),
            ("blaseisolasjon_loft_30cm", "30cm (anbefalt)"),
            ("blaseisolasjon_loft_40cm", "40cm (premium)")
        ]
        
        try:
            print("Insulation thickness costs:")
            for service_name, display_name in thickness_options:
                result = pricing_service.get_service_price(service_name)
                if "error" not in result:
                    unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                    min_price = result.get("unit_price", {}).get("min_price", 0)
                    max_price = result.get("unit_price", {}).get("max_price", 0)
                    print(f"   {display_name}: {min_price:,.0f}-{max_price:,.0f} NOK/m² (snitt: {unit_price:,.0f})")
        
        except Exception as e:
            print(f"   ❌ Error comparing thickness options: {str(e)}")
        
        # Energy upgrade project calculation
        print(f"\n🏠 COMPLETE ENERGY UPGRADE (150m² house):")
        print("=" * 50)
        
        try:
            # Calculate complete energy upgrade
            components = [
                ("blaseisolasjon_loft_30cm", 100, "Loft insulation 100m²"),
                ("vegg_isolasjon_10cm_innvendig", 80, "Wall insulation 80m²"),
                ("kjeller_isolasjon_innvendig", 60, "Basement insulation 60m²"),
                ("lufttetting_komplett_hus", 1, "Complete air sealing"),
                ("dampsperre_montering", 80, "Vapor barrier 80m²")
            ]
            
            total_energy_cost = 0
            print("Complete energy upgrade (150m² house):")
            
            for service_name, quantity, description in components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_energy_cost += cost
                    print(f"   {description}: {cost:,.0f} NOK")
                else:
                    print(f"   {description}: Error getting price")
            
            total_inc_vat = total_energy_cost * 1.25
            cost_per_m2 = total_energy_cost / 150
            
            print(f"\n   📊 Total energy upgrade: {total_energy_cost:,.0f} NOK eks. mva")
            print(f"   📊 Total incl. VAT: {total_inc_vat:,.0f} NOK")
            print(f"   📐 Cost per m²: {cost_per_m2:,.0f} NOK/m²")
            
            # Compare with package
            package_result = pricing_service.get_service_price("komplett_energioppgradering_hus")
            if "error" not in package_result:
                package_cost = package_result.get("unit_price", {}).get("recommended_price", 0)
                savings = total_energy_cost - package_cost
                savings_percent = (savings / total_energy_cost) * 100 if total_energy_cost > 0 else 0
                
                print(f"\n   📦 Package alternative: {package_cost:,.0f} NOK")
                if savings > 0:
                    print(f"   💰 Package savings: {savings:,.0f} NOK ({savings_percent:.1f}%)")
                else:
                    print(f"   💰 Package premium: {abs(savings):,.0f} NOK ({abs(savings_percent):.1f}%)")
                    
                # Show potential Enova support
                enova_support = min(package_cost * 0.25, 50000)  # Up to 25%, max 50k
                net_cost = package_cost - enova_support
                print(f"   🏛️  Potential Enova support: -{enova_support:,.0f} NOK")
                print(f"   💰 Net cost after support: {net_cost:,.0f} NOK")
        
        except Exception as e:
            print(f"   ❌ Error calculating energy upgrade: {str(e)}")
        
        print(f"\n🎉 Isolasjon og tetting pricing database updated!")
        print(f"📈 Comprehensive Oslo/Viken market data for spring 2025")
        print(f"🏠 Covers: blåseisolasjon, dampsperre, lufttetting, veggisolasjon")
        print(f"🔧 Includes: both individual services and complete packages")
        print(f"💡 Key insight: Energy upgrades qualify for Enova support up to 50k NOK")
        print(f"⚡ Energy savings: 20-40% heating cost reduction typical")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_isolasjon_tetting_pricing()