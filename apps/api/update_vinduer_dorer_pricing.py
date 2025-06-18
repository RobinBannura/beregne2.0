#!/usr/bin/env python3
"""
Update pricing database with comprehensive vinduer og dører data from Oslo/Viken spring 2025
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_vinduer_dorer_pricing():
    """Update with comprehensive vinduer og dører pricing from Oslo/Viken 2025"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🏠 Updating with vinduer og dører pricing data (Oslo/Viken spring 2025)")
        print("=" * 75)
        
        # Comprehensive vinduer og dører data based on your research
        vinduer_dorer_data = [
            # Standard windows
            {
                "service": "vindu_standard_komplett",
                "description": "Bytte vindu (standard) komplett (vindu + montering)",
                "unit": "stk",
                "category": "vinduer",
                "min_price": 7000,
                "max_price": 12000,
                "notes": "Standard vindu 120x120cm inkl. montering. PVC 3-5k + trevindu 5-8k + montering 2-4k = ~10k total"
            },
            {
                "service": "vindu_hoy_kvalitet_komplett",
                "description": "Vinduer - høyere kvalitet (3-lags, alu-bekledd)",
                "unit": "stk",
                "category": "vinduer",
                "min_price": 10000,
                "max_price": 18000,
                "notes": "Trecovinduer med 3-lags glass og alubekleding. 8.3-11.3k for 2-lags PVC, opp mot 15k for 3-lags tre/alu"
            },
            {
                "service": "vindu_montasje_kun",
                "description": "Vindu montering (kun arbeid)",
                "unit": "stk",
                "category": "vindumontasje",
                "min_price": 2000,
                "max_price": 4000,
                "notes": "Kun montering av vindu. Varierer etter størrelse, type og tilkomst (etasjer)"
            },
            
            # Window materials only
            {
                "service": "vindu_pvc_2_lags",
                "description": "PVC vindu 2-lags glass (kun materiale)",
                "unit": "stk",
                "category": "vindu_materiale",
                "min_price": 3000,
                "max_price": 5000,
                "notes": "Standard 2-lags PVC-vindu materiale. Størrelse 120x120cm typisk"
            },
            {
                "service": "vindu_tre_2_lags",
                "description": "Trevindu 2-lags glass (kun materiale)",
                "unit": "stk",
                "category": "vindu_materiale",
                "min_price": 5000,
                "max_price": 8000,
                "notes": "Trevindu 2-lags glass. Krever mer vedlikehold enn PVC"
            },
            {
                "service": "vindu_tre_alu_3_lags",
                "description": "Tre/alu vindu 3-lags glass (kun materiale)",
                "unit": "stk",
                "category": "vindu_materiale",
                "min_price": 8000,
                "max_price": 12000,
                "notes": "Premium trevindu med alubekleding og 3-lags energiglass"
            },
            
            # Specialty windows
            {
                "service": "takvindu_stort",
                "description": "Takvindu stort (Velux e.l.)",
                "unit": "stk",
                "category": "takvindu",
                "min_price": 20000,
                "max_price": 50000,
                "notes": "Store vindusflater, spesialglass eller takvinduer. Velux typisk 20-50k inkl. montering"
            },
            {
                "service": "panoramavindu_stor_flate",
                "description": "Panoramavindu/stor vindusflate",
                "unit": "stk",
                "category": "vinduer",
                "min_price": 25000,
                "max_price": 60000,
                "notes": "Store vindusflater, panoramavinduer. Pris øker med størrelse og glasskvalitet"
            },
            
            # Exterior doors
            {
                "service": "ytterdor_enkel_komplett",
                "description": "Ytterdør (ny, enkel type) komplett",
                "unit": "stk",
                "category": "ytterdor",
                "min_price": 6000,
                "max_price": 16000,
                "notes": "Vanlig ytterdør med karm 5k+ og montering 2.5-4k. Komplett 8-20k inkl. mva (6.4-16k eks. mva)"
            },
            {
                "service": "ytterdor_sikkerhet_premium",
                "description": "Ytterdør sikkerhet/premium",
                "unit": "stk",
                "category": "ytterdor",
                "min_price": 20000,
                "max_price": 40000,
                "notes": "Sikkerhetsdør, dobbeltdør med glassfelt. Betydelig dyrere enn standard"
            },
            {
                "service": "ytterdor_montasje_kun",
                "description": "Ytterdør montering (kun arbeid)",
                "unit": "stk",
                "category": "dor_montasje",
                "min_price": 2500,
                "max_price": 4000,
                "notes": "Kun montering av ytterdør. Kompleks montering pga. tetting og justering"
            },
            
            # Interior doors
            {
                "service": "innerdor_standard_komplett",
                "description": "Innerdør (standard) komplett",
                "unit": "stk",
                "category": "innerdor",
                "min_price": 2000,
                "max_price": 4000,
                "notes": "Dørblad med karm 1-2k + montering 0.5-1.5k. Standard hvit fyllingsdør ferdig montert"
            },
            {
                "service": "innerdor_massiv_premium",
                "description": "Innerdør massiv/lydisolerende",
                "unit": "stk",
                "category": "innerdor",
                "min_price": 3500,
                "max_price": 7000,
                "notes": "Massive lydisolerende dører. Dyrere materialer og ofte tyngre montering"
            },
            {
                "service": "innerdor_montasje_kun",
                "description": "Innerdør montering (kun arbeid)",
                "unit": "stk",
                "category": "dor_montasje",
                "min_price": 500,
                "max_price": 1500,
                "notes": "Kun arbeidskostnad for montering. 1-2 timers jobb per dør"
            },
            
            # Specialized glass
            {
                "service": "spesialglass_stoy_sikkerhet",
                "description": "Spesialglass (støy/sikkerhet)",
                "unit": "m²",
                "category": "spesialglass",
                "min_price": 1500,
                "max_price": 3000,
                "notes": "Støydempende eller sikkerhetsglass. Betydelig dyrere enn standard glass"
            },
            
            # Package deals
            {
                "service": "komplett_vindusutskifting_hus",
                "description": "Komplett vindusutskifting hus (12 vinduer)",
                "unit": "pakke",
                "category": "vindu_pakke",
                "min_price": 120000,
                "max_price": 200000,
                "notes": "Komplett utskifting av vinduer i enebolig. 12 vinduer x 10k = 120k, opp mot 200k for premium"
            },
            {
                "service": "komplett_dor_utskifting_hus",
                "description": "Komplett dør utskifting hus (1 ytter + 6 inner)",
                "unit": "pakke",
                "category": "dor_pakke",
                "min_price": 25000,
                "max_price": 45000,
                "notes": "1 ytterdør + 6 innerdører. Pakkerabatt på montering ved flere dører samtidig"
            }
        ]
        
        print("📊 Adding comprehensive vinduer og dører services and pricing:")
        
        # Add service types and pricing data
        for data in vinduer_dorer_data:
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
                PricingData.source == "vinduer_dorer_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="vinduer_dorer_research_2025",
                    confidence=0.92,  # High confidence from detailed market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']:,.0f}-{data['max_price']:,.0f} NOK/{data['unit']} - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with vinduer og dører data")
        
        # Test key window and door scenarios
        print("\n🏠 TESTING VINDUER OG DØRER SCENARIOS:")
        print("=" * 50)
        
        test_scenarios = [
            {
                "name": "Standard vindu utskifting 1 stk",
                "service": "vindu_standard_komplett",
                "quantity": 1,
                "unit": "stk"
            },
            {
                "name": "Premium vinduer 3 stk",
                "service": "vindu_hoy_kvalitet_komplett",
                "quantity": 3,
                "unit": "stk"
            },
            {
                "name": "Ytterdør enkel type",
                "service": "ytterdor_enkel_komplett",
                "quantity": 1,
                "unit": "stk"
            },
            {
                "name": "Innerdører standard 5 stk",
                "service": "innerdor_standard_komplett",
                "quantity": 5,
                "unit": "stk"
            },
            {
                "name": "Takvindu 2 stk",
                "service": "takvindu_stort",
                "quantity": 2,
                "unit": "stk"
            },
            {
                "name": "Komplett vindusutskifting hus",
                "service": "komplett_vindusutskifting_hus",
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
        
        # Compare window quality options
        print(f"\n🏠 WINDOW QUALITY COMPARISON:")
        print("=" * 35)
        
        window_types = [
            ("vindu_pvc_2_lags", "PVC 2-lags (materiale)"),
            ("vindu_tre_2_lags", "Tre 2-lags (materiale)"),
            ("vindu_tre_alu_3_lags", "Tre/alu 3-lags (materiale)"),
            ("vindu_standard_komplett", "Standard komplett"),
            ("vindu_hoy_kvalitet_komplett", "Premium komplett")
        ]
        
        try:
            print("Window options comparison:")
            for service_name, display_name in window_types:
                result = pricing_service.get_service_price(service_name)
                if "error" not in result:
                    unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                    min_price = result.get("unit_price", {}).get("min_price", 0)
                    max_price = result.get("unit_price", {}).get("max_price", 0)
                    print(f"   {display_name}: {min_price:,.0f}-{max_price:,.0f} NOK (snitt: {unit_price:,.0f})")
        
        except Exception as e:
            print(f"   ❌ Error comparing window types: {str(e)}")
        
        # Compare door options
        print(f"\n🏠 DOOR OPTIONS COMPARISON:")
        print("=" * 30)
        
        door_types = [
            ("innerdor_standard_komplett", "Innerdør standard"),
            ("innerdor_massiv_premium", "Innerdør massiv"),
            ("ytterdor_enkel_komplett", "Ytterdør enkel"),
            ("ytterdor_sikkerhet_premium", "Ytterdør sikkerhet")
        ]
        
        try:
            print("Door options comparison:")
            for service_name, display_name in door_types:
                result = pricing_service.get_service_price(service_name)
                if "error" not in result:
                    unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                    min_price = result.get("unit_price", {}).get("min_price", 0)
                    max_price = result.get("unit_price", {}).get("max_price", 0)
                    print(f"   {display_name}: {min_price:,.0f}-{max_price:,.0f} NOK (snitt: {unit_price:,.0f})")
        
        except Exception as e:
            print(f"   ❌ Error comparing door types: {str(e)}")
        
        # Complete window and door renovation
        print(f"\n🏠 COMPLETE WINDOW & DOOR RENOVATION:")
        print("=" * 45)
        
        try:
            # Calculate complete renovation
            components = [
                ("vindu_standard_komplett", 8, "8 standard vinduer"),
                ("ytterdor_enkel_komplett", 1, "1 ytterdør"),
                ("innerdor_standard_komplett", 6, "6 innerdører"),
                ("takvindu_stort", 2, "2 takvinduer")
            ]
            
            total_cost = 0
            print("Complete window & door renovation:")
            
            for service_name, quantity, description in components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_cost += cost
                    print(f"   {description}: {cost:,.0f} NOK")
                else:
                    print(f"   {description}: Error getting price")
            
            total_inc_vat = total_cost * 1.25
            
            print(f"\n   📊 Total renovation cost: {total_cost:,.0f} NOK eks. mva")
            print(f"   📊 Total incl. VAT: {total_inc_vat:,.0f} NOK")
            
            # Compare individual vs packages
            print(f"\n   📦 PACKAGE COMPARISON:")
            
            # Window package
            window_package = pricing_service.get_service_price("komplett_vindusutskifting_hus")
            if "error" not in window_package:
                package_cost = window_package.get("unit_price", {}).get("recommended_price", 0)
                # Individual cost for 8 windows
                individual_windows = pricing_service.get_service_price("vindu_standard_komplett", area=8)
                if "error" not in individual_windows:
                    individual_cost = individual_windows.get("total_cost", {}).get("recommended", 0)
                    # Package is for 12 windows, adjust for 8
                    adjusted_package = package_cost * (8/12)
                    savings = individual_cost - adjusted_package
                    savings_percent = (savings / individual_cost) * 100 if individual_cost > 0 else 0
                    
                    print(f"   Windows (8 stk): Individual {individual_cost:,.0f} vs Package {adjusted_package:,.0f} NOK")
                    if savings > 0:
                        print(f"   Package savings: {savings:,.0f} NOK ({savings_percent:.1f}%)")
        
        except Exception as e:
            print(f"   ❌ Error calculating renovation: {str(e)}")
        
        # Energy efficiency benefits
        print(f"\n⚡ ENERGY EFFICIENCY BENEFITS:")
        print("=" * 35)
        print("New windows typically provide:")
        print("   🔥 20-30% reduction in heating costs")
        print("   🌡️  Better indoor comfort (less drafts)")
        print("   🔇 Improved sound insulation")
        print("   🏡 Increased property value (+3-5%)")
        print("   💰 Payback period: 15-25 years")
        
        print(f"\n🎉 Vinduer og dører pricing database updated!")
        print(f"📈 Comprehensive Oslo/Viken market data for spring 2025")
        print(f"🏠 Covers: vinduer, dører, spesialglass, montering")
        print(f"🔧 Includes: standard to premium quality options")
        print(f"💡 Key insight: Quality windows provide long-term energy savings")
        print(f"📦 Package deals available for multiple window/door projects")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_vinduer_dorer_pricing()