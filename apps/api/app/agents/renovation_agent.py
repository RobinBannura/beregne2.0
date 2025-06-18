from typing import Dict, Any, List
import httpx
import json
import re
from .base_agent import BaseAgent

class RenovationAgent(BaseAgent):
    """
    Spesialisert agent for oppussing og renovering
    - Materialkalkulator for ulike prosjekter
    - Prisestimering fra byggvarehus (Maxbo, Byggmax, etc.)
    - Arbeidsestimater og tidsberegninger
    - Verktøy og utstyrslister
    """
    
    def __init__(self):
        super().__init__()
        self.agent_name = "renovation"
        
        # Materialkonstanter og faktorer
        self.MATERIALS = {
            "maling": {
                "dekning_per_liter": 10,  # m² per liter
                "pris_per_liter": 250,  # Estimert pris NOK
                "lag": 2  # Antall lag normalt
            },
            "fliser": {
                "spill_faktor": 0.1,  # 10% spill
                "pris_per_m2": 300,  # Estimert pris NOK per m²
                "fugemasse_per_m2": 0.5  # kg per m²
            },
            "laminat": {
                "spill_faktor": 0.08,  # 8% spill
                "pris_per_m2": 200,  # Estimert pris NOK per m²
            },
            "gips": {
                "kg_per_m2": 1.2,  # kg gips per m²
                "pris_per_kg": 15
            },
            "isolasjon": {
                "pris_per_m2_100mm": 45,  # NOK per m² for 100mm tykkelse
                "tykkelse_faktor": {
                    "50mm": 0.6,
                    "100mm": 1.0,
                    "150mm": 1.4,
                    "200mm": 1.8
                }
            }
        }
        
        self.ROOM_TYPES = {
            "bad": {
                "fliser_andel": 0.8,  # 80% fliser
                "maling_andel": 0.2,  # 20% maling
                "ventilasjon_krav": True
            },
            "kjøkken": {
                "fliser_andel": 0.6,
                "maling_andel": 0.4,
                "ventilasjon_krav": True
            },
            "stue": {
                "laminat_andel": 1.0,
                "maling_andel": 1.0
            },
            "soverom": {
                "laminat_andel": 1.0,
                "maling_andel": 1.0
            }
        }

    def can_handle(self, query: str) -> bool:
        """Sjekker om agenten kan håndtere spørringen"""
        renovation_keywords = [
            'oppussing', 'renovering', 'bygge', 'maling', 'fliser', 'gulv',
            'bad', 'kjøkken', 'materialer', 'kostnad', 'pris', 'laminat',
            'gips', 'isolasjon', 'tapet', 'verktøy', 'byggekostnad',
            'kvadratmeter', 'm2', 'maxbo', 'byggmax', 'byggvarehus'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in renovation_keywords)

    async def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prosesserer oppussingsspørringer"""
        try:
            # Analyser spørringen
            analysis = self._analyze_renovation_query(query)
            
            if analysis["type"] == "material_calculation":
                result = await self._calculate_materials(analysis, query)
            elif analysis["type"] == "price_estimation":
                result = await self._estimate_prices(analysis, query)
            elif analysis["type"] == "room_renovation":
                result = await self._calculate_room_renovation(analysis, query)
            elif analysis["type"] == "contextual_renovation":
                # Handle contextual responses like "standard kvalitet og 5 kvm"
                result = await self._calculate_room_renovation(analysis, query)
            else:
                result = await self._general_renovation_advice(query)
            
            return {
                "response": result["response"],
                "agent_used": self.agent_name,
                "calculation_details": result.get("details", {}),
                "materials_list": result.get("materials", []),
                "estimated_cost": result.get("cost", None)
            }
            
        except Exception as e:
            return {
                "response": f"Beklager, jeg kunne ikke behandle din oppussingsspørring: {str(e)}",
                "agent_used": self.agent_name,
                "error": str(e)
            }

    def _analyze_renovation_query(self, query: str) -> Dict[str, Any]:
        """Analyserer typen oppussingsspørring"""
        query_lower = query.lower()
        
        # Ekstraherer tall og enheter
        area_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:m2|m²|kvadratmeter|kvm)', query_lower)
        area = float(area_match.group(1).replace(',', '.')) if area_match else None
        
        room_match = re.search(r'(bad|kjøkken|stue|soverom|gang|entre)', query_lower)
        room_type = room_match.group(1) if room_match else None
        
        # Identifiser materialer
        materials = []
        for material in self.MATERIALS.keys():
            if material in query_lower:
                materials.append(material)
        
        # Smart detection for contextual responses
        # If we have area + quality indicators but no explicit room type,
        # this is likely a contextual response to a previous room question
        has_quality_indicators = any(word in query_lower for word in ['standard', 'kvalitet', 'normal', 'høy', 'enkel', 'premium'])
        is_contextual_response = area and has_quality_indicators and not room_type
        
        # Bestem type spørring
        if any(word in query_lower for word in ['mengde', 'antall', 'materiale', 'materialer']) or \
           ('hvor mye' in query_lower and any(mat in query_lower for mat in ['maling', 'fliser', 'laminat', 'gips'])):
            query_type = "material_calculation"
        elif any(word in query_lower for word in ['kostnad', 'pris', 'koster']):
            query_type = "price_estimation"
        elif room_type:
            query_type = "room_renovation"
        elif is_contextual_response:
            # Treat contextual responses with area+quality as renovation requests
            query_type = "contextual_renovation"
            # Default to bathroom for contextual responses (most common)
            room_type = "bad"
        else:
            query_type = "general"
        
        return {
            "type": query_type,
            "area": area,
            "room_type": room_type,
            "materials": materials,
            "original_query": query,
            "is_contextual": is_contextual_response
        }

    async def _calculate_materials(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Beregner nødvendige materialmengder"""
        area = analysis.get("area")
        materials = analysis.get("materials", [])
        
        if not area:
            return {
                "response": "For å beregne materialer trenger jeg arealet. Kan du oppgi kvadratmeter?",
                "details": {}
            }
        
        calculations = {}
        total_cost = 0
        materials_list = []
        
        # Beregn for hvert material
        for material in materials:
            if material == "maling":
                calc = self._calculate_paint(area)
            elif material == "fliser":
                calc = self._calculate_tiles(area)
            elif material == "laminat":
                calc = self._calculate_laminate(area)
            elif material == "gips":
                calc = self._calculate_gypsum(area)
            else:
                continue
            
            calculations[material] = calc
            total_cost += calc["total_cost"]
            materials_list.extend(calc["items"])
        
        # Generer respons
        response = f"<h3>Materialkalkulator for {area} m²</h3>\n\n"
        
        for material, calc in calculations.items():
            response += f"<h4>{material.title()}</h4>\n"
            response += f"<ul>\n"
            for item in calc["items"]:
                response += f"<li>{item['name']}: {item['quantity']} {item['unit']} (ca. {item['cost']:.0f} NOK)</li>\n"
            response += f"</ul>\n"
            response += f"<strong>Delsum {material}: {calc['total_cost']:.0f} NOK</strong>\n\n"
        
        response += f"<h4>Totalkostnad materialer: {total_cost:.0f} NOK</h4>\n"
        response += f"<small>💡 Prisene er estimerte og kan variere mellom leverandører</small>"
        
        return {
            "response": response,
            "details": calculations,
            "materials": materials_list,
            "cost": total_cost
        }

    def _calculate_paint(self, area: float) -> Dict[str, Any]:
        """Beregner malingsbehov"""
        material = self.MATERIALS["maling"]
        liters_needed = (area * material["lag"]) / material["dekning_per_liter"]
        liters_needed = round(liters_needed + 0.5)  # Rund opp med buffer
        
        cost = liters_needed * material["pris_per_liter"]
        
        return {
            "total_cost": cost,
            "items": [
                {
                    "name": "Maling (vegg/tak)",
                    "quantity": liters_needed,
                    "unit": "liter",
                    "cost": cost
                },
                {
                    "name": "Ruller og pensler",
                    "quantity": 1,
                    "unit": "sett",
                    "cost": 300
                }
            ]
        }

    def _calculate_tiles(self, area: float) -> Dict[str, Any]:
        """Beregner flisbehov"""
        material = self.MATERIALS["fliser"]
        tiles_needed = area * (1 + material["spill_faktor"])
        fugemasse_needed = area * material["fugemasse_per_m2"]
        
        tile_cost = tiles_needed * material["pris_per_m2"]
        adhesive_cost = area * 50  # 50 NOK per m² for lim
        grout_cost = fugemasse_needed * 25  # 25 NOK per kg fugemasse
        
        total_cost = tile_cost + adhesive_cost + grout_cost
        
        return {
            "total_cost": total_cost,
            "items": [
                {
                    "name": "Fliser",
                    "quantity": round(tiles_needed, 1),
                    "unit": "m²",
                    "cost": tile_cost
                },
                {
                    "name": "Flislim",
                    "quantity": round(area * 1.2, 1),
                    "unit": "kg",
                    "cost": adhesive_cost
                },
                {
                    "name": "Fugemasse",
                    "quantity": round(fugemasse_needed, 1),
                    "unit": "kg",
                    "cost": grout_cost
                }
            ]
        }

    def _calculate_laminate(self, area: float) -> Dict[str, Any]:
        """Beregner laminatbehov"""
        material = self.MATERIALS["laminat"]
        laminate_needed = area * (1 + material["spill_faktor"])
        
        laminate_cost = laminate_needed * material["pris_per_m2"]
        underlay_cost = area * 30  # 30 NOK per m² for underlag
        
        total_cost = laminate_cost + underlay_cost
        
        return {
            "total_cost": total_cost,
            "items": [
                {
                    "name": "Laminat",
                    "quantity": round(laminate_needed, 1),
                    "unit": "m²",
                    "cost": laminate_cost
                },
                {
                    "name": "Underlag",
                    "quantity": area,
                    "unit": "m²",
                    "cost": underlay_cost
                },
                {
                    "name": "Lister og tilbehør",
                    "quantity": 1,
                    "unit": "sett",
                    "cost": 500
                }
            ]
        }

    def _calculate_gypsum(self, area: float) -> Dict[str, Any]:
        """Beregner gipsbehov"""
        material = self.MATERIALS["gips"]
        gypsum_needed = area * material["kg_per_m2"]
        cost = gypsum_needed * material["pris_per_kg"]
        
        return {
            "total_cost": cost,
            "items": [
                {
                    "name": "Gips/sparkel",
                    "quantity": round(gypsum_needed, 1),
                    "unit": "kg",
                    "cost": cost
                }
            ]
        }

    async def _estimate_prices(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Estimerer priser for oppussingsprosjekt"""
        # Her kan vi i fremtiden integrere med Maxbo API
        area = analysis.get("area", 50)  # Default 50m² hvis ikke oppgitt
        
        # Basis prisestimater
        estimates = {
            "bad_komplett": {
                "lav": 15000,
                "middels": 25000,
                "høy": 40000,
                "per_m2": True
            },
            "kjøkken_komplett": {
                "lav": 20000,
                "middels": 35000,
                "høy": 60000,
                "per_m2": True
            },
            "maling_rom": {
                "lav": 200,
                "middels": 400,
                "høy": 800,
                "per_m2": True
            }
        }
        
        response = f"<h3>Prisestimat for oppussing</h3>\n"
        response += f"<p>Basert på {area} m² gulvareal</p>\n\n"
        
        for project, prices in estimates.items():
            if any(word in query.lower() for word in project.split("_")):
                response += f"<h4>{project.replace('_', ' ').title()}</h4>\n"
                response += f"<ul>\n"
                response += f"<li>Enkelt utførelse: {prices['lav'] * area if prices['per_m2'] else prices['lav']:,.0f} NOK</li>\n"
                response += f"<li>Standard utførelse: {prices['middels'] * area if prices['per_m2'] else prices['middels']:,.0f} NOK</li>\n"
                response += f"<li>Høy standard: {prices['høy'] * area if prices['per_m2'] else prices['høy']:,.0f} NOK</li>\n"
                response += f"</ul>\n\n"
        
        response += "<small>💡 Prisene inkluderer materialer og arbeid. Elektriker/rørlegger kommer i tillegg.</small>"
        
        return {
            "response": response,
            "details": estimates,
            "cost": estimates.get("middels", 0) * area
        }

    async def _calculate_room_renovation(self, analysis: Dict, query: str) -> Dict[str, Any]:
        """Beregner komplett romrenovering"""
        room_type = analysis["room_type"]
        area = analysis.get("area", 10)  # Default 10m² hvis ikke oppgitt
        
        room_config = self.ROOM_TYPES.get(room_type, self.ROOM_TYPES["stue"])
        
        calculations = {}
        total_cost = 0
        materials_list = []
        
        # Beregn materialer basert på romtype
        if "fliser_andel" in room_config:
            tile_area = area * room_config["fliser_andel"]
            calc = self._calculate_tiles(tile_area)
            calculations["fliser"] = calc
            total_cost += calc["total_cost"]
            materials_list.extend(calc["items"])
        
        if "laminat_andel" in room_config:
            laminate_area = area * room_config["laminat_andel"]
            calc = self._calculate_laminate(laminate_area)
            calculations["laminat"] = calc
            total_cost += calc["total_cost"]
            materials_list.extend(calc["items"])
        
        if "maling_andel" in room_config:
            # Estimer veggarealet (høyde 2.5m, trekk fra dører/vinduer)
            wall_area = (area * 0.8) * 2.5  # Approksimering
            calc = self._calculate_paint(wall_area)
            calculations["maling"] = calc
            total_cost += calc["total_cost"]
            materials_list.extend(calc["items"])
        
        # Generer respons
        response = f"<h3>Komplett {room_type}srenovering - {area} m²</h3>\n\n"
        
        for material, calc in calculations.items():
            response += f"<h4>{material.title()}</h4>\n"
            response += f"<ul>\n"
            for item in calc["items"]:
                response += f"<li>{item['name']}: {item['quantity']} {item['unit']} (ca. {item['cost']:.0f} NOK)</li>\n"
            response += f"</ul>\n"
        
        # Legg til arbeidskostnad (50% av materialkostnad)
        labor_cost = total_cost * 0.5
        total_with_labor = total_cost + labor_cost
        
        response += f"\n<h4>Kostnadssammendrag</h4>\n"
        response += f"<ul>\n"
        response += f"<li>Materialer: {total_cost:.0f} NOK</li>\n"
        response += f"<li>Arbeid (estimat): {labor_cost:.0f} NOK</li>\n"
        response += f"<li><strong>Totalt: {total_with_labor:.0f} NOK</strong></li>\n"
        response += f"</ul>\n\n"
        
        if room_config.get("ventilasjon_krav"):
            response += "<small>⚠️ Husk ventilasjon og eventuelle elektriker/rørleggerarbeider</small>"
        
        return {
            "response": response,
            "details": calculations,
            "materials": materials_list,
            "cost": total_with_labor
        }

    async def _general_renovation_advice(self, query: str) -> Dict[str, Any]:
        """Gir generelle oppussingsråd"""
        response = "<h3>Oppussingsrådgiver</h3>\n\n"
        response += "<p>Jeg kan hjelpe deg med:</p>\n"
        response += "<ul>\n"
        response += "<li>📏 <strong>Materialkalkulator</strong> - 'Hvor mye maling trenger jeg til 25 m²?'</li>\n"
        response += "<li>💰 <strong>Kostnadsestimater</strong> - 'Hva koster det å pusse opp et bad på 8 m²?'</li>\n"
        response += "<li>🛠️ <strong>Romrenovering</strong> - 'Komplett kjøkkenrenovering 15 m²'</li>\n"
        response += "<li>🏪 <strong>Prissammenligning</strong> - Estimerte priser fra byggvarehus</li>\n"
        response += "</ul>\n\n"
        response += "<p><strong>Tips:</strong> Oppgi alltid arealet i kvadratmeter for beste resultater!</p>\n"
        response += "<small>💡 Støttede materialer: maling, fliser, laminat, gips, isolasjon</small>"
        
        return {
            "response": response,
            "details": {}
        }

    async def get_maxbo_prices(self, search_term: str) -> List[Dict]:
        """
        Henter priser fra Maxbo (placeholder for fremtidig API-integrasjon)
        """
        # TODO: Implementer API-kall til Maxbo når tilgjengelig
        # For nå returnerer vi mock-data
        
        mock_prices = {
            "maling": [
                {"name": "Jotun Lady Supreme Finish", "price": 289, "unit": "liter"},
                {"name": "Beckers Elegant", "price": 245, "unit": "liter"},
                {"name": "Nordsjö Ambiance", "price": 267, "unit": "liter"}
            ],
            "fliser": [
                {"name": "Keramiske gulvfliser 30x30", "price": 299, "unit": "m²"},
                {"name": "Porselensfliser 60x60", "price": 459, "unit": "m²"},
                {"name": "Naturstein", "price": 699, "unit": "m²"}
            ]
        }
        
        return mock_prices.get(search_term.lower(), [])