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
        
        # Realistiske Oslo-priser 2025 (oppdatert basert på markedsdata)
        self.MATERIALS = {
            "maling": {
                "dekning_per_liter": 8,  # Mer realistisk dekning
                "pris_per_liter": 450,   # Oslo-priser for kvalitetsmaling
                "lag": 2,
                "arbeidstid_per_m2": 0.5,  # timer per m² (inkludert prep)
                "timepris": 750,  # Oslo-timepriser for malere
                "prep_faktor": 1.3  # Ekstra tid for preparering
            },
            "fliser": {
                "spill_faktor": 0.15,  # Mer realistisk spill
                "pris_per_m2": 800,    # Oslo-priser for gode fliser
                "fugemasse_per_m2": 0.8,
                "arbeidstid_per_m2": 2.5,  # Mer realistisk tid
                "timepris": 950,  # Oslo-timepriser for flisleggere
                "underlag_kostnad": 200  # Per m² for underlag
            },
            "laminat": {
                "spill_faktor": 0.1,
                "pris_per_m2": 450,    # Oslo-priser for kvalitetslaminat
                "arbeidstid_per_m2": 1.2,
                "timepris": 700,
                "underlag_kostnad": 150  # Per m² for underlag
            },
            "gips": {
                "kg_per_m2": 1.5,
                "pris_per_kg": 25,      # Oslo-priser
                "arbeidstid_per_m2": 0.8,
                "timepris": 650,
                "spackling_kostnad": 100  # Per m² for spackling
            },
            "rør": {
                "pris_per_meter": 180,  # Oslo-priser for rør
                "pris_per_m2": 1200,    # Realistisk per m² for komplette rørarbeider
                "fittings_faktor": 0.4,
                "arbeidstid_per_m2": 3.5,  # Mer realistisk tid
                "timepris": 1200,  # Oslo-timepriser for rørleggere
                "armatur_kostnad": 8000  # Gjennomsnittlig for bad
            },
            "elektrisk": {
                "pris_per_punkt": 1200,  # Oslo-priser per uttak/bryter
                "pris_per_m2": 1500,     # Realistisk per m² for elektro
                "material_faktor": 0.3,
                "arbeidstid_per_m2": 2.0,
                "timepris": 1350,  # Oslo-timepriser for elektrikere
                "sikringsskap_oppgradering": 15000  # Fast kostnad
            },
            "benkeplate": {
                "pris_per_m2": 2500,    # Oslo-priser for kvarts/granitt
                "arbeidstid_per_m2": 3.0,
                "timepris": 850,
                "montering_kostnad": 5000  # Fast kostnad for montering
            }
        }
        
        # Komplette prosjekttyper (Oslo-markedet)
        self.PROJECT_TYPES = {
            "bad_komplett": {
                "materialer": ["fliser", "rør", "elektrisk", "maling"],
                "arbeidsområder": ["rørlegger", "elektriker", "flislegger", "maler"],
                "base_kostnader": {
                    "wc": 15000,
                    "servant": 8000, 
                    "dusjkabinett": 25000,
                    "ventilasjon": 12000,
                    "gulvvarme": 8000,
                    "riving": 25000
                },
                "tillegg": {
                    "prosjektledelse": 0.18,  # 18% av total for Oslo
                    "uforutsett": 0.15,       # 15% buffer (Oslo-kompleksitet)
                    "rydding": 15000,         # Høyere Oslo-priser
                    "byggesøknad": 8000       # Ofte nødvendig i Oslo
                }
            },
            "kjøkken_komplett": {
                "materialer": ["laminat", "elektrisk", "maling", "benkeplate"],
                "arbeidsområder": ["elektriker", "tømrer", "maler"],
                "base_kostnader": {
                    "skap": 80000,  # Gjennomsnittlig for Oslo
                    "hvitevarer": 45000,
                    "ventilator": 8000,
                    "belysning": 15000,
                    "riving": 20000
                },
                "tillegg": {
                    "prosjektledelse": 0.15,
                    "uforutsett": 0.12,
                    "rydding": 12000,
                    "byggesøknad": 5000
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
            elif analysis["type"] == "painting_specific":
                result = await self._handle_painting_inquiry(analysis, query)
            elif analysis["type"] == "needs_clarification" or analysis["needs_clarification"]:
                result = await self._ask_clarifying_questions(analysis, query)
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
        
        # Legg til base_kostnader (fast utstyr)
        base_kostnader_total = 0
        if project_config and "base_kostnader" in project_config:
            for item, kostnad in project_config["base_kostnader"].items():
                base_kostnader_total += kostnad
        
        # Legg til tillegg
        if project_config:
            tillegg = project_config["tillegg"]
        else:
            # Default tillegg for fallback
            tillegg = {
                "prosjektledelse": 0.15,
                "uforutsett": 0.1,
                "rydding": 15000,
                "byggesøknad": 0
            }
        
        subtotal = total_material_cost + total_labor_cost + base_kostnader_total
        
        prosjektledelse = subtotal * tillegg["prosjektledelse"]
        uforutsett = subtotal * tillegg["uforutsett"]
        rydding = tillegg["rydding"]
        byggesøknad = tillegg.get("byggesøknad", 0)
        
        total_cost = subtotal + prosjektledelse + uforutsett + rydding + byggesøknad
        
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
        
        <h3>🛠️ Fast utstyr og installasjoner</h3>
        <ul>
        """
        
        if project_config and "base_kostnader" in project_config:
            for item, kostnad in project_config["base_kostnader"].items():
                response += f"""<li><strong>{item.replace('_', ' ').title()}:</strong> {kostnad:,.0f} NOK</li>"""
        
        response += f"""
        </ul>
        
        <h3>💰 Kostnadssammendrag</h3>
        <ul>
            <li><strong>Materialer totalt:</strong> {total_material_cost:,.0f} NOK</li>
            <li><strong>Arbeid totalt:</strong> {total_labor_cost:,.0f} NOK</li>
            <li><strong>Fast utstyr:</strong> {base_kostnader_total:,.0f} NOK</li>
            <li><strong>Prosjektledelse ({tillegg['prosjektledelse']*100:.0f}%):</strong> {prosjektledelse:,.0f} NOK</li>
            <li><strong>Uforutsett ({tillegg['uforutsett']*100:.0f}%):</strong> {uforutsett:,.0f} NOK</li>
            <li><strong>Rydding og avfall:</strong> {rydding:,.0f} NOK</li>"""
        
        if byggesøknad > 0:
            response += f"""<li><strong>Byggesøknad:</strong> {byggesøknad:,.0f} NOK</li>"""
        
        response += """
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
        
        <!-- GDPR-Compliant Lead Form -->
        <div id="leadFormModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
            <div style="position: relative; margin: 50px auto; width: 90%; max-width: 600px; background: white; padding: 30px; border-radius: 12px; max-height: 80vh; overflow-y: auto;">
                <span onclick="closeLeadForm()" style="position: absolute; top: 15px; right: 20px; font-size: 24px; cursor: pointer;">&times;</span>
                
                <h3 style="color: #856404; margin-bottom: 20px;">📝 Gratis konsultasjon - househacker</h3>
                
                <form id="leadForm">
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Navn *</label>
                        <input type="text" id="leadName" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Telefon *</label>
                        <input type="tel" id="leadPhone" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">E-post *</label>
                        <input type="email" id="leadEmail" required style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Adresse</label>
                        <input type="text" id="leadAddress" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Beskriv prosjektet ditt</label>
                        <textarea id="leadDescription" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;" placeholder="F.eks: Totalrenovering av bad, ønsker moderne design..."></textarea>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Ønsket tidsramme</label>
                        <select id="leadTimeline" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                            <option value="">Velg tidsramme</option>
                            <option value="umiddelbart">Umiddelbart</option>
                            <option value="1-3 måneder">1-3 måneder</option>
                            <option value="3-6 måneder">3-6 måneder</option>
                            <option value="6-12 måneder">6-12 måneder</option>
                            <option value="over 1 år">Over 1 år</option>
                        </select>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Budsjettramme</label>
                        <select id="leadBudget" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px;">
                            <option value="">Velg budsjettramme</option>
                            <option value="under 200k">Under 200.000 NOK</option>
                            <option value="200-500k">200.000 - 500.000 NOK</option>
                            <option value="500k-1M">500.000 - 1.000.000 NOK</option>
                            <option value="over 1M">Over 1.000.000 NOK</option>
                        </select>
                    </div>
                    
                    <!-- GDPR Samtykke -->
                    <div style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px;">
                        <label style="display: flex; align-items: flex-start; cursor: pointer;">
                            <input type="checkbox" id="privacyConsent" required style="margin-right: 10px; margin-top: 2px;">
                            <span style="font-size: 14px;">
                                <strong>Jeg samtykker til behandling av personopplysninger *</strong><br>
                                <small>Jeg samtykker til at househacker behandler mine personopplysninger for å gi meg informasjon om tjenester og oppfølging av min henvendelse. 
                                Les mer i <a href="https://househacker.no/personvern" target="_blank" style="color: #007bff;">personvernerklæringen</a>.</small>
                            </span>
                        </label>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: flex; align-items: flex-start; cursor: pointer;">
                            <input type="checkbox" id="marketingConsent" style="margin-right: 10px; margin-top: 2px;">
                            <span style="font-size: 14px;">
                                <small>Jeg ønsker å motta markedsføring og nyheter fra househacker (valgfritt)</small>
                            </span>
                        </label>
                    </div>
                    
                    <button type="submit" style="background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; width: 100%;">
                        📞 Send forespørsel
                    </button>
                </form>
            </div>
        </div>
        
        <script>
        function openLeadForm() {{
            document.getElementById('leadFormModal').style.display = 'block';
        }}
        
        function closeLeadForm() {{
            document.getElementById('leadFormModal').style.display = 'none';
        }}
        
        document.getElementById('leadForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const leadData = {{
                project_type: 'renovation',
                estimated_cost: {total_cost},
                area: '{calculation_result.get("area", "ikke oppgitt")}',
                partner_id: 'househacker',
                name: document.getElementById('leadName').value,
                phone: document.getElementById('leadPhone').value,
                email: document.getElementById('leadEmail').value,
                address: document.getElementById('leadAddress').value,
                project_description: document.getElementById('leadDescription').value,
                timeline: document.getElementById('leadTimeline').value,
                budget_range: document.getElementById('leadBudget').value,
                privacy_consent: document.getElementById('privacyConsent').checked,
                marketing_consent: document.getElementById('marketingConsent').checked
            }};
            
            try {{
                const response = await fetch('/api/leads', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(leadData)
                }});
                
                if (response.ok) {{
                    alert('Takk! Vi har mottatt din forespørsel og tar kontakt snart. 😊');
                    closeLeadForm();
                }} else {{
                    const error = await response.json();
                    alert('Feil: ' + error.detail);
                }}
            }} catch (error) {{
                alert('Noe gikk galt. Prøv igjen eller ring oss direkte.');
            }}
        }});
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
            # Grunnleggende oppussingsord
            "oppussing", "oppuss", "pusse opp", "renovering", "renovere", "renover",
            "bygge", "bygg", "installere", "installer", "montere", "monter",
            
            # Rom og områder
            "bad", "baderom", "toalett", "wc", "kjøkken", "kitchen", "stue", "soverom",
            "gang", "hall", "entré", "balkong", "terasse", "kjeller", "loft",
            
            # Materialer
            "maling", "male", "maler", "fliser", "flise", "laminat", "parkett",
            "gips", "gipse", "isolasjon", "isolere", "rør", "rørlegger", 
            "elektrisk", "elektriker", "elektro", "kabler",
            
            # Overflater
            "vegg", "vegger", "tak", "gulv", "gulvet", "dør", "dører", 
            "vindu", "vinduer", "liste", "lister",
            
            # Kostnader og planlegging
            "kostnad", "koster", "pris", "priser", "budsjett", "estimat",
            "kalkulator", "beregn", "hvor mye", "material", "utstyr",
            
            # Håndverkere og tjenester
            "håndverker", "tømrer", "maler", "elektriker", "rørlegger",
            "flislegger", "snekkere", "arbeidstime", "timepris",
            
            # Butikker
            "byggevareh", "maxbo", "byggmax", "jernia", "obs bygg",
            
            # Generelle ord som kan relatere til oppussing
            "prosjekt", "jobb", "arbeid", "hjem", "hus", "leilighet",
            "forbedre", "endre", "skifte", "bytte", "erstatte"
        ]
        
        query_lower = query.lower()
        
        # Sjekk eksakte matches først
        if any(keyword in query_lower for keyword in renovation_keywords):
            return True
            
        # Sjekk vanlige fraser
        common_phrases = [
            "skal pusse", "vil pusse", "ønsker å pusse", "planlegger å pusse",
            "skal renovere", "vil renovere", "ønsker å renovere", "planlegger å renovere",
            "skal bygge", "vil bygge", "ønsker å bygge", "planlegger å bygge",
            "trenger hjelp", "kan du hjelle", "hvor mye koster", "hva koster",
            "kan jeg regne med", "estimere kostnad", "beregne pris"
        ]
        
        return any(phrase in query_lower for phrase in common_phrases)

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
        area = float(area_match.group(1)) if area_match else None  # Ikke sett default
        
        # Prosjekttype
        if any(word in query_lower for word in ['bad', 'baderom', 'toalett']):
            project_type = "bad_komplett"
        elif any(word in query_lower for word in ['kjøkken', 'kitchen']):
            project_type = "kjøkken_komplett"
        else:
            project_type = "unknown"
        
        # Type analyse
        if any(word in query_lower for word in ['komplett', 'totalrenovering', 'alt', 'hele']):
            analysis_type = "full_project_estimate"
        elif any(word in query_lower for word in ['arbeid', 'lønn', 'timepris', 'håndverker']):
            analysis_type = "material_and_labor"
        elif any(word in query_lower for word in ['sammenlign', 'pris', 'billigst', 'leverandør']):
            analysis_type = "price_comparison"
        elif any(word in query_lower for word in ['maling', 'male']) and area:
            analysis_type = "painting_specific"
        elif len(query_lower.split()) <= 5 and any(phrase in query_lower for phrase in ['pusse opp', 'renovere', 'oppussing']):
            # Korte, generelle spørsmål som "jeg skal pusse opp"
            analysis_type = "needs_clarification"
        else:
            analysis_type = "needs_clarification"
        
        # Detaljert analyse for spesifikke materialer
        specific_details = self._extract_specific_requirements(query_lower)
        
        return {
            "type": analysis_type,
            "area": area,
            "project_type": project_type,
            "materials": self._extract_materials(query_lower),
            "needs_clarification": area is None or project_type == "unknown",
            "specific_details": specific_details
        }

    def _extract_specific_requirements(self, query: str) -> Dict[str, Any]:
        """Ekstraherer spesifikke krav fra spørring"""
        details = {
            "ceiling_painting": "tak" in query,
            "wall_painting": "vegg" in query or "vegger" in query,
            "many_windows": "mang" in query and ("vindu" in query or "dør" in query),
            "old_wallpaper": "tapet" in query,
            "rough_surface": "ru" in query or "ujamn" in query,
            "quality_level": "luksus" in query or "high-end" in query or "billig" in query
        }
        return details

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

    async def _ask_clarifying_questions(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Stiller oppfølgingsspørsmål for mer presise kalkulasjoner"""
        project_type = analysis.get("project_type", "unknown")
        area = analysis.get("area")
        
        # Generer spørsmål basert på manglende informasjon
        questions = []
        
        if not area:
            if project_type == "bad_komplett":
                questions.append("📏 Hvor stort er badet ditt? (oppgi i m²)")
            elif project_type == "kjøkken_komplett":
                questions.append("📏 Hvor stort er kjøkkenet ditt? (oppgi i m²)")
            else:
                questions.append("📏 Hvor stort er området du skal pusse opp? (oppgi i m²)")
        
        if project_type == "unknown":
            questions.append("🏠 Hvilket rom skal pusses opp? (bad, kjøkken, stue, etc.)")
        
        # Spesifikke spørsmål for malingsjobber
        if "maling" in analysis.get("materials", []) or "male" in query.lower():
            details = analysis.get("specific_details", {})
            if not details.get("ceiling_painting") and not details.get("wall_painting"):
                questions.append("🎨 Skal du male både tak og vegger, eller kun vegger?")
            if not details.get("many_windows"):
                questions.append("🪟 Er det mange vinduer og dører i rommet?")
            if not details.get("old_wallpaper"):
                questions.append("📰 Er det tapet på veggene som må fjernes?")
        
        # Sjekk om det er et veldig generelt spørsmål
        is_very_general = len(query.split()) <= 5 and any(phrase in query.lower() for phrase in ['pusse opp', 'oppussing', 'renovere'])
        
        if is_very_general:
            greeting = "Flott at du skal pusse opp! 🏠"
        else:
            greeting = "Jeg hjelper deg gjerne med kostnadsestimatet! 😊"
        
        # Generer respons med spørsmål og veiledende priser
        response = f"""
        <h2>🤔 {greeting}</h2>
        <p>For å gi deg det mest presise estimatet trenger jeg litt mer informasjon:</p>
        
        <h3>📝 Kan du svare på følgende:</h3>
        <ul>
        """
        
        for question in questions[:3]:  # Maks 3 spørsmål av gangen
            response += f"<li>{question}</li>"
        
        response += """
        </ul>
        
        <h3>💡 Veiledende priser (Oslo-området):</h3>
        """
        
        if project_type == "bad_komplett" or "bad" in query.lower():
            response += """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4>Baderom (komplett renovering)</h4>
                <ul>
                    <li><strong>Lite bad (2-3 m²):</strong> 200.000 - 350.000 NOK</li>
                    <li><strong>Standard bad (4-6 m²):</strong> 350.000 - 600.000 NOK</li>
                    <li><strong>Stort bad (7-10 m²):</strong> 600.000 - 900.000+ NOK</li>
                </ul>
                <p><small>Inkluderer riving, VVS, elektro, fliser, wc og dusjløsning.</small></p>
            </div>
            """
        
        if project_type == "kjøkken_komplett" or "kjøkken" in query.lower():
            response += """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4>Kjøkken (komplett renovering)</h4>
                <ul>
                    <li><strong>IKEA-løsning:</strong> 200.000 - 400.000 NOK</li>
                    <li><strong>Midt-segment:</strong> 400.000 - 700.000 NOK</li>
                    <li><strong>Snekkerløsning:</strong> 700.000 - 1.200.000+ NOK</li>
                </ul>
                <p><small>Prisen avhenger av: skap, benkeplate, hvitevarer, VVS/elektro-endringer og monteringskostnader (20-30k).</small></p>
            </div>
            """
        
        if "maling" in query.lower():
            response += """
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4>🎨 Maling (per m²)</h4>
                <ul>
                    <li><strong>Kun vegger:</strong> 200 - 400 NOK/m²</li>
                    <li><strong>Vegger + tak:</strong> 300 - 500 NOK/m²</li>
                    <li><strong>Med tapetfjerning:</strong> +100 - 150 NOK/m²</li>
                </ul>
                <p><small>💡 <strong>Pro-tips:</strong> Beregn alltid 10-15% ekstra maling. Bruk kvalitetsmaling for bedre dekning. Husk maskeringstape og plastduk!</small></p>
            </div>
            """
        
        response += """
        <p><strong>Kom gjerne tilbake med mer informasjon, så gir jeg deg et detaljert kostnadsoverslag! 😊</strong></p>
        """
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "needs_followup": True,
            "questions_asked": questions
        }

    async def _handle_painting_inquiry(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Håndterer spesifikke malingsspørsmål med detaljerte oppfølgingsspørsmål"""
        area = analysis.get("area", 20)  # Default 20m² hvis ikke oppgitt
        details = analysis.get("specific_details", {})
        
        # Beregn malingbehov basert på detaljer
        paint_calc = self._calculate_advanced_painting(area, details)
        
        response = f"""
        <h2>🎨 Malingkalkulator - {area} m²</h2>
        
        <h3>📊 Materialberegning</h3>
        <ul>
            <li><strong>Maling nødvendig:</strong> {paint_calc['liters_needed']:.1f} liter</li>
            <li><strong>Kostnad maling:</strong> {paint_calc['paint_cost']:,.0f} NOK</li>
            <li><strong>Arbeidstid:</strong> {paint_calc['work_hours']:.1f} timer</li>
            <li><strong>Arbeidskostnad:</strong> {paint_calc['labor_cost']:,.0f} NOK</li>
        </ul>
        
        <h3>💰 Totalkostnad</h3>
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <h3 style="color: #1976d2;">🎯 Total: {paint_calc['total_cost']:,.0f} NOK</h3>
        </div>
        
        <h3>🛠️ Utstyr du trenger</h3>
        <ul>
            <li>Maskeringstape og plastduk (ca. 500 NOK)</li>
            <li>Pensel og rull (ca. 300 NOK)</li>
            <li>Grundmaling hvis nødvendig (ca. 200 NOK/L)</li>
        </ul>
        
        <h3>💡 Pro-tips</h3>
        <ul>
            <li>🕐 <strong>Tidsbruk:</strong> Planlegg 2-3 dager for et rom (inkl. tørketid)</li>
            <li>🌡️ <strong>Temperatur:</strong> Mal ved 18-22°C for best resultat</li>
            <li>📐 <strong>Teknikk:</strong> Mal først kanter med pensel, deretter rull</li>
            <li>💧 <strong>Underlag:</strong> Vask vegger først, sparkle hull og riper</li>
        </ul>
        """
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": paint_calc['total_cost'],
            "calculation_details": paint_calc
        }

    def _calculate_advanced_painting(self, area: float, details: Dict) -> Dict[str, Any]:
        """Avansert malingberegning med spesifikke detaljer"""
        mat_config = self.MATERIALS["maling"]
        
        # Juster dekning basert på underlag
        coverage = mat_config["dekning_per_liter"]
        if details.get("rough_surface"):
            coverage *= 0.8  # Ru overflate krever mer maling
        if details.get("old_wallpaper"):
            coverage *= 0.7  # Tapet krever mer maling
        
        # Beregn maling
        layers = mat_config["lag"]
        if details.get("quality_level") and "luksus" in str(details.get("quality_level")):
            layers = 3  # Ekstra lag for luksus
        
        liters_needed = (area * layers) / coverage
        
        # Juster arbeidstid
        work_hours = area * mat_config["arbeidstid_per_m2"]
        if details.get("ceiling_painting"):
            work_hours *= 1.5  # Tak tar lengre tid
        if details.get("many_windows"):
            work_hours *= 1.3  # Mange vinduer = mer kantjobb
        if details.get("old_wallpaper"):
            work_hours += area * 0.3  # Tid for tapetfjerning
        
        # Kostnader
        paint_cost = liters_needed * mat_config["pris_per_liter"]
        labor_cost = work_hours * mat_config["timepris"]
        total_cost = paint_cost + labor_cost
        
        return {
            "liters_needed": liters_needed,
            "paint_cost": paint_cost,
            "work_hours": work_hours,
            "labor_cost": labor_cost,
            "total_cost": total_cost,
            "coverage_per_liter": coverage,
            "layers": layers
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