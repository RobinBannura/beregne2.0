from typing import Dict, Any, List
import httpx
import json
import re
import os
from datetime import datetime
from .base_agent import BaseAgent
from ..services.pricing_service import PricingService
from ..database import SessionLocal

class EnhancedRenovationAgent(BaseAgent):
    """
    househacker-assistent som hjelper kunder med:
    - Oppussingsrådgivning og kostnadsestimater
    - Profesjonelle pristilbud og prosjektregistrering
    - Lead-generering og kundeoppfølging
    - Faktabaserte svar innen oppussing
    """
    
    def __init__(self):
        super().__init__()
        self.agent_name = "renovation"
        # Initialize pricing service
        self.db = SessionLocal()
        self.pricing_service = PricingService(self.db)
        
        # Standardized styling for consistent appearance
        self.BRAND_COLOR = "#1f2937"  # househacker brand color
        self.LIGHT_BG = "#f9fafb"
        self.WHITE_BG = "#ffffff"
        self.BORDER_COLOR = "#e5e7eb"
        self.TEXT_GRAY = "#6b7280"
        
        # Faktabasert informasjon om househacker
        self.COMPANY_INFO = {
            "name": "househacker",
            "description": "Vi hjelper til i anbudsprosessen og sparer både kunden og entreprenøren for tid",
            "main_goal": "Definere prosjektet i samarbeid med kunden for at jobben skal bli bedre for alle parter",
            "products": {
                "solo": "Solo-pakke for enkle prosjekter",
                "direkte": "Direkte kontakt med utvalgte entreprenører", 
                "premium": "Premium-tjeneste med full oppfølging"
            },
            "services": [
                "Hjelp i anbudsprosessen",
                "Prosjektdefinisjon i samarbeid med kunde",
                "Tidsbesparelse for både kunde og entreprenør"
            ],
            "process": [
                "Kunde registrerer prosjekt",
                "Vi definerer prosjektet sammen med kunden",
                "Anbudsprosess med relevante entreprenører",
                "Kunde velger tilbyder"
            ]
        }
        
        # Legacy pricing constants (kept for backup calculations)
        self.LEGACY_HOURLY_RATES = {
            "maler": 850,
            "flislegger": 1100, 
            "gulvlegger": 800,
            "rørlegger": 1300,
            "elektriker": 1450,
            "tømrer": 850
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
            "board_id": "2004442153",
            "api_token": os.getenv("MONDAY_API_TOKEN", "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjUyNzE1NzU5NSwiYWFpIjoxMSwidWlkIjo3Njg2NzQ1OCwiaWFkIjoiMjAyNS0wNi0xNlQyMzowNDowOS4yNTlaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6Mjk4NTIzNTgsInJnbiI6ImV1YzEifQ.vUbawhibR9-r7Ex-6L2N_0FEVAeG9N8Sl88kQ14bvWw"),
            "lead_threshold": 50000  # Hvis prosjekt > 50k NOK, send til Monday
        }
    
    def _create_standard_response(self, title: str, total_cost: float, cost_details: str = "", 
                                included_items: list = None, notes: str = "", 
                                additional_info: str = "") -> str:
        """Create a standardized response with consistent styling"""
        included_items = included_items or []
        cost_inc_vat = total_cost * 1.25
        
        # Included items section
        included_section = ""
        if included_items:
            included_section = f"""
    <div style="background: {self.WHITE_BG}; padding: 16px; border-radius: 6px; border: 1px solid {self.BORDER_COLOR}; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Inkludert i prisen:</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px;">
            {''.join([f'<div>• {item}</div>' for item in included_items])}
        </div>
    </div>"""
        
        response = f"""
<div style="background: {self.LIGHT_BG}; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid {self.BRAND_COLOR};">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">{title}</h2>
    
    <div style="background: {self.BRAND_COLOR}; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Estimert kostnad</h3>
        <div style="font-size: 32px; font-weight: 600;">{total_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.9;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px; font-weight: 500;">{cost_inc_vat:,.0f} NOK inkl. mva</div>
        {cost_details}
    </div>
    {included_section}
    {additional_info}
    
    <p style="font-size: 14px; color: {self.TEXT_GRAY}; margin-top: 16px; line-height: 1.5;">
        {notes if notes else 'Basert på markedspriser Oslo/Viken 2025. Prisene kan variere ±10-15% avhengig av materialvalg og kompleksitet.'}
    </p>
</div>

<div style="background: {self.WHITE_BG}; border: 1px solid {self.BORDER_COLOR}; padding: 20px; border-radius: 6px; margin: 16px 0;">
    <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Vil du ha tilbud på dette prosjektet?</h3>
    <p style="margin-bottom: 16px; color: {self.TEXT_GRAY}; font-size: 14px;">
        Vi kobler deg med kvalifiserte håndverkere som kan gi deg konkrete tilbud basert på dine ønsker og behov.
    </p>
    
    <button onclick="window.open('https://househacker.no/kontakt', '_blank')" 
            style="background: {self.BRAND_COLOR}; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; margin-right: 8px;">
        Få tilbud
    </button>
    
    <button onclick="askQuestion('Jeg vil vite mer om kostnadene')" 
            style="background: transparent; color: {self.BRAND_COLOR}; border: 1px solid {self.BRAND_COLOR}; padding: 11px 23px; border-radius: 6px; font-size: 14px; cursor: pointer;">
        Flere detaljer
    </button>
</div>"""
        
        return response
    
    def _create_clarification_response(self, title: str, question: str, options: list) -> str:
        """Create a standardized clarification question with options"""
        options_html = ""
        for i, option in enumerate(options):
            options_html += f"""
            <button onclick="askQuestion('{option['query']}')" 
                    style="background: {self.WHITE_BG}; border: 2px solid {self.BRAND_COLOR}; color: {self.BRAND_COLOR}; 
                           padding: 12px 16px; border-radius: 6px; font-size: 14px; cursor: pointer; 
                           margin: 4px; display: block; width: 100%; text-align: left; transition: all 0.2s;"
                    onmouseover="this.style.background='{self.BRAND_COLOR}'; this.style.color='white';"
                    onmouseout="this.style.background='{self.WHITE_BG}'; this.style.color='{self.BRAND_COLOR}';">
                <strong>{option['title']}</strong><br>
                <small style="opacity: 0.8;">{option['description']}</small>
            </button>"""
        
        return f"""
<div style="background: {self.LIGHT_BG}; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid {self.BRAND_COLOR};">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">{title}</h2>
    
    <div style="background: {self.WHITE_BG}; padding: 20px; border-radius: 6px; border: 1px solid {self.BORDER_COLOR}; margin: 16px 0;">
        <p style="color: #374151; margin-bottom: 16px; font-size: 16px;">{question}</p>
        {options_html}
    </div>
    
    <p style="font-size: 14px; color: {self.TEXT_GRAY}; margin-top: 16px; line-height: 1.5;">
        Velg det alternativet som best beskriver ditt prosjekt, så gir jeg deg en nøyaktig kostnadsberegning.
    </p>
</div>"""
    
    def _is_ambiguous_query(self, query: str, analysis: Dict) -> bool:
        """Detect if a query needs clarification"""
        query_lower = query.lower()
        
        # Door-related ambiguity
        if any(word in query_lower for word in ['dør', 'dører']):
            # Check if it's clearly specified
            if not any(word in query_lower for word in ['ytterdør', 'innerdør', 'dørblad', 'karm']):
                return True
        
        # Window-related ambiguity  
        if any(word in query_lower for word in ['vindu', 'vinduer']):
            # Check if type is specified
            if not any(word in query_lower for word in ['standard', 'premium', 'takvindu', 'panorama']):
                # For basic window replacement, we can assume standard
                return False
        
        # Kitchen ambiguity
        if 'kjøkken' in query_lower:
            if not any(word in query_lower for word in ['ikea', 'skreddersydd', 'midt-segment', 'komplett']):
                return True
                
        return False
    
    async def _handle_ambiguous_query(self, query: str, analysis: Dict) -> Dict[str, Any]:
        """Handle ambiguous queries with intelligent clarification"""
        query_lower = query.lower()
        
        # Door clarification
        if any(word in query_lower for word in ['dør', 'dører']):
            # Extract number if present
            import re
            num_match = re.search(r'(\d+)', query_lower)
            num_doors = num_match.group(1) if num_match else "X"
            
            options = [
                {
                    "title": f"Innerdører - kun dørblad ({num_doors} stk)",
                    "description": "Skifte kun dørblad, beholde eksisterende karm. ~3,000 NOK per dør.",
                    "query": f"skifte {num_doors} innerdører kun dørblad"
                },
                {
                    "title": f"Innerdører - komplett med karm ({num_doors} stk)",
                    "description": "Skifte hele døren inkl. karm og montering. ~5,000-7,000 NOK per dør.",
                    "query": f"skifte {num_doors} innerdører komplett med karm"
                },
                {
                    "title": f"Ytterdører ({num_doors} stk)",
                    "description": "Skifte ytterdør(er) komplett. ~11,000-16,000 NOK per dør.",
                    "query": f"skifte {num_doors} ytterdører"
                }
            ]
            
            response = self._create_clarification_response(
                f"Dørskifte - {num_doors} dører",
                "For å gi deg riktig pris trenger jeg å vite hvilken type dører du vil skifte:",
                options
            )
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "requires_clarification": True,
                "total_cost": 0
            }
        
        # Kitchen clarification
        if 'kjøkken' in query_lower:
            options = [
                {
                    "title": "IKEA-nivå kjøkken",
                    "description": "Standard løsning med grunnleggende hvitevarer. ~80,000-120,000 NOK.",
                    "query": "kjøkken ikea nivå komplett"
                },
                {
                    "title": "Midt-segment kjøkken",
                    "description": "Bedre kvalitet (Sigdal/HTH-nivå). ~150,000-250,000 NOK.",
                    "query": "kjøkken midt-segment komplett"
                },
                {
                    "title": "Skreddersydd kjøkken",
                    "description": "Premium løsning med custom design. ~200,000-500,000 NOK.",
                    "query": "kjøkken skreddersydd komplett"
                }
            ]
            
            response = self._create_clarification_response(
                "Kjøkkenrenovering",
                "Hvilken type kjøkken planlegger du?",
                options
            )
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "requires_clarification": True,
                "total_cost": 0
            }
        
        # Default fallback
        return {
            "response": "Kan du være litt mer spesifikk i spørsmålet ditt? Det hjelper meg å gi deg en mer nøyaktig kalkulasjon.",
            "agent_used": self.agent_name,
            "requires_clarification": True,
            "total_cost": 0
        }

    async def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prosesserer oppussingsspørringer med hybrid AI-tilnærming"""
        try:
            analysis = self._analyze_renovation_query(query)
            
            # HYBRID AI: Check for ambiguous queries first
            if self._is_ambiguous_query(query, analysis):
                return await self._handle_ambiguous_query(query, analysis)
            
            if analysis["type"] == "full_project_estimate":
                if analysis.get("project_type") == "kjøkken_detaljert":
                    result = await self._provide_kitchen_breakdown(analysis, query)
                elif analysis.get("project_type") == "vinduer_dorer":
                    result = await self._handle_windows_doors_work(analysis, query)
                else:
                    result = await self._calculate_full_project(analysis, query)
            elif analysis["type"] == "material_and_labor":
                result = await self._calculate_material_and_labor(analysis, query)
            elif analysis["type"] == "price_comparison":
                result = await self._compare_suppliers(analysis, query)
            elif analysis["type"] == "painting_specific":
                result = await self._handle_painting_inquiry(analysis, query)
            elif analysis["type"] == "electrical_work":
                result = await self._handle_electrical_work(analysis, query)
            elif analysis["type"] == "groundwork":
                result = await self._handle_groundwork(analysis, query)
            elif analysis["type"] == "flooring_work":
                result = await self._handle_flooring_work(analysis, query)
            elif analysis["type"] == "carpentry_work":
                result = await self._handle_carpentry_work(analysis, query)
            elif analysis["type"] == "roofing_cladding_work":
                result = await self._handle_roofing_cladding_work(analysis, query)
            elif analysis["type"] == "insulation_work":
                result = await self._handle_insulation_work(analysis, query)
            elif analysis["type"] == "windows_doors_work":
                result = await self._handle_windows_doors_work(analysis, query)
            elif analysis["type"] == "detailed_breakdown":
                result = await self._provide_detailed_breakdown(analysis, query)
            elif analysis["type"] == "quote_request":
                result = await self._handle_quote_request(analysis, query)
            elif analysis["type"] == "project_registration":
                result = await self._handle_project_registration(analysis, query)
            elif analysis["type"] == "about_househacker":
                result = await self._explain_househacker_services(analysis, query)
            elif analysis["type"] == "needs_clarification" or analysis["needs_clarification"]:
                result = await self._ask_clarifying_questions(analysis, query)
            else:
                result = await self._basic_calculation(analysis, query)
            
            # Lead-generering for alle kalkulasjoner over 10,000 NOK eller hvis brukeren spør om tilbud
            total_cost = result.get("total_cost", 0)
            if total_cost > 10000 or analysis["type"] in ["quote_request", "full_project_estimate"]:
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
        
        # Route bathroom projects to new database-driven calculation
        if project_type == "bad_komplett":
            return await self._calculate_bathroom_project(analysis, query)
        
        project_config = self.PROJECT_TYPES.get(project_type)
        total_material_cost = 0
        total_labor_cost = 0
        total_time_hours = 0
        
        detailed_breakdown = {}
        
        # Beregn for hvert material/arbeidsområde med database-priser
        if project_config:
            for material in project_config["materialer"]:
                mat_calc = self._calculate_material_with_labor(material, area)
                detailed_breakdown[material] = mat_calc
                total_material_cost += mat_calc["material_cost"]
                total_labor_cost += mat_calc["labor_cost"]
                total_time_hours += mat_calc["hours"]
        else:
            # Fallback til grunnleggende materialer
            for material in ["maling", "fliser"]:
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
        
        # Generer enkel respons med kun totalkostnad
        response = f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #374151;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Komplett {project_type.replace('_', ' ').title()} - {area:.0f} m²</h2>
    
    <div style="background: #374151; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Estimert kostnad</h3>
        <div style="font-size: 32px; font-weight: 600;">{total_cost:,.0f} NOK</div>
        <p style="margin-top: 8px; opacity: 0.9; font-size: 14px;">Estimert tidsbruk: {total_time_hours:.0f} timer ({total_time_hours/8:.1f} arbeidsdager)</p>
    </div>
    
    <p style="font-size: 14px; color: #6b7280; margin-top: 16px; line-height: 1.5;">
        Prisen inkluderer materialer, arbeid, utstyr, prosjektledelse og uforutsette kostnader. 
        Faktiske priser kan variere ±15% avhengig av leverandør og kompleksitet.
    </p>
</div>

<div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 20px; border-radius: 6px; margin: 16px 0;">
    <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Ønsker du tilbud på prosjektet?</h3>
    <p style="margin-bottom: 16px; color: #6b7280; font-size: 14px;">Vi kobler deg med kvalifiserte håndverkere som kan gi deg konkrete tilbud basert på dine ønsker.</p>
    
    <button onclick="window.open('https://househacker.no/kontakt', '_blank')" 
            style="background: #374151; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; margin-right: 8px;">
        Få tilbud
    </button>
    
    <button onclick="askQuestion('Jeg vil vite mer om kostnadene')" 
            style="background: transparent; color: #374151; border: 1px solid #374151; padding: 11px 23px; border-radius: 6px; font-size: 14px; cursor: pointer;">
        Flere detaljer
    </button>
</div>"""
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": total_cost,
            "material_cost": total_material_cost,
            "labor_cost": total_labor_cost,
            "estimated_hours": total_time_hours,
            "breakdown": detailed_breakdown
        }

    async def _calculate_bathroom_project(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Beregner komplett badprosjekt med database-priser"""
        area = analysis.get("area", 6)  # Default 6m² bathroom
        query_lower = query.lower()
        
        try:
            # Determine calculation approach based on area and query
            if area <= 4:
                # Use 4m² package
                package_service = "bad_totalrenovering_4m2"
                package_area = 4
            elif area <= 8:
                # Use 8m² package
                package_service = "bad_totalrenovering_8m2"
                package_area = 8
            elif area <= 12:
                # Use 12m² package
                package_service = "bad_totalrenovering_12m2"
                package_area = 12
            else:
                # Use component-based calculation for larger bathrooms
                return await self._calculate_large_bathroom_components(area, query_lower)
            
            # Get package pricing from database
            package_result = self.pricing_service.get_service_price(package_service)
            
            if "error" in package_result:
                # Fallback to component-based calculation
                return await self._calculate_bathroom_components(area, query_lower)
            
            # Extract package pricing
            package_price = package_result.get("unit_price", {}).get("recommended_price", 0)
            
            # Scale price based on actual area vs package area
            area_factor = area / package_area
            scaled_price = package_price * area_factor
            
            # Generate response
            response = f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #1f2937;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Komplett Badrenovering - {area:.0f} m²</h2>
    
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Estimert kostnad</h3>
        <div style="font-size: 32px; font-weight: 600;">{scaled_price:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.9;">eksl. mva</div>
        <div style="font-size: 20px; margin-top: 4px; font-weight: 500;">{scaled_price * 1.25:,.0f} NOK inkl. mva</div>
        <p style="margin-top: 8px; opacity: 0.9; font-size: 14px;">Per m²: {scaled_price / area:,.0f} NOK/m²</p>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 6px; border: 1px solid #e5e7eb; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Inkludert i totalprisen:</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px;">
            <div>• Riving og avfallshåndtering</div>
            <div>• Membran og tetting</div>
            <div>• Flislegging (vegg og gulv)</div>
            <div>• Rørleggerarbeid</div>
            <div>• Elektriker</div>
            <div>• Maling (våtrom)</div>
            <div>• WC og servant</div>
            <div>• Dusjkabinett</div>
            <div>• Ventilasjon</div>
            <div>• Gulvvarme (standard)</div>
        </div>
    </div>
    
    <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 16px; border-radius: 6px; margin: 16px 0;">
        <h4 style="color: #92400e; margin-bottom: 8px;">Prissammenligning per m²:</h4>
        <p style="color: #92400e; font-size: 14px; margin: 0;">
            4m² bad: ~88,000 NOK/m² • 8m² bad: ~54,000 NOK/m² • 12m² bad: ~35,000 NOK/m²<br>
            <strong>Små bad har høyere m²-pris pga fast teknisk overhead</strong>
        </p>
    </div>
    
    <p style="font-size: 14px; color: #6b7280; margin-top: 16px; line-height: 1.5;">
        Prisen er basert på {package_area}m² pakkeprising skalert til {area:.0f}m². 
        Inkluderer alle materialer, arbeid og koordinering. Prisene kan variere ±10-15% avhengig av materialvalg og kompleksitet.
    </p>
</div>

<div style="background: #ffffff; border: 1px solid #e5e7eb; padding: 20px; border-radius: 6px; margin: 16px 0;">
    <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Vil du ha tilbud på badrenovering?</h3>
    <p style="margin-bottom: 16px; color: #6b7280; font-size: 14px;">
        Vi kobler deg med kvalifiserte håndverkere som kan gi deg konkrete tilbud basert på dine ønsker og behov.
    </p>
    
    <button onclick="window.open('https://househacker.no/kontakt', '_blank')" 
            style="background: #1f2937; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; margin-right: 8px;">
        Få tilbud på badrenovering
    </button>
    
    <button onclick="askQuestion('Jeg vil vite mer om badkostnader')" 
            style="background: transparent; color: #1f2937; border: 1px solid #1f2937; padding: 11px 23px; border-radius: 6px; font-size: 14px; cursor: pointer;">
        Detaljert kostnadsfordeling
    </button>
</div>"""
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": scaled_price,
                "area": area,
                "price_per_m2": scaled_price / area,
                "package_used": package_service,
                "pricing_source": "database_package"
            }
            
        except Exception as e:
            # Fallback to component-based calculation
            return await self._calculate_bathroom_components(area, query_lower)

    async def _calculate_bathroom_components(self, area: float, query_lower: str) -> Dict[str, Any]:
        """Component-based bathroom calculation as fallback"""
        try:
            components = [
                ("bad_riving_avfall", area),
                ("bad_membran", area),
                ("bad_flislegging_arbeid", area),
                ("bad_fliser_material", area),
                ("bad_elektriker", area),
                ("bad_rorlegger", area),
                ("bad_maler_vatrom", area)
            ]
            
            total_cost = 0
            component_breakdown = []
            
            for service_name, component_area in components:
                result = self.pricing_service.get_service_price(service_name, area=component_area)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_cost += cost
                    
                    component_breakdown.append({
                        "service": service_name,
                        "cost": cost,
                        "description": result.get("service_description", service_name)
                    })
            
            response = f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #1f2937;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Badrenovering (komponentbasert) - {area:.0f} m²</h2>
    
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Total kostnad</h3>
        <div style="font-size: 32px; font-weight: 600;">{total_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.9;">eksl. mva</div>
        <div style="font-size: 20px; margin-top: 4px; font-weight: 500;">{total_cost * 1.25:,.0f} NOK inkl. mva</div>
    </div>
    
    <h3 style="color: #374151; margin-bottom: 12px;">Kostnadsfordeling:</h3>
    <div style="background: #ffffff; padding: 16px; border-radius: 6px; border: 1px solid #e5e7eb;">"""
            
            for component in component_breakdown:
                service_display = component["service"].replace("bad_", "").replace("_", " ").title()
                response += f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; padding: 4px 0; border-bottom: 1px solid #f3f4f6;">
            <span>{service_display}</span>
            <strong>{component['cost']:,.0f} NOK</strong>
        </div>"""
            
            response += f"""
    </div>
    
    <p style="font-size: 14px; color: #6b7280; margin-top: 16px; line-height: 1.5;">
        Komponentbasert beregning for {area:.0f}m² bad basert på aktuelle markedspriser i Oslo/Viken.
    </p>
</div>"""
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": total_cost,
                "area": area,
                "components": component_breakdown,
                "pricing_source": "database_components"
            }
            
        except Exception as e:
            # Ultimate fallback
            fallback_cost = area * 45000  # 45k per m² fallback
            return {
                "response": f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827;">Badrenovering - {area:.0f} m²</h2>
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <div style="font-size: 32px; font-weight: 600;">{fallback_cost:,.0f} NOK</div>
    </div>
    <p>Estimat basert på gjennomsnittspriser for badrenovering.</p>
</div>""",
                "agent_used": self.agent_name,
                "total_cost": fallback_cost,
                "area": area,
                "pricing_source": "fallback"
            }

    async def _calculate_large_bathroom_components(self, area: float, query_lower: str) -> Dict[str, Any]:
        """Handle large bathrooms (>12m²) with component scaling"""
        return await self._calculate_bathroom_components(area, query_lower)

    async def _handle_electrical_work(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Handle electrical work specific queries"""
        query_lower = query.lower()
        area = analysis.get("area")
        
        try:
            # Determine what type of electrical work is requested
            if any(word in query_lower for word in ['timepris', 'time', 'per time']):
                return await self._calculate_electrician_hourly_rate(query_lower)
            elif any(word in query_lower for word in ['stikkontakt', 'kontakt']):
                return await self._calculate_electrical_outlets(query_lower, area)
            elif any(word in query_lower for word in ['downlight', 'spot', 'punkter']):
                return await self._calculate_downlights(query_lower, area)
            elif any(word in query_lower for word in ['sikringsskap', 'skap', 'kurs']):
                return await self._calculate_electrical_panel(query_lower)
            elif any(word in query_lower for word in ['gulvvarme', 'varmekabler']):
                return await self._calculate_floor_heating(query_lower, area)
            elif any(word in query_lower for word in ['elbillader', 'lader']):
                return await self._calculate_ev_charger(query_lower)
            elif any(word in query_lower for word in ['el-anlegg', 'el anlegg', 'komplett']):
                return await self._calculate_complete_electrical_system(query_lower, area)
            else:
                # General electrical work
                return await self._calculate_general_electrical_work(query_lower, area)
                
        except Exception as e:
            return {
                "response": f"Beklager, jeg kunne ikke beregne elektriker-kostnadene: {str(e)}",
                "agent_used": self.agent_name,
                "total_cost": 0,
                "error": str(e)
            }

    async def _calculate_electrician_hourly_rate(self, query_lower: str) -> Dict[str, Any]:
        """Calculate electrician hourly rates"""
        try:
            result = self.pricing_service.get_service_price("elektriker_timepris_montor")
            
            if "error" in result:
                raise Exception("Could not get hourly rate")
            
            hourly_rate = result.get("unit_price", {}).get("recommended_price", 900)
            min_rate = result.get("unit_price", {}).get("min_price", 700)
            max_rate = result.get("unit_price", {}).get("max_price", 1100)
            
            response = f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #1f2937;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Timepris Elektriker - Oslo</h2>
    
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Timepris montør</h3>
        <div style="font-size: 32px; font-weight: 600;">{hourly_rate:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.9;">per time eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px; font-weight: 500;">{hourly_rate * 1.25:,.0f} NOK inkl. mva</div>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 6px; border: 1px solid #e5e7eb; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Prisintervall Oslo:</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px;">
            <div>• Minimum: {min_rate:,.0f} NOK/time</div>
            <div>• Anbefalt: {hourly_rate:,.0f} NOK/time</div>
            <div>• Maksimum: {max_rate:,.0f} NOK/time</div>
            <div>• Oppstart: 500-850 NOK</div>
        </div>
    </div>
    
    <p style="font-size: 14px; color: #6b7280; margin-top: 16px; line-height: 1.5;">
        Prisene varierer basert på kompleksitet og leverandør. Storbyspenn 700-1300 kr; Oslo eksempler 900-1500 kr. 
        Oppstart/servicebil ofte inkludert i første time.
    </p>
</div>"""
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": hourly_rate,
                "hourly_rate": hourly_rate,
                "pricing_source": "database"
            }
            
        except Exception as e:
            return await self._electrical_fallback("timepris elektriker", 900)

    async def _calculate_electrical_outlets(self, query_lower: str, area: float) -> Dict[str, Any]:
        """Calculate cost for electrical outlets"""
        try:
            # Extract number of outlets from query
            import re
            number_match = re.search(r'(\d+)', query_lower)
            num_outlets = int(number_match.group(1)) if number_match else 5
            
            # Use package pricing if 5 or more outlets
            if num_outlets >= 5:
                result = self.pricing_service.get_service_price("stikkontakt_pakke_5_stk")
                if "error" not in result:
                    package_cost = result.get("unit_price", {}).get("recommended_price", 4400)
                    # Scale for different quantities
                    total_cost = package_cost * (num_outlets / 5)
                else:
                    raise Exception("Package pricing not available")
            else:
                # Individual outlet pricing
                result = self.pricing_service.get_service_price("ekstra_stikkontakt_dobbel")
                if "error" not in result:
                    outlet_cost = result.get("unit_price", {}).get("recommended_price", 950)
                    total_cost = outlet_cost * num_outlets
                else:
                    raise Exception("Individual pricing not available")
            
            cost_inc_vat = total_cost * 1.25
            cost_per_outlet = total_cost / num_outlets
            
            response = f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #1f2937;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Stikkontakter - {num_outlets} stk</h2>
    
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Total kostnad</h3>
        <div style="font-size: 32px; font-weight: 600;">{total_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.9;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px; font-weight: 500;">{cost_inc_vat:,.0f} NOK inkl. mva</div>
        <p style="margin-top: 8px; opacity: 0.9; font-size: 14px;">Per stikkontakt: {cost_per_outlet:,.0f} NOK</p>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 6px; border: 1px solid #e5e7eb; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Inkludert:</h3>
        <div>• Doble stikkontakter</div>
        <div>• Materialer inkludert</div>
        <div>• Montering og tilkobling</div>
        <div>• {'Pakkerabatt ved ' + str(num_outlets) + ' kontakter' if num_outlets >= 5 else 'Enkeltpris'}</div>
    </div>
    
    <p style="font-size: 14px; color: #6b7280; margin-top: 16px; line-height: 1.5;">
        Basert på markedspriser Oslo/Viken 2025. {'Pakkeløsning gir lavere pris per kontakt' if num_outlets >= 5 else 'Vurder pakkeløsning ved flere kontakter'}.
    </p>
</div>"""
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": total_cost,
                "num_outlets": num_outlets,
                "cost_per_outlet": cost_per_outlet,
                "pricing_source": "database"
            }
            
        except Exception as e:
            return await self._electrical_fallback(f"{num_outlets} stikkontakter", num_outlets * 950)

    async def _electrical_fallback(self, service_name: str, fallback_cost: float) -> Dict[str, Any]:
        """Fallback for electrical calculations"""
        return {
            "response": f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827;">{service_name.title()}</h2>
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <div style="font-size: 32px; font-weight: 600;">{fallback_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px;">estimat eks. mva</div>
    </div>
    <p>Estimat basert på gjennomsnittspriser for elektrikerarbeid i Oslo.</p>
</div>""",
            "agent_used": self.agent_name,
            "total_cost": fallback_cost,
            "pricing_source": "fallback"
        }

    async def _calculate_downlights(self, query_lower: str, area: float) -> Dict[str, Any]:
        """Calculate downlight installation costs"""
        # Implementation for downlights
        return await self._electrical_fallback("downlights", 15000)

    async def _calculate_electrical_panel(self, query_lower: str) -> Dict[str, Any]:
        """Calculate electrical panel costs"""
        # Implementation for electrical panels
        return await self._electrical_fallback("sikringsskap", 18000)

    async def _calculate_floor_heating(self, query_lower: str, area: float) -> Dict[str, Any]:
        """Calculate floor heating costs"""
        # Implementation for floor heating
        if area:
            cost = area * 1075  # Average price from database
            return await self._electrical_fallback(f"gulvvarme {area}m²", cost)
        return await self._electrical_fallback("gulvvarme", 10000)

    async def _calculate_ev_charger(self, query_lower: str) -> Dict[str, Any]:
        """Calculate EV charger installation costs"""
        # Implementation for EV charger
        return await self._electrical_fallback("elbillader", 15000)

    async def _calculate_complete_electrical_system(self, query_lower: str, area: float) -> Dict[str, Any]:
        """Calculate complete electrical system costs"""
        # Implementation for complete electrical systems
        if area:
            cost = area * 1250  # Average price from database
            return await self._electrical_fallback(f"komplett el-anlegg {area}m²", cost)
        return await self._electrical_fallback("komplett el-anlegg", 130000)

    async def _calculate_general_electrical_work(self, query_lower: str, area: float) -> Dict[str, Any]:
        """General electrical work calculation"""
        return await self._electrical_fallback("elektrikerarbeid", 8000)

    async def _handle_groundwork(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Handle groundwork specific queries"""
        query_lower = query.lower()
        area = analysis.get("area")
        
        try:
            # Determine what type of groundwork is requested
            if any(word in query_lower for word in ['graving', 'grave', 'utgraving']):
                return await self._calculate_excavation(query_lower, area)
            elif any(word in query_lower for word in ['grunnmur', 'fundament']):
                return await self._calculate_foundation(query_lower, area)
            elif any(word in query_lower for word in ['sprengning', 'fjell']):
                return await self._calculate_rock_blasting(query_lower, area)
            elif any(word in query_lower for word in ['drenering']):
                return await self._calculate_drainage(query_lower, area)
            elif any(word in query_lower for word in ['plate på mark', 'betongplate']):
                return await self._calculate_concrete_slab(query_lower, area)
            elif any(word in query_lower for word in ['gravemaskin', 'maskin']):
                return await self._calculate_excavator_rental(query_lower)
            elif any(word in query_lower for word in ['komplett', 'fundamentering']):
                return await self._calculate_complete_foundation(query_lower, area)
            else:
                # General groundwork
                return await self._calculate_general_groundwork(query_lower, area)
                
        except Exception as e:
            return {
                "response": f"Beklager, jeg kunne ikke beregne grunnarbeid-kostnadene: {str(e)}",
                "agent_used": self.agent_name,
                "total_cost": 0,
                "error": str(e)
            }

    async def _calculate_excavation(self, query_lower: str, area: float) -> Dict[str, Any]:
        """Calculate excavation costs"""
        try:
            if not area:
                area = 200  # Default area if not specified
            
            # Choose service based on complexity
            if any(word in query_lower for word in ['ny bolig', 'bolig', 'hus', 'planering']):
                service = "graving_ny_bolig_inkl_planering"
                complexity = "complex"
            else:
                service = "graving_generell_utgraving"
                complexity = "standard"
            
            result = self.pricing_service.get_service_price(service, area=area)
            
            if "error" in result:
                raise Exception("Could not get excavation pricing")
            
            total_cost = result.get("total_cost", {}).get("recommended", 0)
            unit_price = result.get("unit_price", {}).get("recommended_price", 0)
            min_price = result.get("unit_price", {}).get("min_price", 0)
            max_price = result.get("unit_price", {}).get("max_price", 0)
            
            response = f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #1f2937;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Graving av tomt - {area:.0f} m²</h2>
    
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Total kostnad</h3>
        <div style="font-size: 32px; font-weight: 600;">{total_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.9;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px; font-weight: 500;">{total_cost * 1.25:,.0f} NOK inkl. mva</div>
        <p style="margin-top: 8px; opacity: 0.9; font-size: 14px;">Per m²: {unit_price:,.0f} NOK/m²</p>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 6px; border: 1px solid #e5e7eb; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">📊 Prisintervall:</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px;">
            <div>• Minimum: {min_price:,.0f} NOK/m²</div>
            <div>• Anbefalt: {unit_price:,.0f} NOK/m²</div>
            <div>• Maksimum: {max_price:,.0f} NOK/m²</div>
            <div>• Type: {complexity.title()} graving</div>
        </div>
    </div>
    
    <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 16px; border-radius: 6px; margin: 16px 0;">
        <h4 style="color: #92400e; margin-bottom: 8px;">⚠️ Faktorer som påvirker pris:</h4>
        <p style="color: #92400e; font-size: 14px; margin: 0;">
            • Grunnforhold (fjell, leire, sand)<br>
            • Tilkomst og terreng<br>
            • Volum og kompleksitet<br>
            • Årstid og værforhold
        </p>
    </div>
    
    <p style="font-size: 14px; color: #6b7280; margin-top: 16px; line-height: 1.5;">
        Basert på markedspriser Oslo/Viken 2025. {'Kompleks graving med planering' if complexity == 'complex' else 'Standard utgraving'}. 
        Store spredninger skyldes lokale grunnforhold og tilkomst.
    </p>
</div>"""
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": total_cost,
                "area": area,
                "unit_price": unit_price,
                "service_type": service,
                "pricing_source": "database"
            }
            
        except Exception as e:
            return await self._groundwork_fallback(f"graving {area:.0f}m²", area * 2500)

    async def _calculate_foundation(self, query_lower: str, area: float) -> Dict[str, Any]:
        """Calculate foundation costs"""
        try:
            if not area:
                area = 120  # Default house size
            
            result = self.pricing_service.get_service_price("grunnmur_betong_leca", area=area)
            
            if "error" in result:
                raise Exception("Could not get foundation pricing")
            
            total_cost = result.get("total_cost", {}).get("recommended", 0)
            unit_price = result.get("unit_price", {}).get("recommended_price", 0)
            
            # Check if package pricing is available and beneficial
            package_result = self.pricing_service.get_service_price("komplett_grunnmur_pakke_120m2")
            package_available = "error" not in package_result
            
            response = f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #1f2937;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Grunnmur - {area:.0f} m²</h2>
    
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Grunnmur kostnad</h3>
        <div style="font-size: 32px; font-weight: 600;">{total_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.9;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px; font-weight: 500;">{total_cost * 1.25:,.0f} NOK inkl. mva</div>
        <p style="margin-top: 8px; opacity: 0.9; font-size: 14px;">Per m²: {unit_price:,.0f} NOK/m²</p>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 6px; border: 1px solid #e5e7eb; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Inkludert i prisen:</h3>
        <div>• Betong/Leca blokker</div>
        <div>• Armering og fundamentering</div>
        <div>• Grunnleggende isolasjon</div>
        <div>• Standard høyde grunnmur</div>
    </div>"""
            
            if package_available:
                package_cost = package_result.get("unit_price", {}).get("recommended_price", 0)
                response += f"""
    <div style="background: #e0f2fe; border: 1px solid #0288d1; padding: 16px; border-radius: 6px; margin: 16px 0;">
        <h4 style="color: #0277bd; margin-bottom: 8px;">📦 Pakkeløsning tilgjengelig:</h4>
        <p style="color: #0277bd; font-size: 14px; margin: 0;">
            Komplett fundamentering (120m²): {package_cost:,.0f} NOK<br>
            Inkluderer graving + grunnmur + drenering
        </p>
    </div>"""
            
            response += f"""
    <p style="font-size: 14px; color: #6b7280; margin-top: 16px; line-height: 1.5;">
        Grunnmur i betong/Leca, snitt ≈ 2500 kr/m² grunnflate. 
        Varierer med høyde, isolasjonskrav og grunnforhold.
    </p>
</div>"""
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": total_cost,
                "area": area,
                "unit_price": unit_price,
                "pricing_source": "database"
            }
            
        except Exception as e:
            return await self._groundwork_fallback(f"grunnmur {area:.0f}m²", area * 2500)

    async def _groundwork_fallback(self, service_name: str, fallback_cost: float) -> Dict[str, Any]:
        """Fallback for groundwork calculations"""
        return {
            "response": f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827;">🏗️ {service_name.title()}</h2>
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <div style="font-size: 32px; font-weight: 600;">{fallback_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px;">estimat eks. mva</div>
    </div>
    <p>Estimat basert på gjennomsnittspriser for grunnarbeider i Oslo.</p>
</div>""",
            "agent_used": self.agent_name,
            "total_cost": fallback_cost,
            "pricing_source": "fallback"
        }

    # Placeholder methods for other groundwork types
    async def _calculate_rock_blasting(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._groundwork_fallback("fjellsprengning", (area or 20) * 250)
    
    async def _calculate_drainage(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._groundwork_fallback("drenering", (area or 40) * 6750)
    
    async def _calculate_concrete_slab(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._groundwork_fallback("plate på mark", (area or 100) * 1650)
    
    async def _calculate_excavator_rental(self, query_lower: str) -> Dict[str, Any]:
        return await self._groundwork_fallback("gravemaskin", 1500)
    
    async def _calculate_complete_foundation(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._groundwork_fallback("komplett fundamentering", (area or 120) * 3500)
    
    async def _calculate_general_groundwork(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._groundwork_fallback("grunnarbeider", 50000)

    async def _handle_flooring_work(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Handle flooring work specific queries"""
        query_lower = query.lower()
        area = analysis.get("area")
        
        try:
            # Determine what type of flooring work is requested
            if any(word in query_lower for word in ['parkett', 'parkettgulv']):
                if any(word in query_lower for word in ['fiskebein', 'mønster', 'stav']):
                    return await self._calculate_parquet_pattern(query_lower, area)
                else:
                    return await self._calculate_parquet_straight(query_lower, area)
            elif any(word in query_lower for word in ['laminat']):
                return await self._calculate_laminate(query_lower, area)
            elif any(word in query_lower for word in ['vinyl']):
                return await self._calculate_vinyl_flooring(query_lower, area)
            elif any(word in query_lower for word in ['epoxy', 'epoksygulv']):
                return await self._calculate_epoxy_flooring(query_lower, area)
            elif any(word in query_lower for word in ['microsement']):
                return await self._calculate_microsement_flooring(query_lower, area)
            elif any(word in query_lower for word in ['avretting', 'gulvavretting', 'flytsparkel']):
                return await self._calculate_floor_leveling(query_lower, area)
            elif any(word in query_lower for word in ['sliping', 'gulvsliping']):
                return await self._calculate_floor_sanding(query_lower, area)
            elif any(word in query_lower for word in ['varmekabler gulv', 'gulvvarme']):
                return await self._calculate_floor_heating_flooring(query_lower, area)
            elif any(word in query_lower for word in ['komplett', 'helrenovering']):
                return await self._calculate_complete_flooring_project(query_lower, area)
            else:
                # General flooring work
                return await self._calculate_general_flooring(query_lower, area)
                
        except Exception as e:
            return {
                "response": f"Beklager, jeg kunne ikke beregne gulvarbeid-kostnadene: {str(e)}",
                "agent_used": self.agent_name,
                "total_cost": 0,
                "error": str(e)
            }

    async def _calculate_parquet_straight(self, query_lower: str, area: float) -> Dict[str, Any]:
        """Calculate straight parquet flooring costs"""
        try:
            if not area:
                area = 25  # Default area if not specified
            
            result = self.pricing_service.get_service_price("parkett_legging_rettmonster", area=area)
            
            if "error" in result:
                raise Exception("Could not get parquet pricing")
            
            total_cost = result.get("total_cost", {}).get("recommended", 0)
            unit_price = result.get("unit_price", {}).get("recommended_price", 0)
            min_price = result.get("unit_price", {}).get("min_price", 0)
            max_price = result.get("unit_price", {}).get("max_price", 0)
            
            # Check if package pricing is available
            package_available = False
            if area >= 25 and area <= 35:
                package_result = self.pricing_service.get_service_price("komplett_parkett_30m2_pakke")
                package_available = "error" not in package_result
            
            response = f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #8b4513;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Parkett (rettmønster) - {area:.0f} m²</h2>
    
    <div style="background: #8b4513; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Parkettlegging kostnad</h3>
        <div style="font-size: 32px; font-weight: 600;">{total_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.9;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px; font-weight: 500;">{total_cost * 1.25:,.0f} NOK inkl. mva</div>
        <p style="margin-top: 8px; opacity: 0.9; font-size: 14px;">Per m²: {unit_price:,.0f} NOK/m²</p>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 6px; border: 1px solid #e5e7eb; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">📊 Prisintervall:</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px;">
            <div>• Minimum: {min_price:,.0f} NOK/m²</div>
            <div>• Anbefalt: {unit_price:,.0f} NOK/m²</div>
            <div>• Maksimum: {max_price:,.0f} NOK/m²</div>
            <div>• Type: Rettmønster parkett</div>
        </div>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 6px; border: 1px solid #e5e7eb; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Inkludert i prisen:</h3>
        <div>• Professjonell parkettlegging</div>
        <div>• Underlag og lim</div>
        <div>• Kantlister (grunnleggende)</div>
        <div>• Overflatebehandling (standard)</div>
    </div>"""
            
            if package_available:
                package_cost = package_result.get("unit_price", {}).get("recommended_price", 0)
                response += f"""
    <div style="background: #e8f5e8; border: 1px solid #4caf50; padding: 16px; border-radius: 6px; margin: 16px 0;">
        <h4 style="color: #2e7d32; margin-bottom: 8px;">📦 Pakkeløsning tilgjengelig:</h4>
        <p style="color: #2e7d32; font-size: 14px; margin: 0;">
            Komplett parkett 30m²: {package_cost:,.0f} NOK<br>
            Inkluderer avretting + parkett + finish
        </p>
    </div>"""
            
            response += f"""
    <p style="font-size: 14px; color: #6b7280; margin-top: 16px; line-height: 1.5;">
        Startpris 300 kr hos Ditt Tregulv; parkett generelt min. 400 kr på Mittanbud. 
        Små rom (<10m²) eller kompliserte geometrier kan gi påslag.
    </p>
</div>"""
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": total_cost,
                "area": area,
                "unit_price": unit_price,
                "flooring_type": "parkett_rettmønster",
                "pricing_source": "database"
            }
            
        except Exception as e:
            return await self._flooring_fallback(f"parkett {area:.0f}m²", area * 400)

    async def _calculate_laminate(self, query_lower: str, area: float) -> Dict[str, Any]:
        """Calculate laminate flooring costs"""
        try:
            if not area:
                area = 40  # Default area for laminate
            
            result = self.pricing_service.get_service_price("laminat_legging_standard", area=area)
            
            if "error" in result:
                raise Exception("Could not get laminate pricing")
            
            total_cost = result.get("total_cost", {}).get("recommended", 0)
            unit_price = result.get("unit_price", {}).get("recommended_price", 0)
            
            response = f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #6b46c1;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Laminatgulv - {area:.0f} m²</h2>
    
    <div style="background: #6b46c1; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white; margin-bottom: 8px; font-size: 16px; font-weight: 500;">Laminat kostnad</h3>
        <div style="font-size: 32px; font-weight: 600;">{total_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px; opacity: 0.9;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px; font-weight: 500;">{total_cost * 1.25:,.0f} NOK inkl. mva</div>
        <p style="margin-top: 8px; opacity: 0.9; font-size: 14px;">Per m²: {unit_price:,.0f} NOK/m²</p>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 6px; border: 1px solid #e5e7eb; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">✅ Fordeler med laminat:</h3>
        <div>• Rimeligste gulvalternativ (150-400 kr/m²)</div>
        <div>• Rask og enkel installasjon</div>
        <div>• Slitesterkt og lettstelt</div>
        <div>• Stort utvalg av design</div>
    </div>
    
    <p style="font-size: 14px; color: #6b7280; margin-top: 16px; line-height: 1.5;">
        Enkleste gulvtyper 150-200 kr; komplette installasjoner opp til 400 kr/m². 
        Kvadratmeterkostnaden synker ved store flater.
    </p>
</div>"""
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": total_cost,
                "area": area,
                "unit_price": unit_price,
                "flooring_type": "laminat",
                "pricing_source": "database"
            }
            
        except Exception as e:
            return await self._flooring_fallback(f"laminat {area:.0f}m²", area * 275)

    async def _flooring_fallback(self, service_name: str, fallback_cost: float) -> Dict[str, Any]:
        """Fallback for flooring calculations"""
        return {
            "response": f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827;">{service_name.title()}</h2>
    <div style="background: #6b46c1; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <div style="font-size: 32px; font-weight: 600;">{fallback_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px;">estimat eks. mva</div>
    </div>
    <p>Estimat basert på gjennomsnittspriser for gulvarbeider i Oslo.</p>
</div>""",
            "agent_used": self.agent_name,
            "total_cost": fallback_cost,
            "pricing_source": "fallback"
        }

    # Placeholder methods for other flooring types
    async def _calculate_parquet_pattern(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._flooring_fallback("parkett fiskebein", (area or 25) * 900)
    
    async def _calculate_vinyl_flooring(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._flooring_fallback("vinylgulv", (area or 10) * 950)
    
    async def _calculate_epoxy_flooring(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._flooring_fallback("epoksygulv", (area or 20) * 750)
    
    async def _calculate_microsement_flooring(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._flooring_fallback("microsement", (area or 15) * 1400)
    
    async def _calculate_floor_leveling(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._flooring_fallback("gulvavretting", (area or 30) * 450)
    
    async def _calculate_floor_sanding(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._flooring_fallback("gulvsliping", (area or 25) * 375)
    
    async def _calculate_floor_heating_flooring(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._flooring_fallback("gulvvarme", (area or 20) * 1075)
    
    async def _calculate_complete_flooring_project(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._flooring_fallback("komplett gulvprosjekt", (area or 40) * 2000)
    
    async def _calculate_general_flooring(self, query_lower: str, area: float) -> Dict[str, Any]:
        return await self._flooring_fallback("gulvarbeider", (area or 30) * 600)

    async def _provide_kitchen_breakdown(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Gir detaljert kjøkkenrenovering guide med realistiske kostnader"""
        response = f"""
<div style="background: #f8f9fa; padding: 20px; border-radius: 6px; margin: 16px 0;">
    <h2 style="color: #333; margin-bottom: 16px; font-size: 18px; font-weight: 600;">Kjøkkenrenovering - Oslo-området</h2>
    
    <p style="margin-bottom: 16px; color: #555; line-height: 1.5;">
        Typisk oppsett og kostnader for kjøkkenrenovering:
    </p>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">1. Riving av eksisterende kjøkken</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">
            <li style="margin-bottom: 4px;">Prøv å selge eller gi bort gratis mot demontering og henting</li>
            <li style="margin-bottom: 4px;">Det er både billigere og mer miljøvennlig enn avfallshåndtering</li>
        </ul>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">2. Avfallshåndtering</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">
            <li style="margin-bottom: 4px;">2.000–5.000 kr hvis du må kaste kjøkkenet</li>
            <li style="margin-bottom: 4px;">Gratis hvis noen henter det</li>
        </ul>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">3. Nytt røropplegg</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">
            <li style="margin-bottom: 4px;">ca. 30.000 kr for komplett opplegg</li>
            <li style="margin-bottom: 4px;">Lavere hvis man gjenbruker eksisterende føringsveier</li>
            <li style="margin-bottom: 4px;">Husk lekkasjesikring (krav)</li>
        </ul>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">4. Nytt elektrisk anlegg</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">
            <li style="margin-bottom: 4px;">ca. 30.000 kr, avhengig av antall kurser og punkter</li>
            <li style="margin-bottom: 4px;">Husk komfyrvakt (påbudt)</li>
        </ul>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">5. Kjøkkeninnredning og hvitevarer</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">
            <li style="margin-bottom: 4px;"><strong>IKEA/startpakke:</strong> fra 50.000 kr</li>
            <li style="margin-bottom: 4px;"><strong>Midtsegment:</strong> 100.000–200.000 kr</li>
            <li style="margin-bottom: 4px;"><strong>Skreddersydd/snekker:</strong> 200.000–500.000+ kr</li>
            <li style="margin-bottom: 4px;">Kommer an på stil, materialer, hvitevarer og løsninger</li>
        </ul>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">6. Benkeplate</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">
            <li style="margin-bottom: 4px;"><strong>Laminat:</strong> fra 2.000 kr</li>
            <li style="margin-bottom: 4px;"><strong>Tre:</strong> fra 5.000 kr</li>
            <li style="margin-bottom: 4px;"><strong>Stein/kompositt:</strong> fra 15.000 kr og oppover</li>
        </ul>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">7. Montering av kjøkken</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">
            <li style="margin-bottom: 4px;">ca. 20.000 kr, avhengig av kompleksitet og løsning</li>
        </ul>
    </div>
    
    <div style="background: #ffffff; border: 1px solid #ddd; padding: 16px; border-radius: 4px; margin: 16px 0;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Vil du ha et mer presist estimat?</h3>
        <p style="margin-bottom: 12px; color: #555; font-size: 14px;">
            Bare si fra hvor stort kjøkkenet er og hva slags løsning du vurderer, så hjelper jeg deg gjerne videre.
        </p>
        
        <button onclick="window.open('https://househacker.no/kontakt', '_blank')" 
                style="background: #333; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; margin-right: 8px;">
            Få tilbud
        </button>
        
        <button onclick="askQuestion('Jeg vil vite mer om kjøkkenkostnader')" 
                style="background: transparent; color: #333; border: 1px solid #333; padding: 9px 19px; border-radius: 4px; font-size: 14px; cursor: pointer;">
            Mer info
        </button>
    </div>
</div>"""
        
        # Beregn estimert totalkostnad (midtsjikt)
        estimated_total = 30000 + 30000 + 125000 + 10000 + 20000 + 5000  # Ca. 220k for standard renovering
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": estimated_total,
            "project_type": "kjøkken_detaljert"
        }

    def _calculate_material_with_labor(self, material: str, area: float) -> Dict[str, Any]:
        """Beregner både material og arbeidskostnad med database-priser"""
        try:
            # Use database pricing for materials
            if material == "maling":
                # Use advanced painting calculation which is database-driven
                calc = self._calculate_advanced_painting(area, {})
                return {
                    "material_cost": calc.get("paint_cost", 0),
                    "labor_cost": calc.get("labor_cost", 0),
                    "hours": calc.get("work_hours", 0),
                    "total": calc.get("total_cost", 0)
                }
            elif material == "fliser":
                # Try to get tile pricing from database
                result = self.pricing_service.get_service_price("bad_flislegging_arbeid", area=area)
                if "error" not in result:
                    total_cost = result.get("total_cost", {}).get("recommended", 0)
                    # Estimate material vs labor split (30% material, 70% labor)
                    material_cost = total_cost * 0.3
                    labor_cost = total_cost * 0.7
                    hours = labor_cost / 1100  # Assume flislegger rate
                else:
                    # Fallback pricing
                    material_cost = area * 500  # 500 NOK/m² for tiles
                    labor_cost = area * 1000   # 1000 NOK/m² for labor
                    hours = area * 1.5         # 1.5 hours per m²
                    total_cost = material_cost + labor_cost
            elif material == "elektrisk":
                # Use electrical pricing from database
                result = self.pricing_service.get_service_price("bad_elektriker", area=area)
                if "error" not in result:
                    total_cost = result.get("total_cost", {}).get("recommended", 0)
                    # Electrical work is mostly labor
                    material_cost = total_cost * 0.2
                    labor_cost = total_cost * 0.8
                    hours = labor_cost / 1300  # Electrician rate
                else:
                    # Fallback
                    material_cost = area * 200
                    labor_cost = area * 800
                    hours = area * 0.8
                    total_cost = material_cost + labor_cost
            elif material == "rør":
                # Use plumber pricing from database
                result = self.pricing_service.get_service_price("bad_rorlegger", area=area)
                if "error" not in result:
                    total_cost = result.get("total_cost", {}).get("recommended", 0)
                    # Plumbing work has more material cost
                    material_cost = total_cost * 0.4
                    labor_cost = total_cost * 0.6
                    hours = labor_cost / 1300  # Plumber rate
                else:
                    # Fallback
                    material_cost = area * 600
                    labor_cost = area * 900
                    hours = area * 1.0
                    total_cost = material_cost + labor_cost
            else:
                # Generic material fallback
                material_cost = area * 300  # 300 NOK/m² generic material
                labor_cost = area * 600     # 600 NOK/m² generic labor
                hours = area * 0.8          # 0.8 hours per m²
                total_cost = material_cost + labor_cost
            
            return {
                "material_cost": material_cost,
                "labor_cost": labor_cost,
                "hours": hours,
                "total": total_cost
            }
            
        except Exception as e:
            # Ultimate fallback
            fallback_total = area * 500  # 500 NOK/m² fallback
            return {
                "material_cost": fallback_total * 0.4,
                "labor_cost": fallback_total * 0.6,
                "hours": area * 0.6,
                "total": fallback_total
            }
    
    def _calculate_advanced_painting(self, area: float, details: Dict, query: str = "") -> Dict[str, Any]:
        """Avansert malingberegning med database-priser"""
        
        # Store query for service selection
        self._current_query = query
        
        # Convert floor area to paintable area (walls + ceiling)
        # For whole house projects: floor area × 2.8 = total paintable area
        # For single rooms: use area as-is (already wall area)
        paintable_area = area
        if area > 80:  # Assume whole house if > 80m²
            paintable_area = area * 2.8
            
        # Determine which service to use based on query context
        # For new houses: skjøtesparkling + maling
        # For renovations: standard innvendig maling or helsparkling
        service_name = "innvendig_maling_standard"  # Default
        
        # Check if it's a new house or mentions sparkling (check both details and query)
        # Pass the original query to this method
        original_query = getattr(self, '_current_query', '').lower()
        query_context = f"{str(details).lower()} {original_query}"
        
        if any(word in query_context for word in ["nytt", "ny", "sparkle", "sparkling", "nybygg"]):
            service_name = "skjotesparkling_inkl_maling"  # Most common for new houses
        elif any(word in query_context for word in ["helspark", "hele", "total"]):
            service_name = "helsparkling_inkl_maling"
        
        # Get pricing from database
        pricing_result = self.pricing_service.get_service_price(service_name, area=paintable_area)
        
        if "error" in pricing_result:
            # Fallback calculation
            return self._legacy_painting_calculation(area, details)
        
        # Extract pricing information
        unit_price = pricing_result.get("unit_price", {}).get("recommended_price", 120)
        total_cost = pricing_result.get("total_cost", {}).get("recommended", area * unit_price)
        
        # Estimate material vs labor split (typically 25% material, 75% labor)
        material_portion = 0.25
        labor_portion = 0.75
        
        # Calculate components
        paint_cost = total_cost * material_portion
        labor_cost = total_cost * labor_portion
        
        # Estimate liters needed (8 m² per liter, 2 coats)
        coverage_per_liter = 8
        layers = 2
        liters_needed = (paintable_area * layers) / coverage_per_liter
        
        # Estimate work hours
        hourly_rate = self.LEGACY_HOURLY_RATES.get("maler", 850)
        work_hours = labor_cost / hourly_rate if hourly_rate > 0 else paintable_area * 0.6
        
        # Apply modifiers based on details
        if details.get("rough_surface"):
            liters_needed *= 1.25
            work_hours *= 1.2
        if details.get("ceiling_painting"):
            work_hours *= 1.5
        if details.get("many_windows"):
            work_hours *= 1.3
        if details.get("old_wallpaper"):
            work_hours += area * 0.3
        
        # Recalculate costs if modifiers applied (only if there are actual modifications)
        modifiers_applied = any([
            details.get("rough_surface"),
            details.get("ceiling_painting"),
            details.get("many_windows"),
            details.get("old_wallpaper")
        ])
        
        if modifiers_applied:
            modifier = work_hours / (area * 0.6) if area > 0 else 1.2
            total_cost *= modifier
            paint_cost = total_cost * material_portion
            labor_cost = total_cost * labor_portion
        
        # Add rigg og drift costs (setup, masking, cleanup, travel, parking, waste disposal)
        rigg_og_drift = self._calculate_rigg_og_drift_costs(area, details, paintable_area)
        
        # Update total cost
        total_cost_with_rigg = total_cost + rigg_og_drift["total_rigg_cost"]
        
        return {
            "liters_needed": liters_needed,
            "paint_cost": paint_cost,
            "work_hours": work_hours,
            "labor_cost": labor_cost,
            "rigg_og_drift": rigg_og_drift,
            "total_cost": total_cost_with_rigg,
            "base_cost": total_cost,
            "layers": layers,
            "unit_price": unit_price,
            "pricing_source": "database",
            "floor_area": area,
            "paintable_area": paintable_area
        }
    
    def _calculate_rigg_og_drift_costs(self, floor_area: float, details: Dict, paintable_area: float = None) -> Dict[str, Any]:
        """Beregner rigg og drift kostnader (oppsett, masking, rydding, transport, etc.)"""
        
        # Use paintable area if provided, otherwise floor area
        calculation_area = paintable_area if paintable_area else floor_area
        
        # Base rigg og drift costs - higher for whole house projects
        if floor_area > 80:  # Whole house
            base_rigg_cost = 8000  # Higher base for whole house
        else:
            base_rigg_cost = 2500  # Room/smaller projects
        
        # Area-based scaling
        area_factor = max(1.0, calculation_area / 100)  # Scale based on paintable area
        
        components = {
            "transport_parkering": 800 * area_factor,         # Kjøring, parkering Oslo
            "masking_tildekking": 12 * calculation_area,      # Maskeringstape, plastduk per m² malerflate
            "oppsett_nedrigging": 1200 * area_factor,         # Stige, utstyr, opprydding
            "avfallshåndtering": 600 * area_factor            # Kasting av avfall, tomme malingsb⁄kker
        }
        
        # Additional costs based on job complexity
        if details.get("many_windows"):
            components["ekstra_masking"] = 500  # Mer masking rundt vinduer
        
        if details.get("ceiling_painting"):
            components["takarbeid_rigg"] = 800  # Ekstra rigg for takarbeid
        
        if details.get("old_wallpaper"):
            components["tapetfjerning_avfall"] = 400  # Mer avfall fra tapet
        
        # Get database pricing for rigg og drift if available
        try:
            rigg_pricing = self.pricing_service.get_service_price("rigg_og_drift")
            if "error" not in rigg_pricing:
                # Use database pricing as baseline
                db_daily_rate = rigg_pricing.get("unit_price", {}).get("market_avg", 3500)
                # Estimate days needed (most paint jobs are 1-2 days)
                estimated_days = max(1, area / 40)  # 40m² per dag
                base_rigg_cost = db_daily_rate * estimated_days
        except Exception:
            pass  # Fall back to fixed costs
        
        total_rigg_cost = max(base_rigg_cost, sum(components.values()))
        
        return {
            "components": components,
            "base_rigg_cost": base_rigg_cost,
            "total_rigg_cost": total_rigg_cost,
            "breakdown": {
                "transport_parkering": components["transport_parkering"],
                "masking_tildekking": components["masking_tildekking"], 
                "oppsett_nedrigging": components["oppsett_nedrigging"],
                "avfallshåndtering": components["avfallshåndtering"]
            }
        }
    
    def _legacy_painting_calculation(self, area: float, details: Dict) -> Dict[str, Any]:
        """Fallback painting calculation when database is unavailable"""
        # Basic calculations with fallback rates
        coverage_per_liter = 8
        layers = 2
        paint_price_per_liter = 550
        hourly_rate = 850
        hours_per_m2 = 0.6
        
        liters_needed = (area * layers) / coverage_per_liter
        work_hours = area * hours_per_m2
        
        # Apply detail modifiers
        if details.get("rough_surface"):
            liters_needed *= 1.25
            work_hours *= 1.2
        if details.get("ceiling_painting"):
            work_hours *= 1.5
        if details.get("many_windows"):
            work_hours *= 1.3
        if details.get("old_wallpaper"):
            work_hours += area * 0.3
        
        paint_cost = liters_needed * paint_price_per_liter
        labor_cost = work_hours * hourly_rate
        base_cost = paint_cost + labor_cost
        
        # Add rigg og drift costs for fallback calculation too
        paintable_area = area * 2.8 if area > 80 else area  # Same conversion as main method
        rigg_og_drift = self._calculate_rigg_og_drift_costs(area, details, paintable_area)
        total_cost = base_cost + rigg_og_drift["total_rigg_cost"]
        
        return {
            "liters_needed": liters_needed,
            "paint_cost": paint_cost,
            "work_hours": work_hours,
            "labor_cost": labor_cost,
            "rigg_og_drift": rigg_og_drift,
            "total_cost": total_cost,
            "base_cost": base_cost,
            "layers": layers,
            "pricing_source": "fallback"
        }

    def _generate_lead_capture(self, calculation_result: Dict) -> Dict[str, Any]:
        """Genererer lead-capture for store prosjekter"""
        total_cost = calculation_result.get("total_cost", 0)
        
        lead_message = f"""
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="color: #856404;">Trenger du hjelp med gjennomføring?</h3>
            <p>Dette er et større prosjekt på <strong>{total_cost:,.0f} NOK</strong>. Vi kan hjelpe deg med:</p>
            <ul>
                <li>Koble deg med kvalifiserte håndverkere</li>
                <li>Prosjektplanlegging og koordinering</li>
                <li>Forhandling av priser med leverandører</li>
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
            "tilbud", "pristilbud", "anbud", "offert", "konsultasjon",
            "registrere", "prosjekt", "befaring", "househacker",
            
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
            "kan jeg regne med", "estimere kostnad", "beregne pris",
            "gi meg et tilbud", "kan du gi", "tilbud på", "hjelp med",
            "trenger tilbud", "vil ha tilbud", "ønsker tilbud", "få tilbud",
            "kan jeg få", "hjelpe meg", "på dette", "dette arbeidet"
        ]
        
        return any(phrase in query_lower for phrase in common_phrases)

    def get_capabilities(self) -> Dict[str, Any]:
        """Returnerer informasjon om hva denne agenten kan gjøre"""
        return {
            "name": self.agent_name,
            "description": "househacker-assistent for oppussingsprosjekter og prosjektregistrering",
            "keywords": [
                "househacker", "oppussing", "renovering", "prosjektregistrering", "tilbud",
                "håndverkere", "befaring", "kvalitetssikring", "prosjektkoordinering"
            ],
            "features": [
                "Prosjektregistrering og oppfølging",
                "Profesjonelle kostnadsestimater",
                "Kobling med kvalifiserte håndverkere", 
                "Gratis befaring og rådgivning",
                "Tilbudssammenligning",
                "Kvalitetssikring av arbeid"
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
            project_type = "kjøkken_detaljert"
        elif any(word in query_lower for word in ['elektriker', 'elektrik', 'stikkontakt', 'sikringsskap', 'downlight', 'gulvvarme', 'elbillader', 'el-anlegg', 'el-sjekk', 'kurs', 'varmekabler']):
            project_type = "elektriker_arbeid"
        elif any(word in query_lower for word in ['graving', 'grunnmur', 'fundamentering', 'sprengning', 'fjell', 'drenering', 'plate på mark', 'gravemaskin', 'tomt', 'fundament']):
            project_type = "grunnarbeider"
        elif any(word in query_lower for word in ['gulv', 'parkett', 'laminat', 'vinyl', 'epoxy', 'microsement', 'gulvavretting', 'gulvsliping', 'varmekabler gulv']):
            project_type = "gulvarbeider"
        # Check doors/windows BEFORE carpentry to ensure proper routing
        elif any(word in query_lower for word in ['vindu', 'vinduer', 'bytte vindu', 'vindusutskifting', 'vindumontasje', 'spesialglass']) or re.search(r'\d+\s*vinduer?', query_lower):
            project_type = "vinduer_dorer"
        elif any(word in query_lower for word in ['ytterdør', 'inngangsdør', 'innerdør', 'dører']) or re.search(r'\d+\s*dører?', query_lower):
            project_type = "vinduer_dorer"
        elif any(word in query_lower for word in ['tømrer', 'lettvegg', 'skillevegg', 'himling', 'vindusfor', 'listverk', 'gipsplat', 'konstruksjon']):
            project_type = "tomrer_bygg"
        elif any(word in query_lower for word in ['tak', 'takomlegging', 'takstein', 'takshingel', 'skifer', 'takrenne', 'ytterkledning', 'kledning', 'etterisolering', 'fasade']):
            project_type = "tak_ytterkledning"
        elif any(word in query_lower for word in ['isolasjon', 'isolering', 'blåseisolasjon', 'dampsperre', 'lufttetting', 'kuldebryt', 'energioppgradering', 'kjellerisolasjon']):
            project_type = "isolasjon_tetting"
        else:
            project_type = "unknown"
        
        # Type analyse
        if any(word in query_lower for word in ['komplett', 'totalrenovering', 'alt', 'hele']):
            analysis_type = "full_project_estimate"
        elif project_type == "bad_komplett" and (area or any(word in query_lower for word in ['renovere', 'pusse opp', 'oppussing', 'flislegging', 'kostnad', 'koster', 'pris'])):
            analysis_type = "full_project_estimate"  # Alle badspørsmål med areal eller renovering skal bruke database-priser
        elif project_type == "kjøkken_detaljert":
            analysis_type = "full_project_estimate"  # Alle kjøkkenspørsmål skal bruke detaljert guide
        elif project_type == "elektriker_arbeid":
            analysis_type = "electrical_work"  # Elektriker-spesifikke spørsmål
        elif project_type == "grunnarbeider":
            analysis_type = "groundwork"  # Grunnarbeid-spesifikke spørsmål
        elif project_type == "gulvarbeider":
            analysis_type = "flooring_work"  # Gulvarbeid-spesifikke spørsmål
        elif project_type == "tomrer_bygg":
            analysis_type = "carpentry_work"  # Tømrer/bygg-spesifikke spørsmål
        elif project_type == "tak_ytterkledning":
            analysis_type = "roofing_cladding_work"  # Tak og ytterkledning-spesifikke spørsmål
        elif project_type == "isolasjon_tetting":
            analysis_type = "insulation_work"  # Isolasjon og tetting-spesifikke spørsmål
        elif project_type == "vinduer_dorer":
            analysis_type = "windows_doors_work"  # Vinduer og dører-spesifikke spørsmål
        elif any(word in query_lower for word in ['arbeid', 'lønn', 'timepris', 'håndverker']):
            analysis_type = "material_and_labor"
        elif any(word in query_lower for word in ['sammenlign', 'pris', 'billigst', 'leverandør']):
            analysis_type = "price_comparison"
        elif any(word in query_lower for word in ['maling', 'male']) and area:
            analysis_type = "painting_specific"
        elif any(phrase in query_lower for phrase in ['flere detaljer', 'mer om kostnad', 'detaljert', 'breakdown', 'liste']):
            analysis_type = "detailed_breakdown"
        elif any(phrase in query_lower for phrase in ['tilbud', 'gi meg et tilbud', 'kan du gi', 'trenger tilbud', 'få tilbud', 'på dette']) and 'hjelp med' not in query_lower:
            analysis_type = "quote_request"
        elif any(phrase in query_lower for phrase in ['registrere prosjekt', 'registrere et prosjekt', 'registrer et prosjekt', 'jeg vil registrere', 'melde fra om prosjekt']):
            analysis_type = "project_registration"
        elif any(phrase in query_lower for phrase in ['hvordan fungerer', 'om househacker', 'hva er househacker', 'hvem er househacker']):
            analysis_type = "about_househacker"
        elif 'hjelp med' in query_lower and any(word in query_lower for word in ['kjøkken', 'bad', 'renovering']):
            analysis_type = "full_project_estimate"  # Behandle som kostnadsforespørsel
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
        # Known materials that we support
        known_materials = ["maling", "fliser", "laminat", "gips", "rør", "elektrisk", "benkeplate"]
        
        materials = []
        for material in known_materials:
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
            calc = self._calculate_material_with_labor(material, area)
            breakdown[material] = calc
            total_cost += calc["total"]
        
        response = f"""
        <h2>Material og Arbeidskostnad - {area} m²</h2>
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

    async def _provide_detailed_breakdown(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Gir detaljert kostnadsoppstilling for badrenovering 5m²"""
        # Standard 5m² bad for detaljert breakdown
        area = 5.0
        project_type = "bad_komplett"
        
        project_config = self.PROJECT_TYPES.get(project_type)
        total_material_cost = 0
        total_labor_cost = 0
        total_time_hours = 0
        
        detailed_breakdown = {}
        
        # Beregn for hvert material/arbeidsområde med database-priser
        if project_config:
            for material in project_config["materialer"]:
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
        tillegg = project_config["tillegg"]
        subtotal = total_material_cost + total_labor_cost + base_kostnader_total
        
        prosjektledelse = subtotal * tillegg["prosjektledelse"]
        uforutsett = subtotal * tillegg["uforutsett"]
        rydding = tillegg["rydding"]
        byggesøknad = tillegg.get("byggesøknad", 0)
        
        total_cost = subtotal + prosjektledelse + uforutsett + rydding + byggesøknad
        
        # Generer detaljert respons
        response = f"""
<div style="background: #f8fafc; padding: 20px; border-radius: 12px; margin: 15px 0; border-left: 4px solid #374151;">
    <h2 style="color: #1f2937; margin-bottom: 15px;">📋 Detaljert kostnadsoppstilling - Bad 5 m²</h2>
    
    <h3 style="color: #374151;">🔨 Materialer og arbeid</h3>
    <table style="width:100%; border-collapse: collapse; margin-bottom: 20px;">
    <tr style="background: #1f2937; color: white;">
        <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Kategori</th>
        <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">Materialer</th>
        <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">Arbeid</th>
        <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">Timer</th>
        <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">Sum</th>
    </tr>"""
        
        for material, calc in detailed_breakdown.items():
            material_name = {
                "fliser": "Flislegging",
                "rør": "Rørarbeider", 
                "elektrisk": "Elektroarbeider",
                "maling": "Maling"
            }.get(material, material.title())
            
            response += f"""
    <tr style="background: #ffffff;">
        <td style="border: 1px solid #ddd; padding: 12px; font-weight: bold;">{material_name}</td>
        <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">{calc['material_cost']:,.0f} NOK</td>
        <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">{calc['labor_cost']:,.0f} NOK</td>
        <td style="border: 1px solid #ddd; padding: 12px; text-align: right;">{calc['hours']:.1f}t</td>
        <td style="border: 1px solid #ddd; padding: 12px; text-align: right; font-weight: bold;">{calc['total']:,.0f} NOK</td>
    </tr>"""
        
        response += f"""
    </table>
    
    <h3 style="color: #374151;">🛠️ Fast utstyr og installasjoner</h3>
    <ul style="background: #ffffff; padding: 15px; border-radius: 8px; margin-bottom: 20px;">"""
        
        if project_config and "base_kostnader" in project_config:
            for item, kostnad in project_config["base_kostnader"].items():
                item_name = {
                    "wc": "WC/toalett",
                    "servant": "Servant og speil",
                    "dusjkabinett": "Dusjkabinett",
                    "ventilasjon": "Ventilasjon",
                    "gulvvarme": "Gulvvarme",
                    "riving": "Riving og klargjøring"
                }.get(item, item.replace('_', ' ').title())
                response += f"""<li><strong>{item_name}:</strong> {kostnad:,.0f} NOK</li>"""
        
        response += f"""
    </ul>
    
    <h3 style="color: #374151;">💰 Kostnadssammendrag</h3>
    <div style="background: #ffffff; padding: 15px; border-radius: 8px;">
        <ul>
            <li><strong>Materialer totalt:</strong> {total_material_cost:,.0f} NOK</li>
            <li><strong>Arbeid totalt:</strong> {total_labor_cost:,.0f} NOK</li>
            <li><strong>Fast utstyr:</strong> {base_kostnader_total:,.0f} NOK</li>
            <li><strong>Prosjektledelse ({tillegg['prosjektledelse']*100:.0f}%):</strong> {prosjektledelse:,.0f} NOK</li>
            <li><strong>Uforutsett ({tillegg['uforutsett']*100:.0f}%):</strong> {uforutsett:,.0f} NOK</li>
            <li><strong>Rydding og avfall:</strong> {rydding:,.0f} NOK</li>"""
        
        if byggesøknad > 0:
            response += f"""<li><strong>Byggesøknad:</strong> {byggesøknad:,.0f} NOK</li>"""
        
        response += f"""
        </ul>
    </div>
    
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
        <h3 style="color: white; margin-bottom: 10px;">🎯 Totalkostnad</h3>
        <div style="font-size: 28px; font-weight: bold; color: #10b981;">{total_cost:,.0f} NOK</div>
        <p style="margin-top: 10px; opacity: 0.9;">Estimert tidsbruk: {total_time_hours:.0f} timer ({total_time_hours/8:.1f} arbeidsdager)</p>
    </div>
    
    <p style="font-size: 14px; color: #6b7280; margin-top: 15px;">
        💡 Dette er en detaljert oppstilling for et standard 5m² bad i Oslo. Prisene er basert på markedspriser og inkluderer alle nødvendige materialer, arbeid og tilleggskostnader.
    </p>
</div>"""
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": total_cost,
            "material_cost": total_material_cost,
            "labor_cost": total_labor_cost,
            "estimated_hours": total_time_hours,
            "breakdown": detailed_breakdown
        }

    async def _handle_quote_request(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Håndterer forespørsler om tilbud eller konsultasjon"""
        response = f"""
<div style="background: #f8f9fa; padding: 20px; border-radius: 6px; margin: 16px 0;">
    <h2 style="color: #333; margin-bottom: 16px; font-size: 18px; font-weight: 600;">Anbudsprosess med househacker</h2>
    
    <p style="margin-bottom: 16px; color: #555; line-height: 1.5;">
        {self.COMPANY_INFO["description"]}. {self.COMPANY_INFO["main_goal"]}.
    </p>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Våre tjenester:</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">"""
        
        for service in self.COMPANY_INFO["services"]:
            response += f"<li style='margin-bottom: 4px;'>{service}</li>"
        
        response += f"""
        </ul>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Produktalternativer:</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">"""
        
        for product, description in self.COMPANY_INFO["products"].items():
            response += f"<li style='margin-bottom: 4px;'><strong>{product.title()}:</strong> {description}</li>"
        
        response += f"""
        </ul>
    </div>
    
    <div style="margin-top: 16px; text-align: center;">
        <button onclick="window.open('https://househacker.no/kontakt', '_blank')" 
                style="background: #333; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; cursor: pointer;">
            Registrer prosjekt
        </button>
    </div>
</div>"""
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": 0,
            "show_lead_capture": True
        }

    async def _handle_project_registration(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Håndterer prosjektregistrering direkte"""
        response = f"""
<div style="background: #f8f9fa; padding: 20px; border-radius: 6px; margin: 16px 0;">
    <h2 style="color: #333; margin-bottom: 16px; font-size: 18px; font-weight: 600;">Registrer ditt oppussingsprosjekt</h2>
    
    <p style="margin-bottom: 16px; color: #555; line-height: 1.5;">
        {self.COMPANY_INFO["description"]}. {self.COMPANY_INFO["main_goal"]}.
    </p>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Våre tjenester:</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">"""
        
        for service in self.COMPANY_INFO["services"]:
            response += f"<li style='margin-bottom: 4px;'>{service}</li>"
        
        response += f"""
        </ul>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Prosessen:</h3>
        <ol style="margin: 0; padding-left: 18px; color: #555;">"""
        
        for step in self.COMPANY_INFO["process"]:
            response += f"<li style='margin-bottom: 4px;'>{step}</li>"
            
        response += f"""
        </ol>
    </div>
    
    <div style="text-align: center; margin-top: 16px;">
        <button onclick="window.open('https://househacker.no/kontakt', '_blank')" 
                style="background: #333; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; cursor: pointer;">
            Registrer prosjekt
        </button>
    </div>
</div>"""
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "show_lead_capture": True
        }

    async def _explain_househacker_services(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Forklarer househacker sine tjenester basert på faktisk informasjon"""
        response = f"""
<div style="background: #f8f9fa; padding: 20px; border-radius: 6px; margin: 16px 0;">
    <h2 style="color: #333; margin-bottom: 16px; font-size: 18px; font-weight: 600;">Om househacker</h2>
    
    <p style="margin-bottom: 16px; color: #555; line-height: 1.5;">
        {self.COMPANY_INFO["description"]}.
    </p>
    
    <p style="margin-bottom: 20px; color: #555; line-height: 1.5;">
        {self.COMPANY_INFO["main_goal"]}.
    </p>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Våre produkter:</h3>
        <ul style="margin: 0; padding-left: 18px; color: #555;">"""
        
        for product, description in self.COMPANY_INFO["products"].items():
            response += f"<li style='margin-bottom: 4px;'><strong>{product.title()}:</strong> {description}</li>"
        
        response += f"""
        </ul>
    </div>
    
    <div style="background: #ffffff; padding: 16px; border-radius: 4px; margin: 16px 0; border: 1px solid #ddd;">
        <h3 style="color: #333; margin-bottom: 10px; font-size: 14px; font-weight: 600;">Prosessen:</h3>
        <ol style="margin: 0; padding-left: 18px; color: #555;">"""
        
        for step in self.COMPANY_INFO["process"]:
            response += f"<li style='margin-bottom: 4px;'>{step}</li>"
        
        response += f"""
        </ol>
    </div>
    
    <div style="margin-top: 16px;">
        <button onclick="askQuestion('Registrer et prosjekt')" 
                style="background: #333; color: white; padding: 10px 20px; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; margin-right: 8px;">
            Registrer prosjekt
        </button>
        
        <button onclick="askQuestion('Hva koster et bad?')" 
                style="background: transparent; color: #333; border: 1px solid #333; padding: 9px 19px; border-radius: 4px; font-size: 14px; cursor: pointer;">
            Se kostnader
        </button>
    </div>
</div>"""
        
        return {
            "response": response,
            "agent_used": self.agent_name
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
        paint_calc = self._calculate_advanced_painting(area, details, query)
        
        # Check if it's a whole house project
        is_whole_house = area > 80
        area_description = f"{area} m² gulvflate" if is_whole_house else f"{area} m²"
        
        response = f"""
        <h2>🎨 Malingkalkulator - {area_description}</h2>
        
        {f'<p style="margin-bottom: 16px; padding: 12px; background: #f0f8ff; border-radius: 6px; font-size: 14px; color: #2c5aa0;"><strong>Hele hus:</strong> {area} m² gulvflate = ca. {paint_calc.get("paintable_area", area):.0f} m² malerflate (vegger + tak)</p>' if is_whole_house else ''}
        
        <h3>📊 Materialberegning</h3>
        <ul>
            <li><strong>Maling nødvendig:</strong> {paint_calc['liters_needed']:.1f} liter</li>
            <li><strong>Kostnad maling:</strong> {paint_calc['paint_cost']:,.0f} NOK</li>
            <li><strong>Arbeidstid:</strong> {paint_calc['work_hours']:.1f} timer</li>
            <li><strong>Arbeidskostnad:</strong> {paint_calc['labor_cost']:,.0f} NOK</li>
        </ul>
        
        <h3>🚚 Rigg og drift</h3>
        <ul>
            <li><strong>Transport og parkering:</strong> {paint_calc['rigg_og_drift']['breakdown']['transport_parkering']:,.0f} NOK</li>
            <li><strong>Masking og tildekking:</strong> {paint_calc['rigg_og_drift']['breakdown']['masking_tildekking']:,.0f} NOK</li>
            <li><strong>Oppsett og nedrigging:</strong> {paint_calc['rigg_og_drift']['breakdown']['oppsett_nedrigging']:,.0f} NOK</li>
            <li><strong>Avfallshåndtering:</strong> {paint_calc['rigg_og_drift']['breakdown']['avfallshåndtering']:,.0f} NOK</li>
        </ul>
        
        <h3>💰 Totalkostnad</h3>
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <h3 style="color: #1976d2;">🎯 Total: {paint_calc['total_cost']:,.0f} NOK</h3>
            <p style="margin: 8px 0; opacity: 0.8; font-size: 14px;">Inkluderer materialer, arbeid og rigg/drift</p>
        </div>
        
        <h3>ℹ️ Inkludert i rigg og drift</h3>
        <ul>
            <li>🚗 Transport og parkering i Oslo</li>
            <li>🎭 Maskeringstape og plastduk</li>
            <li>🪜 Oppsett av stige og utstyr</li>
            <li>🗑️ Avfallshåndtering og opprydding</li>
            <li>📦 Nedrigging og transport bort</li>
        </ul>
        
        <h3>💡 Pro-tips</h3>
        <ul>
            <li>🕐 <strong>Tidsbruk:</strong> Planlegg 2-3 dager for et rom (inkl. tørketid)</li>
            <li>🌡️ <strong>Temperatur:</strong> Mal ved 18-22°C for best resultat</li>
            <li>📐 <strong>Teknikk:</strong> Mal først kanter med pensel, deretter rull</li>
            <li>💧 <strong>Underlag:</strong> Vask vegger først, sparkle hull og riper</li>
        </ul>"""
        
        # Legg til tilbudsforespørsel hvis kostnad er over 10,000 NOK
        if paint_calc['total_cost'] > 10000:
            response += f"""
        
<div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
    <h3 style="color: #856404; margin-bottom: 15px;">🤝 Ønsker du profesjonell hjelp?</h3>
    <p style="margin-bottom: 20px;">Dette er et større malingsjobb på {paint_calc['total_cost']:,.0f} NOK. Vi kan koble deg med erfarne malere!</p>
    
    <button onclick="window.open('https://househacker.no/kontakt', '_blank')" 
            style="background: #1f2937; color: white; padding: 15px 30px; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin: 0 10px;">
        🎨 Få tilbud fra malere
    </button>
    
    <button onclick="askQuestion('Jeg vil vite mer om malingskostnadene')" 
            style="background: transparent; color: #856404; border: 2px solid #856404; padding: 13px 25px; border-radius: 8px; font-size: 14px; cursor: pointer; margin: 0 10px;">
        📋 Flere detaljer
    </button>
</div>"""
        
        response += """
        """
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "total_cost": paint_calc['total_cost'],
            "calculation_details": paint_calc
        }

    # Old method removed - replaced with database-based version earlier in file
    
    def _legacy_painting_calculation(self, area: float, details: Dict) -> Dict[str, Any]:
        """Fallback painting calculation when database is unavailable"""
        # Basic calculations with fallback rates
        coverage_per_liter = 8
        layers = 2
        paint_price_per_liter = 550
        hourly_rate = 850
        hours_per_m2 = 0.6
        
        liters_needed = (area * layers) / coverage_per_liter
        work_hours = area * hours_per_m2
        
        # Apply detail modifiers
        if details.get("rough_surface"):
            liters_needed *= 1.25
            work_hours *= 1.2
        if details.get("ceiling_painting"):
            work_hours *= 1.5
        if details.get("many_windows"):
            work_hours *= 1.3
        if details.get("old_wallpaper"):
            work_hours += area * 0.3
        
        paint_cost = liters_needed * paint_price_per_liter
        labor_cost = work_hours * hourly_rate
        total_cost = paint_cost + labor_cost
        
        return {
            "liters_needed": liters_needed,
            "paint_cost": paint_cost,
            "work_hours": work_hours,
            "labor_cost": labor_cost,
            "total_cost": total_cost,
            "layers": layers,
            "pricing_source": "fallback"
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
        """Beregner malingbehov med fallback-verdier"""
        # Fallback constants
        dekning_per_liter = 8
        lag = 2
        pris_per_liter = 550
        
        liters_needed = (area * lag) / dekning_per_liter
        total_cost = liters_needed * pris_per_liter
        
        return {
            "liters_needed": liters_needed,
            "total_cost": total_cost,
            "layers": lag
        }

    def _calculate_tiles(self, area: float) -> Dict[str, Any]:
        """Beregner flisbehov med fallback-verdier"""
        # Fallback constants
        spill_faktor = 0.15
        pris_per_m2 = 950
        
        area_with_waste = area * (1 + spill_faktor)
        total_cost = area_with_waste * pris_per_m2
        
        return {
            "area_with_waste": area_with_waste,
            "total_cost": total_cost,
            "waste_factor": spill_faktor
        }

    def _calculate_laminate_legacy(self, area: float) -> Dict[str, Any]:
        """Beregner laminatbehov med fallback-verdier (legacy method)"""
        # Fallback constants
        spill_faktor = 0.1
        pris_per_m2 = 550
        
        area_with_waste = area * (1 + spill_faktor)
        total_cost = area_with_waste * pris_per_m2
        
        return {
            "area_with_waste": area_with_waste,
            "total_cost": total_cost,
            "waste_factor": spill_faktor
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

    # New comprehensive category handlers
    async def _handle_carpentry_work(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Handle carpentry and building work queries"""
        try:
            query_lower = query.lower()
            area = analysis.get("area", 10)  # Default area
            
            # Route to specific carpentry calculations
            if any(word in query_lower for word in ['lettvegg', 'skillevegg']):
                return await self._calculate_partition_wall(query_lower, area)
            elif any(word in query_lower for word in ['himling', 'tak']):
                return await self._calculate_ceiling_work(query_lower, area)
            elif any(word in query_lower for word in ['dør', 'innerdør']):
                return await self._calculate_door_installation(query_lower)
            elif any(word in query_lower for word in ['listverk', 'lister']):
                return await self._calculate_molding_work(query_lower)
            elif any(word in query_lower for word in ['tømrer', 'timepris']):
                return await self._calculate_carpenter_hourly(query_lower)
            else:
                return await self._carpentry_general_fallback(query_lower, area)
                
        except Exception as e:
            return await self._carpentry_fallback(f"tømrerarbeid {area:.0f}m²", area * 600)

    async def _handle_roofing_cladding_work(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Handle roofing and exterior cladding work queries"""
        try:
            query_lower = query.lower()
            area = analysis.get("area", 100)  # Default roof area
            
            # Route to specific roofing/cladding calculations
            if any(word in query_lower for word in ['takomlegging', 'nytt tak']):
                return await self._calculate_roof_replacement(query_lower, area)
            elif any(word in query_lower for word in ['takrenne', 'nedløp']):
                return await self._calculate_gutters(query_lower)
            elif any(word in query_lower for word in ['etterisolering', 'kledning']):
                return await self._calculate_exterior_insulation(query_lower, area)
            elif any(word in query_lower for word in ['takvindu']):
                return await self._calculate_roof_windows(query_lower)
            else:
                return await self._roofing_general_fallback(query_lower, area)
                
        except Exception as e:
            return await self._roofing_fallback(f"takarbeid {area:.0f}m²", area * 2000)

    async def _handle_insulation_work(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Handle insulation and sealing work queries"""
        try:
            query_lower = query.lower()
            area = analysis.get("area", 80)  # Default insulation area
            
            # Route to specific insulation calculations
            if any(word in query_lower for word in ['blåseisolasjon', 'loft']):
                return await self._calculate_blown_insulation(query_lower, area)
            elif any(word in query_lower for word in ['dampsperre']):
                return await self._calculate_vapor_barrier(query_lower, area)
            elif any(word in query_lower for word in ['lufttetting']):
                return await self._calculate_air_sealing(query_lower)
            elif any(word in query_lower for word in ['energioppgradering']):
                return await self._calculate_energy_upgrade(query_lower, area)
            else:
                return await self._insulation_general_fallback(query_lower, area)
                
        except Exception as e:
            return await self._insulation_fallback(f"isolasjonsarbeid {area:.0f}m²", area * 400)

    async def _handle_windows_doors_work(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Handle windows and doors work queries"""
        try:
            query_lower = query.lower()
            
            # Extract number of windows/doors - more flexible patterns
            num_match = re.search(r'(\d+)\s*(?:stk|vindu|vinduer|dør|dører|innerdør|innerdører|ytterdør)', query_lower)
            if not num_match:
                num_match = re.search(r'bytte\s*(\d+)\s*(?:vindu|dør)', query_lower)
            if not num_match:
                num_match = re.search(r'skifte\s*(\d+)\s*(?:vindu|dør|innerdør)', query_lower)
            if not num_match:
                num_match = re.search(r'(\d+)', query_lower)
            num_items = int(num_match.group(1)) if num_match else 1
            
            # Route to specific window/door calculations
            if any(word in query_lower for word in ['vindu', 'vinduer']):
                return await self._calculate_window_replacement(query_lower, num_items)
            elif any(word in query_lower for word in ['ytterdør']):
                return await self._calculate_exterior_door(query_lower)
            elif any(word in query_lower for word in ['innerdør']):
                return await self._calculate_interior_doors(query_lower, num_items)
            elif any(word in query_lower for word in ['takvindu']):
                return await self._calculate_roof_windows(query_lower)
            else:
                return await self._windows_doors_general_fallback(query_lower, num_items)
                
        except Exception as e:
            return await self._windows_doors_fallback(f"vindu/dør arbeid", 10000)

    # Fallback methods for new categories
    async def _carpentry_fallback(self, service_name: str, fallback_cost: float) -> Dict[str, Any]:
        """Fallback for carpentry calculations"""
        return {
            "response": f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827;">🔨 Tømrerarbeid</h2>
    <div style="background: #6b46c1; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white;">Estimat</h3>
        <div style="font-size: 32px; font-weight: 600;">{fallback_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px;">{fallback_cost * 1.25:,.0f} NOK inkl. mva</div>
    </div>
    <p style="color: #6b7280; margin-top: 16px;">
        Kontakt oss for detaljert tilbud på tømrerarbeid.
    </p>
</div>""",
            "agent_used": self.agent_name,
            "total_cost": fallback_cost,
            "pricing_source": "fallback"
        }

    async def _roofing_fallback(self, service_name: str, fallback_cost: float) -> Dict[str, Any]:
        """Fallback for roofing calculations"""
        return {
            "response": f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827;">🏠 Tak og Ytterkledning</h2>
    <div style="background: #dc2626; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white;">Estimat</h3>
        <div style="font-size: 32px; font-weight: 600;">{fallback_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px;">{fallback_cost * 1.25:,.0f} NOK inkl. mva</div>
    </div>
    <p style="color: #6b7280; margin-top: 16px;">
        Kontakt oss for detaljert tilbud på tak og ytterkledning.
    </p>
</div>""",
            "agent_used": self.agent_name,
            "total_cost": fallback_cost,
            "pricing_source": "fallback"
        }

    async def _insulation_fallback(self, service_name: str, fallback_cost: float) -> Dict[str, Any]:
        """Fallback for insulation calculations"""
        return {
            "response": f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827;">🏠 Isolasjon og Tetting</h2>
    <div style="background: #059669; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white;">Estimat</h3>
        <div style="font-size: 32px; font-weight: 600;">{fallback_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px;">{fallback_cost * 1.25:,.0f} NOK inkl. mva</div>
    </div>
    <div style="background: #ecfdf5; padding: 16px; border-radius: 6px; margin: 16px 0;">
        <p style="color: #065f46; margin: 0;">💡 Energioppgraderinger kan kvalifisere for Enova-støtte opp til 50.000 NOK</p>
    </div>
    <p style="color: #6b7280; margin-top: 16px;">
        Kontakt oss for detaljert tilbud på isolasjon og energioppgradering.
    </p>
</div>""",
            "agent_used": self.agent_name,
            "total_cost": fallback_cost,
            "pricing_source": "fallback"
        }

    async def _windows_doors_fallback(self, service_name: str, fallback_cost: float) -> Dict[str, Any]:
        """Fallback for windows/doors calculations"""
        return {
            "response": f"""
<div style="background: #f9fafb; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827;">🚪 Vinduer og Dører</h2>
    <div style="background: #1e40af; color: white; padding: 20px; border-radius: 6px; text-align: center; margin: 16px 0;">
        <h3 style="color: white;">Estimat</h3>
        <div style="font-size: 32px; font-weight: 600;">{fallback_cost:,.0f} NOK</div>
        <div style="font-size: 18px; margin-top: 8px;">eks. mva</div>
        <div style="font-size: 20px; margin-top: 4px;">{fallback_cost * 1.25:,.0f} NOK inkl. mva</div>
    </div>
    <p style="color: #6b7280; margin-top: 16px;">
        Kontakt oss for detaljert tilbud på vinduer og dører.
    </p>
</div>""",
            "agent_used": self.agent_name,
            "total_cost": fallback_cost,
            "pricing_source": "fallback"
        }

    # Placeholder methods for specific calculations (to be implemented)
    async def _calculate_partition_wall(self, query_lower: str, area: float):
        return await self._carpentry_fallback(f"lettvegg {area:.0f}m²", area * 4000)
        
    async def _calculate_ceiling_work(self, query_lower: str, area: float):
        return await self._carpentry_fallback(f"himling {area:.0f}m²", area * 700)
        
    async def _calculate_door_installation(self, query_lower: str):
        return await self._carpentry_fallback("dørmontering", 3000)
        
    async def _calculate_molding_work(self, query_lower: str):
        return await self._carpentry_fallback("listverk", 80)
        
    async def _calculate_carpenter_hourly(self, query_lower: str):
        return await self._carpentry_fallback("tømrer timepris", 725)
        
    async def _carpentry_general_fallback(self, query_lower: str, area: float):
        return await self._carpentry_fallback(f"tømrerarbeid {area:.0f}m²", area * 600)
        
    async def _calculate_roof_replacement(self, query_lower: str, area: float):
        return await self._roofing_fallback(f"takomlegging {area:.0f}m²", area * 2300)
        
    async def _calculate_gutters(self, query_lower: str):
        return await self._roofing_fallback("takrenner", 350)
        
    async def _calculate_exterior_insulation(self, query_lower: str, area: float):
        return await self._roofing_fallback(f"etterisolering {area:.0f}m²", area * 2400)
        
    async def _roofing_general_fallback(self, query_lower: str, area: float):
        return await self._roofing_fallback(f"takarbeid {area:.0f}m²", area * 2000)
        
    async def _calculate_blown_insulation(self, query_lower: str, area: float):
        return await self._insulation_fallback(f"blåseisolasjon {area:.0f}m²", area * 280)
        
    async def _calculate_vapor_barrier(self, query_lower: str, area: float):
        return await self._insulation_fallback(f"dampsperre {area:.0f}m²", area * 75)
        
    async def _calculate_air_sealing(self, query_lower: str):
        return await self._insulation_fallback("lufttetting", 25000)
        
    async def _calculate_energy_upgrade(self, query_lower: str, area: float):
        return await self._insulation_fallback(f"energioppgradering {area:.0f}m²", area * 1500)
        
    async def _insulation_general_fallback(self, query_lower: str, area: float):
        return await self._insulation_fallback(f"isolasjonsarbeid {area:.0f}m²", area * 400)
        
    async def _calculate_window_replacement(self, query_lower: str, num_items: int):
        """Calculate window replacement costs using database pricing"""
        try:
            # Use database pricing for windows
            result = self.pricing_service.get_service_price("vindu_standard_komplett", area=num_items)
            
            if "error" not in result:
                total_cost = result.get("total_cost", {}).get("recommended", 0)
                unit_price = result.get("unit_price", {}).get("recommended_price", 0)
            else:
                # Fallback to reasonable estimates
                unit_price = 9500
                total_cost = unit_price * num_items
            
            # Use standardized response template
            title = f"Vindusutskifting - {num_items} {'vindu' if num_items == 1 else 'vinduer'}"
            cost_details = f'<p style="margin-top: 8px; opacity: 0.9; font-size: 14px;">Per vindu: {unit_price:,.0f} NOK</p>'
            
            included_items = [
                "Nye vinduer (standard kvalitet)",
                "Demontering av gamle vinduer", 
                "Montering og tilpasning",
                "Tetting og isolering",
                "Opprydding og bortkjøring"
            ]
            
            notes = "Basert på markedspriser Oslo/Viken 2025. Energieffektive vinduer kan redusere oppvarmingskostnadene med 20-30%."
            
            response = self._create_standard_response(
                title=title,
                total_cost=total_cost,
                cost_details=cost_details,
                included_items=included_items,
                notes=notes
            )
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": total_cost,
                "num_windows": num_items,
                "cost_per_window": unit_price,
                "pricing_source": "database"
            }
            
        except Exception as e:
            return await self._windows_doors_fallback(f"vinduer {num_items} stk", num_items * 9500)
        
    async def _calculate_exterior_door(self, query_lower: str):
        return await self._windows_doors_fallback("ytterdør", 11000)
        
    async def _calculate_interior_doors(self, query_lower: str, num_items: int):
        """Calculate interior door costs using database pricing"""
        try:
            # Check if it's "komplett med karm" or just "dørblad"
            if 'komplett' in query_lower and 'karm' in query_lower:
                # Full door replacement including frame
                unit_price = 5500  # Average for full door replacement
                service_name = "innerdør_standard_komplett"
            else:
                # Just door leaf replacement
                unit_price = 3000  # Average for door leaf only
                service_name = "innerdor_standard_komplett"
            
            # Use fallback pricing (database service not available for doors yet)
            total_cost = unit_price * num_items
            
            # Create standardized response
            title = f"Innerdører - {num_items} {'dør' if num_items == 1 else 'dører'}"
            cost_details = f'<p style="margin-top: 8px; opacity: 0.9; font-size: 14px;">Per dør: {unit_price:,.0f} NOK</p>'
            
            if 'komplett' in query_lower and 'karm' in query_lower:
                included_items = [
                    "Nye innerdører (standard kvalitet)",
                    "Karmer og omramming", 
                    "Demontering av gamle dører",
                    "Montering og justering",
                    "Håndtak og beslag"
                ]
                notes = "Komplett utskifting inkludert karm og all montering. Basert på markedspriser Oslo/Viken 2025."
            else:
                included_items = [
                    "Nye dørblad (standard kvalitet)",
                    "Demontering av gamle dørblad",
                    "Montering på eksisterende karm", 
                    "Justering og tilpasning"
                ]
                notes = "Kun utskifting av dørblad, eksisterende karm beholdes. Basert på markedspriser Oslo/Viken 2025."
            
            response = self._create_standard_response(
                title=title,
                total_cost=total_cost,
                cost_details=cost_details,
                included_items=included_items,
                notes=notes
            )
            
            return {
                "response": response,
                "agent_used": self.agent_name,
                "total_cost": total_cost,
                "num_doors": num_items,
                "cost_per_door": unit_price,
                "pricing_source": "fallback"
            }
            
        except Exception as e:
            return await self._windows_doors_fallback(f"innerdører {num_items} stk", num_items * 3000)
        
    async def _calculate_roof_windows(self, query_lower: str):
        return await self._windows_doors_fallback("takvindu", 35000)
        
    async def _windows_doors_general_fallback(self, query_lower: str, num_items: int):
        return await self._windows_doors_fallback(f"vindu/dør {num_items} stk", num_items * 8000)