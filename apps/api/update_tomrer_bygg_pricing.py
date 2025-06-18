#!/usr/bin/env python3
"""
Update pricing database with comprehensive tømrer/bygg data from Oslo/Viken spring 2025
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import ServiceType, PricingData

def update_tomrer_bygg_pricing():
    """Update with comprehensive tømrer/bygg pricing from Oslo/Viken 2025"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        print("🔨 Updating with tømrer/bygg pricing data (Oslo/Viken spring 2025)")
        print("=" * 70)
        
        # Comprehensive tømrer/bygg data based on your research
        tomrer_bygg_data = [
            # Lettvegg and partition walls
            {
                "service": "lettvegg_skillevegg_med_dor",
                "description": "Lett skillevegg inkl. isolasjon og dør",
                "unit": "m²",
                "category": "lettvegg",
                "min_price": 3000,
                "max_price": 5000,
                "notes": "Pris inkl. materialer (stendere, gipsplater, isolasjon) og arbeid. 30-50k for typisk lettvegg med dør"
            },
            
            # Ceiling work
            {
                "service": "nedforet_himling_gips",
                "description": "Nedforet himling (gips)",
                "unit": "m²",
                "category": "himling",
                "min_price": 500,
                "max_price": 900,
                "notes": "Montering av nedforet tak med gips. Sparkling og maling kommer i tillegg. Komplekse vinkler øker prisen"
            },
            
            # Door installation
            {
                "service": "innerdor_montering",
                "description": "Innsetting av innerdør (montering i ferdig veggåpning)",
                "unit": "stk",
                "category": "dor_montering",
                "min_price": 500,
                "max_price": 1500,
                "notes": "Kun arbeidskostnad for å montere innerdør (1-2 timers jobb). Dørblad/karm kostnader kommer i tillegg"
            },
            {
                "service": "innerdor_komplett",
                "description": "Innerdør (standard) komplett",
                "unit": "stk",
                "category": "dor_komplett",
                "min_price": 2000,
                "max_price": 4000,
                "notes": "Dørblad med karm 1000-2000 kr + montering 500-1500 kr. Standard hvit fyllingsdør ferdig montert"
            },
            
            # Window trim and molding
            {
                "service": "vindusforinger_lister",
                "description": "Vindusforinger og lister (innvendig karm/gerikt)",
                "unit": "stk",
                "category": "vindusarbeid",
                "min_price": 1500,
                "max_price": 3000,
                "notes": "Komplett foring av vindu innvendig med karmlister. Inkluderer materialer og arbeid"
            },
            
            # Structural changes
            {
                "service": "barende_konstruksjon_endring",
                "description": "Endring av bærende konstruksjon (utsparing i bærende vegg)",
                "unit": "job",
                "category": "konstruksjon",
                "min_price": 50000,
                "max_price": 150000,
                "notes": "Innebærer beregning og montering av drager/stålbjelke. Krever statiker og søknad. Pris øker med spennvidde"
            },
            
            # General carpentry hourly rate
            {
                "service": "tomrer_timepris",
                "description": "Tømrer timepris",
                "unit": "time",
                "category": "timearbeid",
                "min_price": 600,
                "max_price": 850,
                "notes": "Standard timepris for tømrerarbeid. Spesialiserte oppgaver eller Oslo sentrum kan være høyere"
            },
            
            # Gypsum board installation
            {
                "service": "gipsplater_montering_vegger",
                "description": "Montering av gipsplater (vegger)",
                "unit": "m²",
                "category": "gipsarbeid",
                "min_price": 500,
                "max_price": 700,
                "notes": "Oppsetting av gips på vegg inkl. stender/lekt hvis nødvendig. Materialer inkludert"
            },
            
            # Molding and trim work
            {
                "service": "listverk_gulv_tak",
                "description": "Listverk (montering) - gulv-/taklister",
                "unit": "lm",
                "category": "listverk",
                "min_price": 60,
                "max_price": 100,
                "notes": "Utskifting eller ny montering av lister. Enkle glatte lister ca. 60-80 kr/m, kompleks hjørneskjæring øker prisen"
            },
            
            # Package deals for typical projects
            {
                "service": "komplett_lettvegg_4m_med_dor",
                "description": "Komplett lettvegg 4m med dør (pakkeløsning)",
                "unit": "pakke",
                "category": "lettvegg_pakke",
                "min_price": 25000,
                "max_price": 40000,
                "notes": "4 meter lettvegg (2.5m høy) med standard innerdør, inkl. alle materialer og arbeid"
            },
            {
                "service": "komplett_himling_25m2",
                "description": "Komplett nedforet himling 25m² (pakkeløsning)",
                "unit": "pakke",
                "category": "himling_pakke",
                "min_price": 18000,
                "max_price": 28000,
                "notes": "Nedforet himling med gips for 25m² rom, inkl. sparkling men ekskl. maling"
            },
            
            # Specialized carpentry work
            {
                "service": "tregulv_montering",
                "description": "Tregulv montering (massivtre)",
                "unit": "m²",
                "category": "gulvarbeid",
                "min_price": 300,
                "max_price": 600,
                "notes": "Montering av massivt tregulv. Pris for arbeid, materialer kommer i tillegg. Komplekse mønstre øker prisen"
            },
            {
                "service": "innredning_skreddersydd",
                "description": "Innredning skreddersydd (bokhyller, skap)",
                "unit": "lm",
                "category": "innredning",
                "min_price": 2000,
                "max_price": 4000,
                "notes": "Skreddersydde bokhyller eller skap. Pris per løpemeter ferdig montert. Avhenger av materialer og kompleksitet"
            }
        ]
        
        print("📊 Adding comprehensive tømrer/bygg services and pricing:")
        
        # Add service types and pricing data
        for data in tomrer_bygg_data:
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
                PricingData.source == "tomrer_bygg_research_2025"
            ).first()
            
            if not existing_pricing:
                pricing_data = PricingData(
                    service_type_id=service.id,
                    min_price=data["min_price"],
                    max_price=data["max_price"],
                    avg_price=(data["min_price"] + data["max_price"]) / 2,
                    region="Oslo",
                    source="tomrer_bygg_research_2025",
                    confidence=0.93,  # High confidence from detailed market research
                    notes=data["notes"]
                )
                db.add(pricing_data)
                print(f"   💰 {data['min_price']:,.0f}-{data['max_price']:,.0f} NOK/{data['unit']} - {data['notes'][:50]}...")
        
        db.commit()
        
        # Update market rates
        pricing_service.update_market_rates("Oslo")
        print("\n✅ Market rates recalculated with tømrer/bygg data")
        
        # Test key carpentry scenarios
        print("\n🔨 TESTING TØMRER/BYGG SCENARIOS:")
        print("=" * 50)
        
        test_scenarios = [
            {
                "name": "Lettvegg 3x2.5m med dør",
                "service": "lettvegg_skillevegg_med_dor",
                "quantity": 7.5,  # 3m x 2.5m = 7.5m²
                "unit": "m²"
            },
            {
                "name": "Nedforet himling 20m²",
                "service": "nedforet_himling_gips",
                "quantity": 20,
                "unit": "m²"
            },
            {
                "name": "Montering 3 innerdører",
                "service": "innerdor_montering",
                "quantity": 3,
                "unit": "stk"
            },
            {
                "name": "Vindusforinger 2 vinduer",
                "service": "vindusforinger_lister",
                "quantity": 2,
                "unit": "stk"
            },
            {
                "name": "Tømrer 8 timer",
                "service": "tomrer_timepris",
                "quantity": 8,
                "unit": "timer"
            },
            {
                "name": "Komplett lettvegg pakke",
                "service": "komplett_lettvegg_4m_med_dor",
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
                    print(f"\n🔨 {scenario['name']}:")
                    print(f"   Cost: {cost:,.0f} NOK eks. mva")
                    print(f"   Incl. VAT: {cost_inc_vat:,.0f} NOK")
                    if scenario["quantity"] > 1:
                        unit_cost = cost / scenario["quantity"]
                        print(f"   Per {scenario['unit']}: {unit_cost:,.0f} NOK")
                
            except Exception as e:
                print(f"   ❌ Error testing {scenario['name']}: {str(e)}")
        
        # Show cost comparison for typical room renovation
        print(f"\n🏠 TYPICAL ROOM RENOVATION (3x4m rom):")
        print("=" * 45)
        
        try:
            # Calculate complete room renovation with tømrer work
            components = [
                ("lettvegg_skillevegg_med_dor", 10, "Ny lettvegg (10m²)"),
                ("nedforet_himling_gips", 12, "Nedforet himling (12m²)"),
                ("innerdor_montering", 1, "Montering 1 dør"),
                ("listverk_gulv_tak", 14, "Lister gulv/tak (14m)")
            ]
            
            total_carpentry_cost = 0
            print("Complete room renovation (tømrer work):")
            
            for service_name, quantity, description in components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_carpentry_cost += cost
                    print(f"   {description}: {cost:,.0f} NOK")
                else:
                    print(f"   {description}: Error getting price")
            
            total_inc_vat = total_carpentry_cost * 1.25
            cost_per_m2 = total_carpentry_cost / 12  # 12m² room
            
            print(f"\n   📊 Total carpentry cost: {total_carpentry_cost:,.0f} NOK eks. mva")
            print(f"   📊 Total incl. VAT: {total_inc_vat:,.0f} NOK")
            print(f"   📐 Cost per m²: {cost_per_m2:,.0f} NOK/m²")
        
        except Exception as e:
            print(f"   ❌ Error calculating room renovation: {str(e)}")
        
        # Compare package vs individual components
        print(f"\n📦 PACKAGE vs INDIVIDUAL COMPARISON:")
        print("=" * 40)
        
        try:
            # Calculate individual components for lettvegg
            individual_components = [
                ("lettvegg_skillevegg_med_dor", 10, "Lettvegg 10m²"),
                ("innerdor_komplett", 1, "Komplett innerdør")
            ]
            
            individual_total = 0
            print("Individual components (lettvegg project):")
            
            for service_name, quantity, description in individual_components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    individual_total += cost
                    print(f"   {description}: {cost:,.0f} NOK")
            
            # Compare with package
            package_result = pricing_service.get_service_price("komplett_lettvegg_4m_med_dor")
            if "error" not in package_result:
                package_cost = package_result.get("unit_price", {}).get("recommended_price", 0)
                
                # Note: Package is for 4m wall, so adjust for comparison
                adjusted_package = package_cost * 2.5  # Scale to 10m²
                
                savings = individual_total - adjusted_package
                savings_percent = (savings / individual_total) * 100 if individual_total > 0 else 0
                
                print(f"\n   📊 Individual total (10m²): {individual_total:,.0f} NOK")
                print(f"   📦 Package price (scaled): {adjusted_package:,.0f} NOK")
                if savings > 0:
                    print(f"   💰 Package savings: {savings:,.0f} NOK ({savings_percent:.1f}%)")
                else:
                    print(f"   💰 Package premium: {abs(savings):,.0f} NOK ({abs(savings_percent):.1f}%)")
        
        except Exception as e:
            print(f"   ❌ Error comparing package: {str(e)}")
        
        print(f"\n🎉 Tømrer/bygg pricing database updated!")
        print(f"📈 Comprehensive Oslo/Viken market data for spring 2025")
        print(f"🔨 Covers: lettvegg, himling, dører, vindusforinger, listverk")
        print(f"🏗️ Includes: both individual services and package deals")
        print(f"💡 Key insight: Packages often provide better value for complete projects")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_tomrer_bygg_pricing()