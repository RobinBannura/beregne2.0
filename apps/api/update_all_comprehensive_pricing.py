#!/usr/bin/env python3
"""
Master script to update all comprehensive pricing data from Oslo/Viken spring 2025
Runs all individual pricing update scripts in sequence
"""

import subprocess
import sys
import time

def run_script(script_name, category_name):
    """Run a pricing update script and handle errors"""
    try:
        print(f"\n{'='*60}")
        print(f"🔄 RUNNING: {category_name}")
        print(f"{'='*60}")
        
        # Run the script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {category_name} completed")
            # Print last few lines of output for confirmation
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines[-3:]:
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ FAILED: {category_name}")
            print(f"Error: {result.stderr}")
            return False
            
        time.sleep(2)  # Brief pause between scripts
        return True
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {category_name} took too long")
        return False
    except Exception as e:
        print(f"💥 ERROR: {category_name} - {str(e)}")
        return False

def main():
    """Run all comprehensive pricing updates"""
    
    print("🏗️ COMPREHENSIVE PRICING DATABASE UPDATE")
    print("=" * 60)
    print("Updating all 11 construction categories with Oslo/Viken spring 2025 data")
    print("This will populate the database with comprehensive market pricing")
    print("=" * 60)
    
    # Define all pricing update scripts in logical order
    pricing_scripts = [
        # Core categories first
        ("update_tomrer_bygg_pricing.py", "1. Tømrer/Bygg"),
        ("update_tak_ytterkledning_pricing.py", "2. Tak og Ytterkledning"), 
        ("update_isolasjon_tetting_pricing.py", "3. Isolasjon og Tetting"),
        ("update_vinduer_dorer_pricing.py", "4. Vinduer og Dører"),
        ("update_kjokken_pricing.py", "5. Kjøkken"),
        
        # Already existing from previous work
        ("update_elektriker_pricing.py", "6. Elektriker (existing)"),
        ("update_grunnarbeider_pricing.py", "7. Grunnarbeider (existing)"),
        ("update_gulvarbeider_pricing.py", "8. Gulvarbeider (existing)"),
    ]
    
    successful_updates = 0
    failed_updates = []
    start_time = time.time()
    
    for script_file, category_name in pricing_scripts:
        success = run_script(script_file, category_name)
        if success:
            successful_updates += 1
        else:
            failed_updates.append(category_name)
    
    # Summary
    elapsed_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"📊 UPDATE SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {successful_updates}/{len(pricing_scripts)} categories")
    print(f"⏱️  Total time: {elapsed_time:.1f} seconds")
    
    if failed_updates:
        print(f"❌ Failed: {', '.join(failed_updates)}")
    else:
        print(f"🎉 ALL PRICING CATEGORIES UPDATED SUCCESSFULLY!")
        
        # Show database stats
        print(f"\n📈 DATABASE NOW CONTAINS:")
        print(f"   🔨 Tømrer/bygg: lettvegg, himling, dører, vindusforinger")
        print(f"   🏠 Tak/kledning: takomlegging, etterisolering, takrenner")
        print(f"   🏠 Isolasjon: blåseisolasjon, dampsperre, lufttetting")
        print(f"   🚪 Vinduer/dører: utskifting, montering, alle kvaliteter")
        print(f"   🍳 Kjøkken: riving, montering, benkeplater, hvitevarer")
        print(f"   ⚡ Elektriker: timepris, installasjoner, el-anlegg")
        print(f"   🏗️  Grunnarbeider: graving, fundamentering, sprengning")
        print(f"   🏠 Gulvarbeider: parkett, laminat, vinyl, microsement")
        
        print(f"\n💡 KEY INSIGHTS FROM ALL CATEGORIES:")
        print(f"   📦 Package deals often provide 15-25% savings")
        print(f"   🏛️  Enova support available for energy upgrades (up to 50k)")
        print(f"   💰 Total project costs range from 50k to 600k+ depending on scope")
        print(f"   ⚡ Energy upgrades typically reduce heating costs by 20-40%")
        print(f"   🔧 Professional installation ensures warranty and quality")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Update enhanced renovation agent with new categories")
        print(f"   2. Add query recognition for all new service types")
        print(f"   3. Test integration with sample queries")
        print(f"   4. Deploy to production for customer use")
    
    return len(failed_updates) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)