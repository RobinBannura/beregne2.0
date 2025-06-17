from typing import Dict, Any, List
import httpx
import json
import re
import os
from datetime import datetime
from .base_agent import BaseAgent

class EnhancedRenovationAgent(BaseAgent):
    """
    Avansert oppussingsagent med:
    - Komplett byggekostnadskalkulator
    - Arbeidstid og lønn beregninger
    - Lead-generering til Monday/CRM
    - Sanntids materialpriser
    """
    
    def __init__(self):
        super().__init__()
        self.agent_name = "renovation"
        
        # Utvidede materialkonstanter
        self.MATERIALS = {
            "maling": {
                "dekning_per_liter": 10,
                "pris_per_liter": 250,
                "lag": 2,
                "arbeidstid_per_m2": 0.3,  # timer per m²
                "timepris": 650  # NOK per time
            },
            "fliser": {
                "spill_faktor": 0.1,
                "pris_per_m2": 300,
                "fugemasse_per_m2": 0.5,
                "arbeidstid_per_m2": 1.2,
                "timepris": 750
            },
            "laminat": {
                "spill_faktor": 0.08,
                "pris_per_m2": 200,
                "arbeidstid_per_m2": 0.8,
                "timepris": 650
            },
            "gips": {
                "kg_per_m2": 1.2,
                "pris_per_kg": 15,
                "arbeidstid_per_m2": 0.5,
                "timepris": 600
            },
            "rør": {
                "pris_per_meter": 85,
                "pris_per_m2": 400,  # Estimated per m2 for plumbing
                "fittings_faktor": 0.3,
                "arbeidstid_per_m2": 2.0,  # hours per m2
                "arbeidstid_per_meter": 0.4,
                "timepris": 850  # Rørlegger
            },
            "elektrisk": {
                "pris_per_punkt": 450,
                "pris_per_m2": 600,  # Estimated per m2 for electrical work
                "material_faktor": 0.4,
                "arbeidstid_per_m2": 1.5,  # hours per m2
                "arbeidstid_per_punkt": 1.0,
                "timepris": 950  # Elektriker
            },
            "benkeplate": {
                "pris_per_m2": 1200,  # Kitchen countertop
                "arbeidstid_per_m2": 2.0,
                "timepris": 700
            }
        }
        
        # Komplette prosjekttyper
        self.PROJECT_TYPES = {
            "bad_komplett": {
                "materialer": ["fliser", "rør", "elektrisk", "maling"],
                "arbeidsområder": ["rørlegger", "elektriker", "flislegger", "maler"],
                "tillegg": {
                    "prosjektledelse": 0.15,  # 15% av total
                    "uforutsett": 0.1,       # 10% buffer
                    "rydding": 5000          # Fast sum
                }
            },
            "kjøkken_komplett": {
                "materialer": ["laminat", "elektrisk", "maling", "benkeplate"],
                "arbeidsområder": ["elektriker", "tømrer", "maler"],
                "tillegg": {
                    "prosjektledelse": 0.12,
                    "uforutsett": 0.08,
                    "rydding": 3000
                }
            }
        }
        
        # CRM integrasjon
        self.MONDAY_CONFIG = {
            "board_id": os.getenv("MONDAY_BOARD_ID", "2004442153"),
            "api_token": os.getenv("MONDAY_API_TOKEN", "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUyNzE1NzU5NSwiYWFpIjoxMSwidWlkIjo3Njg2NzQ1OCwiaWFkIjoiMjAyNS0wNi0xNlQyMzowNDowOS4yNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjk4NTIzNTgsInJnbiI6ImV1YzEifQ.vUbawhibR9-r7Ex-6L2N_0FEVAeG9N8Sl88kQ14bvWw"),
            "lead_threshold": 50000  # Hvis prosjekt > 50k NOK, send til Monday
        }

    async def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prosesserer oppussingsspørringer med full kostnadskalkulator"""
        try:
            analysis = self._analyze_renovation_query(query)
            
            if analysis["type"] == "full_project_estimate":
                result = await self._calculate_full_project(analysis, query)
            elif analysis["type"] == "material_and_labor":
                result = await self._calculate_material_and_labor(analysis, query)
            elif analysis["type"] == "price_comparison":
                result = await self._compare_suppliers(analysis, query)
            else:
                result = await self._basic_calculation(analysis, query)
            
            # Lead-generering hvis stort prosjekt
            if result.get("total_cost", 0) > self.MONDAY_CONFIG["lead_threshold"]:
                result["lead_generation"] = self._generate_lead_capture(result)
            
            return result
            
        except Exception as e:
            return {
                "response": f"Beklager, jeg kunne ikke behandle din oppussingsspørring: {str(e)}",
                "agent_used": self.agent_name,
                "error": str(e)
            }

    async def _calculate_full_project(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Beregner komplett prosjekt med materialer, arbeid og tillegg"""
        project_type = analysis.get("project_type", "bad_komplett")
        area = analysis.get("area", 10)
        
        project_config = self.PROJECT_TYPES.get(project_type)
        total_material_cost = 0
        total_labor_cost = 0
        total_time_hours = 0
        
        detailed_breakdown = {}
        
        # Beregn for hvert material/arbeidsområde
        if project_config:
            for material in project_config["materialer"]:
                if material in self.MATERIALS:
                    mat_calc = self._calculate_material_with_labor(material, area)
                    detailed_breakdown[material] = mat_calc
                    total_material_cost += mat_calc["material_cost"]
                    total_labor_cost += mat_calc["labor_cost"]
                    total_time_hours += mat_calc["hours"]
        else:
            # Fallback til grunnleggende materialer
            for material in ["maling", "fliser"]:
                if material in self.MATERIALS:
                    mat_calc = self._calculate_material_with_labor(material, area)
                    detailed_breakdown[material] = mat_calc
                    total_material_cost += mat_calc["material_cost"]
                    total_labor_cost += mat_calc["labor_cost"]
                    total_time_hours += mat_calc["hours"]
        
        # Legg til tillegg
        if project_config:
            tillegg = project_config["tillegg"]
        else:
            # Default tillegg for fallback
            tillegg = {
                "prosjektledelse": 0.15,
                "uforutsett": 0.1,
                "rydding": 5000
            }
        
        subtotal = total_material_cost + total_labor_cost
        
        prosjektledelse = subtotal * tillegg["prosjektledelse"]
        uforutsett = subtotal * tillegg["uforutsett"]
        rydding = tillegg["rydding"]
        
        total_cost = subtotal + prosjektledelse + uforutsett + rydding
        
        # Generer respons
        response = f"""
        <h2>🏗️ Komplett {project_type.replace('_', ' ').title()} - {area} m²</h2>
        
        <h3>📋 Detaljert kostnadsoverslag</h3>
        <table style="width:100%; border-collapse: collapse;">
        <tr style="background: #f5f5f5;">
            <th style="border: 1px solid #ddd; padding: 8px;">Kategori</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Materialer</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Arbeid</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Timer</th>
            <th style="border: 1px solid #ddd; padding: 8px;">Sum</th>
        </tr>
        """
        
        for material, calc in detailed_breakdown.items():
            response += f"""
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">{material.title()}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{calc['material_cost']:,.0f} NOK</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{calc['labor_cost']:,.0f} NOK</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{calc['hours']:.1f}t</td>
                <td style="border: 1px solid #ddd; padding: 8px;"><strong>{calc['total']:,.0f} NOK</strong></td>
            </tr>
            """
        
        response += f"""
        </table>
        
        <h3>💰 Kostnadssammendrag</h3>
        <ul>
            <li><strong>Materialer totalt:</strong> {total_material_cost:,.0f} NOK</li>
            <li><strong>Arbeid totalt:</strong> {total_labor_cost:,.0f} NOK</li>
            <li><strong>Prosjektledelse ({tillegg['prosjektledelse']*100:.0f}%):</strong> {prosjektledelse:,.0f} NOK</li>
            <li><strong>Uforutsett ({tillegg['uforutsett']*100:.0f}%):</strong> {uforutsett:,.0f} NOK</li>
            <li><strong>Rydding og avfall:</strong> {rydding:,.0f} NOK</li>
        </ul>
        
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <h3 style="color: #1976d2;">🎯 Totalkostnad: {total_cost:,.0f} NOK</h3>
            <p><strong>Estimert tidsbruk:</strong> {total_time_hours:.0f} timer ({total_time_hours/8:.1f} arbeidsdager)</p>
        </div>
        
        <p><small>💡 Prisene er estimater basert på markedspriser per {datetime.now().strftime('%B %Y')}. 
        Faktiske priser kan variere ±15% avhengig av leverandør og kompleksitet.</small></p>
        """
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": total_cost,
            "material_cost": total_material_cost,
            "labor_cost": total_labor_cost,
            "estimated_hours": total_time_hours,
            "breakdown": detailed_breakdown
        }

    def _calculate_material_with_labor(self, material: str, area: float) -> Dict[str, Any]:
        """Beregner både material og arbeidskostnad"""
        mat_config = self.MATERIALS[material]
        
        # Materialkostnad (eksisterende logikk)
        if material == "maling":
            material_cost = self._calculate_paint(area)["total_cost"]
        elif material == "fliser":
            material_cost = self._calculate_tiles(area)["total_cost"]
        elif material == "laminat":
            material_cost = self._calculate_laminate(area)["total_cost"]
        else:
            material_cost = area * mat_config.get("pris_per_m2", 100)
        
        # Arbeidskostnad
        hours = area * mat_config["arbeidstid_per_m2"]
        labor_cost = hours * mat_config["timepris"]
        
        return {
            "material_cost": material_cost,
            "labor_cost": labor_cost,
            "hours": hours,
            "total": material_cost + labor_cost
        }

    def _generate_lead_capture(self, calculation_result: Dict) -> Dict[str, Any]:
        """Genererer lead-capture for store prosjekter"""
        total_cost = calculation_result.get("total_cost", 0)
        
        lead_message = f"""
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #856404;">🤝 Trenger du hjelp med gjennomføring?</h3>
            <p>Dette er et større prosjekt på <strong>{total_cost:,.0f} NOK</strong>. Vi kan hjelpe deg med:</p>
            <ul>
                <li>🏗️ Koble deg med kvalifiserte håndverkere</li>
                <li>📋 Prosjektplanlegging og koordinering</li>
                <li>💰 Forhandling av priser med leverandører</li>
                <li>🔍 Kvalitetskontroll underveis</li>
            </ul>
            
            <div style="text-align: center; margin-top: 15px;">
                <button onclick="openLeadForm()" style="background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer;">
                    💬 Få gratis konsultasjon
                </button>
            </div>
        </div>
        
        <script>
        function openLeadForm() {{
            // Integrasjon med Monday eller Google Sheets
            const leadData = {{
                project_type: 'renovation',
                estimated_cost: {total_cost},
                area: '{calculation_result.get("area", "ikke oppgitt")}',
                timestamp: new Date().toISOString()
            }};
            
            // Send til Monday.com eller Google Sheets
            fetch('/api/leads', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(leadData)
            }});
            
            // Åpne kontaktskjema
            window.open('https://calendly.com/househacker/konsultasjon', '_blank');
        }}
        </script>
        """
        
        return {
            "show_lead_capture": True,
            "lead_message": lead_message,
            "estimated_value": total_cost,
            "recommended_action": "schedule_consultation"
        }

    def can_handle(self, query: str) -> bool:
        """Sjekker om denne agenten kan håndtere spørringen"""
        renovation_keywords = [
            "oppussing", "renovering", "maling", "fliser", "laminat", "bad", "kjøkken",
            "material", "kostnad", "pris", "bygge", "installere", "rør", "elektrisk",
            "gips", "isolasjon", "vegg", "gulv", "tak", "prosjekt", "håndverker",
            "byggevareh", "maxbo", "byggmax", "jernia", "arbeidstime", "timepris"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in renovation_keywords)

    def get_capabilities(self) -> Dict[str, Any]:
        """Returnerer informasjon om hva denne agenten kan gjøre"""
        return {
            "name": self.agent_name,
            "description": "Avansert oppussings- og byggekostnadskalkulator med CRM-integrasjon",
            "keywords": [
                "oppussing", "renovering", "materialkalkulator", "byggekostnader",
                "arbeidstid", "timepris", "prosjektledelse", "håndverkere", "CRM"
            ],
            "features": [
                "Komplett materialkalkulator",
                "Arbeidstid og lønnsberegninger", 
                "Sanntids materialpriser",
                "Lead-generering for store prosjekter",
                "Monday.com CRM integrasjon",
                "Detaljerte kostnadsoverslag"
            ]
        }

    def _analyze_renovation_query(self, query: str) -> Dict[str, Any]:
        """Analyserer spørring for å bestemme type beregning som trengs"""
        query_lower = query.lower()
        
        # Ekstrahering av areal
        area_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:m²|m2|kvadratmeter|kvm)', query_lower)
        area = float(area_match.group(1)) if area_match else 10  # Default 10m²
        
        # Prosjekttype
        if any(word in query_lower for word in ['bad', 'baderom', 'toalett']):
            project_type = "bad_komplett"
        elif any(word in query_lower for word in ['kjøkken', 'kitchen']):
            project_type = "kjøkken_komplett"
        else:
            project_type = "bad_komplett"  # Default
        
        # Type analyse
        if any(word in query_lower for word in ['komplett', 'totalrenovering', 'alt', 'hele']):
            analysis_type = "full_project_estimate"
        elif any(word in query_lower for word in ['arbeid', 'lønn', 'timepris', 'håndverker']):
            analysis_type = "material_and_labor"
        elif any(word in query_lower for word in ['sammenlign', 'pris', 'billigst', 'leverandør']):
            analysis_type = "price_comparison"
        else:
            analysis_type = "material_and_labor"
        
        return {
            "type": analysis_type,
            "area": area,
            "project_type": project_type,
            "materials": self._extract_materials(query_lower)
        }

    def _extract_materials(self, query: str) -> List[str]:
        """Ekstraherer materialer fra spørring"""
        materials = []
        for material in self.MATERIALS.keys():
            if material in query:
                materials.append(material)
        return materials if materials else ["maling", "fliser"]  # Default

    async def _calculate_material_and_labor(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Beregner material og arbeidskostnader"""
        materials = analysis.get("materials", ["maling"])
        area = analysis.get("area", 10)
        
        total_cost = 0
        breakdown = {}
        
        for material in materials:
            if material in self.MATERIALS:
                calc = self._calculate_material_with_labor(material, area)
                breakdown[material] = calc
                total_cost += calc["total"]
        
        response = f"""
        <h2>🔨 Material og Arbeidskostnad - {area} m²</h2>
        <ul>
        """
        
        for material, calc in breakdown.items():
            response += f"""
            <li><strong>{material.title()}:</strong> 
                Material: {calc['material_cost']:,.0f} NOK + 
                Arbeid: {calc['labor_cost']:,.0f} NOK = 
                <strong>{calc['total']:,.0f} NOK</strong>
            </li>
            """
        
        response += f"""
        </ul>
        <p><strong>Total kostnad: {total_cost:,.0f} NOK</strong></p>
        """
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": total_cost,
            "breakdown": breakdown
        }

    async def _compare_suppliers(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Sammenligner priser fra forskjellige leverandører"""
        materials = analysis.get("materials", ["maling"])
        
        response = "<h2>🏪 Prissammenligning</h2>"
        
        for material in materials:
            prices = await self.get_realtime_prices(material)
            response += f"""
            <h3>{material.title()}</h3>
            <ul>
            """
            for price_info in prices:
                response += f"""
                <li><strong>{price_info['supplier']}:</strong> {price_info['price']} NOK 
                    ({price_info['availability']}, {price_info['delivery_time']})</li>
                """
            response += "</ul>"
        
        return {
            "response": response,
            "agent_used": self.agent_name
        }

    async def _basic_calculation(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Grunnleggende materialberegning"""
        materials = analysis.get("materials", ["maling"])
        area = analysis.get("area", 10)
        
        if "maling" in materials:
            return await self._calculate_paint_basic(area)
        elif "fliser" in materials:
            return await self._calculate_tiles_basic(area)
        else:
            return {
                "response": "Kan ikke beregne for det materialet ennå.",
                "agent_used": self.agent_name
            }

    async def _calculate_paint_basic(self, area: float) -> Dict[str, Any]:
        """Grunnleggende malingberegning"""
        paint_calc = self._calculate_paint(area)
        
        response = f"""
        <h2>🎨 Malingkalkulator - {area} m²</h2>
        <ul>
            <li><strong>Liter maling:</strong> {paint_calc['liters_needed']:.1f} L</li>
            <li><strong>Kostnad:</strong> {paint_calc['total_cost']:,.0f} NOK</li>
        </ul>
        """
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": paint_calc['total_cost']
        }

    async def _calculate_tiles_basic(self, area: float) -> Dict[str, Any]:
        """Grunnleggende flisberegning"""
        tiles_calc = self._calculate_tiles(area)
        
        response = f"""
        <h2>🏗️ Fliskalkulator - {area} m²</h2>
        <ul>
            <li><strong>Fliser nødvendig:</strong> {tiles_calc['area_with_waste']:.1f} m²</li>
            <li><strong>Kostnad:</strong> {tiles_calc['total_cost']:,.0f} NOK</li>
        </ul>
        """
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": tiles_calc['total_cost']
        }

    def _calculate_paint(self, area: float) -> Dict[str, Any]:
        """Beregner malingbehov"""
        mat_config = self.MATERIALS["maling"]
        liters_needed = (area * mat_config["lag"]) / mat_config["dekning_per_liter"]
        total_cost = liters_needed * mat_config["pris_per_liter"]
        
        return {
            "liters_needed": liters_needed,
            "total_cost": total_cost,
            "layers": mat_config["lag"]
        }

    def _calculate_tiles(self, area: float) -> Dict[str, Any]:
        """Beregner flisbehov"""
        mat_config = self.MATERIALS["fliser"]
        area_with_waste = area * (1 + mat_config["spill_faktor"])
        total_cost = area_with_waste * mat_config["pris_per_m2"]
        
        return {
            "area_with_waste": area_with_waste,
            "total_cost": total_cost,
            "waste_factor": mat_config["spill_faktor"]
        }

    def _calculate_laminate(self, area: float) -> Dict[str, Any]:
        """Beregner laminatbehov"""
        mat_config = self.MATERIALS["laminat"]
        area_with_waste = area * (1 + mat_config["spill_faktor"])
        total_cost = area_with_waste * mat_config["pris_per_m2"]
        
        return {
            "area_with_waste": area_with_waste,
            "total_cost": total_cost,
            "waste_factor": mat_config["spill_faktor"]
        }
    
    async def get_realtime_prices(self, material: str) -> List[Dict]:
        """Henter sanntidspriser fra forskjellige leverandører"""
        # Placeholder for API-integrasjoner
        suppliers = ["maxbo", "byggmax", "jernia"]
        prices = []
        
        for supplier in suppliers:
            # Her kan du integrere med ekte API-er
            mock_price = self._get_mock_price(material, supplier)
            prices.append(mock_price)
        
        return sorted(prices, key=lambda x: x["price"])
    
    def _get_mock_price(self, material: str, supplier: str) -> Dict:
        """Mock-priser for demonstrasjon"""
        base_prices = {
            "maling": {"maxbo": 289, "byggmax": 245, "jernia": 267},
            "fliser": {"maxbo": 299, "byggmax": 279, "jernia": 315},
            "laminat": {"maxbo": 199, "byggmax": 189, "jernia": 205}
        }
        
        return {
            "supplier": supplier,
            "material": material,
            "price": base_prices.get(material, {}).get(supplier, 250),
            "unit": "per enhet",
            "availability": "På lager",
            "delivery_time": "2-3 dager"
        }