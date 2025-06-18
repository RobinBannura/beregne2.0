from typing import Dict, Any, Optional, List
import httpx
import json
import re
import os

class AIQueryAnalyzer:
    """
    AI-powered query analysis for renovation queries
    Replaces regex-based analysis with intelligent understanding
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    async def analyze_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze renovation query using AI for better understanding
        Returns structured analysis including project type, intent, missing info
        """
        
        # Build the AI prompt for query analysis
        analysis_prompt = self._build_analysis_prompt(query, context)
        
        try:
            # Call OpenAI API for analysis
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",  # Fast and cost-effective
                        "messages": [
                            {
                                "role": "system", 
                                "content": "You are an expert renovation consultant analyzing Norwegian customer queries. Respond only with valid JSON."
                            },
                            {
                                "role": "user", 
                                "content": analysis_prompt
                            }
                        ],
                        "temperature": 0.1,  # Low temperature for consistent analysis
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    ai_response = response.json()
                    analysis_text = ai_response["choices"][0]["message"]["content"]
                    
                    # Parse JSON response
                    try:
                        analysis = json.loads(analysis_text)
                        return self._validate_and_enhance_analysis(analysis, query)
                    except json.JSONDecodeError:
                        # Fallback to regex if AI response is invalid
                        return self._fallback_regex_analysis(query)
                else:
                    # Fallback to regex if API fails
                    return self._fallback_regex_analysis(query)
                    
        except Exception as e:
            print(f"AI analysis failed: {e}")
            # Fallback to regex analysis
            return self._fallback_regex_analysis(query)
    
    def _build_analysis_prompt(self, query: str, context: str) -> str:
        """Build prompt for AI analysis"""
        
        prompt = f"""Analyze this Norwegian renovation query and respond with JSON only:

Query: "{query}"
{f"Context: {context}" if context else ""}

Determine:
1. Project type (bad_komplett, kjøkken_detaljert, maling, elektriker_arbeid, gulvarbeider, vinduer_dorer, tomrer_bygg, tak_ytterkledning, isolasjon_tetting, grunnarbeider)
2. Analysis type (full_project_estimate, material_and_labor, price_comparison, painting_specific, electrical_work, groundwork, flooring_work, carpentry_work, roofing_cladding_work, insulation_work, windows_doors_work, detailed_breakdown, quote_request, project_registration, about_househacker, needs_clarification)
3. Area/quantity if mentioned
4. Specific requirements or preferences
5. Missing information needed for accurate estimate
6. Whether query is ambiguous and needs clarification

Respond with this exact JSON structure:
{{
    "type": "analysis_type_here",
    "project_type": "project_type_here", 
    "area": number_or_null,
    "quantity": number_or_null,
    "room_type": "room_name_or_null",
    "requirements": ["list", "of", "requirements"],
    "preferences": {{"quality": "budget/mid/premium", "brands": []}},
    "missing_info": ["what", "info", "is", "needed"],
    "is_ambiguous": true_or_false,
    "confidence": 0.0_to_1.0,
    "reasoning": "brief explanation"
}}

Examples:
- "male stue og gang 45 kvm" → type: "painting_specific", project_type: "maling", area: 45, room_type: "stue_gang"
- "bytte 5 dører" → type: "needs_clarification", is_ambiguous: true, missing_info: ["door_type", "interior_or_exterior"]
- "pusse opp bad 6 kvm" → type: "full_project_estimate", project_type: "bad_komplett", area: 6, room_type: "bad"
- "parkett hele leiligheten" → type: "flooring_work", project_type: "gulvarbeider", missing_info: ["total_area"]
"""
        
        return prompt
    
    def _validate_and_enhance_analysis(self, analysis: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Validate and enhance AI analysis with fallback logic"""
        
        # Ensure required fields exist
        if "type" not in analysis:
            analysis["type"] = "needs_clarification"
        
        if "project_type" not in analysis:
            analysis["project_type"] = self._guess_project_type_from_query(query)
        
        if "confidence" not in analysis:
            analysis["confidence"] = 0.7
        
        # Add some fallback logic for common cases
        query_lower = query.lower()
        
        # Area extraction fallback
        if not analysis.get("area"):
            area_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:m²|m2|kvadratmeter|kvm)', query_lower)
            if area_match:
                analysis["area"] = float(area_match.group(1))
        
        # Quantity extraction fallback  
        if not analysis.get("quantity"):
            qty_patterns = [
                r'(\d+)\s*(?:stk|vindu|vinduer|dør|dører|innerdør|innerdører|ytterdør)',
                r'(\d+)\s*(?:rom|soverom|bad|kjøkken)'
            ]
            for pattern in qty_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    analysis["quantity"] = int(match.group(1))
                    break
        
        # Set needs_clarification flag
        analysis["needs_clarification"] = analysis.get("is_ambiguous", False) or len(analysis.get("missing_info", [])) > 2
        
        return analysis
    
    def _guess_project_type_from_query(self, query: str) -> str:
        """Fallback project type detection"""
        query_lower = query.lower()
        
        project_patterns = [
            (r'bad|baderom|toalett', 'bad_komplett'),
            (r'kjøkken|kitchen', 'kjøkken_detaljert'),
            (r'mal\w+|maling', 'maling'),
            (r'elektriker|elektrisk|stikkontakt|sikringsskap', 'elektriker_arbeid'),
            (r'gulv|parkett|laminat|vinyl', 'gulvarbeider'),
            (r'vindu|vinduer|dør|dører', 'vinduer_dorer'),
            (r'tømrer|lettvegg|skillevegg|himling', 'tomrer_bygg'),
            (r'tak|takomlegging|ytterkledning', 'tak_ytterkledning'),
            (r'isolasjon|isolering|energioppgradering', 'isolasjon_tetting'),
            (r'graving|grunnmur|fundamentering', 'grunnarbeider')
        ]
        
        for pattern, project_type in project_patterns:
            if re.search(pattern, query_lower):
                return project_type
        
        return "needs_clarification"
    
    def _fallback_regex_analysis(self, query: str) -> Dict[str, Any]:
        """Fallback regex-based analysis when AI fails"""
        query_lower = query.lower()
        
        # Basic regex analysis (simplified version of original)
        analysis = {
            "type": "needs_clarification",
            "project_type": self._guess_project_type_from_query(query),
            "area": None,
            "quantity": None,
            "room_type": None,
            "requirements": [],
            "preferences": {},
            "missing_info": ["detailed_requirements"],
            "is_ambiguous": True,
            "confidence": 0.5,
            "reasoning": "Fallback regex analysis due to AI failure",
            "needs_clarification": True
        }
        
        # Extract area
        area_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:m²|m2|kvadratmeter|kvm)', query_lower)
        if area_match:
            analysis["area"] = float(area_match.group(1))
            analysis["type"] = "full_project_estimate"
            analysis["confidence"] = 0.7
        
        # Extract quantity
        qty_match = re.search(r'(\d+)\s*(?:stk|vindu|vinduer|dør|dører)', query_lower)
        if qty_match:
            analysis["quantity"] = int(qty_match.group(1))
            analysis["type"] = "full_project_estimate"
            analysis["confidence"] = 0.7
        
        return analysis
    
    async def generate_followup_questions(self, query: str, analysis: Dict[str, Any], 
                                        context: str = "") -> List[str]:
        """Generate intelligent follow-up questions based on analysis"""
        
        if not analysis.get("missing_info"):
            return []
        
        prompt = f"""Generate 2-3 intelligent follow-up questions in Norwegian for this renovation query:

Query: "{query}"
Context: {context}
Missing info: {analysis.get('missing_info', [])}
Project type: {analysis.get('project_type', 'unknown')}

Generate practical, specific questions that help us provide accurate pricing. 
Questions should be:
- Short and clear
- Focused on missing information
- Professional tone
- In Norwegian

Respond with JSON array of questions:
["question 1", "question 2", "question 3"]
"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a Norwegian renovation expert. Respond only with valid JSON array."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 200
                    }
                )
                
                if response.status_code == 200:
                    ai_response = response.json()
                    questions_text = ai_response["choices"][0]["message"]["content"]
                    return json.loads(questions_text)
                    
        except Exception as e:
            print(f"Failed to generate follow-up questions: {e}")
        
        # Fallback questions based on missing info
        return self._generate_fallback_questions(analysis)
    
    def _generate_fallback_questions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate fallback questions when AI fails"""
        missing_info = analysis.get("missing_info", [])
        project_type = analysis.get("project_type", "")
        
        questions = []
        
        if "total_area" in missing_info or "area" in missing_info:
            if "bad" in project_type:
                questions.append("Hvor stort er badet i kvadratmeter?")
            elif "kjøkken" in project_type:
                questions.append("Hvor stort er kjøkkenet?")
            else:
                questions.append("Hvor mange kvadratmeter skal behandles?")
        
        if "door_type" in missing_info:
            questions.append("Skal du skifte innerdører eller ytterdører?")
        
        if "quality_level" in missing_info:
            questions.append("Ønsker du rimelige, midt-segment eller premium løsninger?")
        
        return questions[:3]  # Max 3 questions