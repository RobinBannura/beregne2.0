#!/usr/bin/env python3
"""
Calculate realistic wall and ceiling area from floor area
"""

def calculate_wall_ceiling_area():
    """Calculate wall and ceiling area from floor area"""
    
    floor_area = 150  # m² gulvflate
    
    print(f"🏠 Beregning av vegg- og takflate fra {floor_area} m² gulvflate")
    print("=" * 60)
    
    # Typical Norwegian house calculations
    # Assume rectangular house layout
    
    # Estimate room dimensions from floor area
    # For 150m² house, typical layout might be ~12m x 12.5m
    estimated_length = (floor_area ** 0.5) * 1.1  # Slightly rectangular
    estimated_width = floor_area / estimated_length
    
    # Standard room height in Norway
    room_height = 2.7  # meters (typical for new houses)
    
    print(f"📐 Estimerte husdimensjoner:")
    print(f"   Lengde: {estimated_length:.1f} m")
    print(f"   Bredde: {estimated_width:.1f} m") 
    print(f"   Høyde: {room_height} m")
    print(f"   Gulvflate: {floor_area} m²")
    
    # Calculate wall area
    perimeter = 2 * (estimated_length + estimated_width)
    gross_wall_area = perimeter * room_height
    
    # Subtract doors and windows (typical deductions)
    # Norwegian houses typically have:
    doors_area = 15 * 2.1  # ~15 doors x 2.1m² each
    windows_area = floor_area * 0.15  # ~15% of floor area in windows
    
    net_wall_area = gross_wall_area - doors_area - windows_area
    
    # Calculate ceiling area (same as floor area for flat ceilings)
    ceiling_area = floor_area
    
    # Total paintable area
    total_paintable_area = net_wall_area + ceiling_area
    
    print(f"\n🎨 Malerflater:")
    print(f"   Brutto veggflate: {gross_wall_area:.0f} m²")
    print(f"   - Dører: {doors_area:.0f} m²")
    print(f"   - Vinduer: {windows_area:.0f} m²")
    print(f"   = Netto veggflate: {net_wall_area:.0f} m²")
    print(f"   + Takflate: {ceiling_area:.0f} m²")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   TOTAL MALERFLATE: {total_paintable_area:.0f} m²")
    
    # Calculate costs with correct area
    price_per_m2 = 225  # Average from 200-250 NOK/m² (skjøtesparkling + maling)
    material_and_labor = total_paintable_area * price_per_m2
    
    # Rigg og drift for large project (more realistic for whole house)
    rigg_og_drift = max(15000, floor_area * 50)  # Higher for whole house projects
    
    total_ex_vat = material_and_labor + rigg_og_drift
    total_inc_vat = total_ex_vat * 1.25  # 25% MVA
    
    print(f"\n💰 KORREKTE KOSTNADER:")
    print(f"   Malerflate: {total_paintable_area:.0f} m² x {price_per_m2} NOK/m²")
    print(f"   Arbeid og materialer: {material_and_labor:,.0f} NOK")
    print(f"   Rigg og drift: {rigg_og_drift:,.0f} NOK")
    print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"   Totalt eks. mva: {total_ex_vat:,.0f} NOK")
    print(f"   Totalt inkl. mva: {total_inc_vat:,.0f} NOK")
    
    print(f"\n🎯 SAMMENLIGNING:")
    print(f"   Min erfaring: 130.000-200.000 NOK inkl. mva")
    print(f"   Beregnet pris: {total_inc_vat:,.0f} NOK inkl. mva")
    
    if 130000 <= total_inc_vat <= 200000:
        print(f"   ✅ PERFEKT MATCH!")
    else:
        print(f"   ⚠️  Avvik fra erfaring")
    
    # Calculate conversion factor for future use
    conversion_factor = total_paintable_area / floor_area
    print(f"\n📊 KONVERTERINGSFAKTOR:")
    print(f"   Gulvflate → Malerflate: {conversion_factor:.1f}x")
    print(f"   (For fremtidige beregninger: gulvflate x {conversion_factor:.1f})")
    
    return {
        "floor_area": floor_area,
        "total_paintable_area": total_paintable_area,
        "conversion_factor": conversion_factor,
        "total_cost_inc_vat": total_inc_vat,
        "total_cost_ex_vat": total_ex_vat
    }

if __name__ == "__main__":
    calculate_wall_ceiling_area()