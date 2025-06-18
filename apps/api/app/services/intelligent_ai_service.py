from typing import Dict, Any, List, Optional
import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IntelligentAIService:
    """
    Intelligent AI service that provides contextual follow-up questions
    and understands complex renovation projects using OpenAI GPT-4o-mini
    """
    
    def __init__(self, agent_name: str = "renovation"):
        self.agent_name = agent_name
        
        # Load agent-specific API key
        api_key_env = f"OPENAI_API_KEY_{agent_name.upper()}"
        self.api_key = os.getenv(api_key_env)
        
        if not self.api_key:
            raise ValueError(f"No OpenAI API key found for agent '{agent_name}'. Please set {api_key_env}")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Conversation context for this agent
        self.context = {
            "agent_name": agent_name,
            "expertise_area": self._get_expertise_area(agent_name),
            "current_session": None
        }
    
    def _get_expertise_area(self, agent_name: str) -> str:
        """Get expertise area for different agents"""
        expertise_map = {
            "renovation": "oppussing, bygg, håndverk og prisestimering",
            "loan": "boliglån, finansiering og kreditt",
            "energy": "energi, strømpriser og energieffektivisering"
        }
        return expertise_map.get(agent_name, "generell rådgivning")
    
    async def generate_intelligent_followup(
        self, 
        user_query: str, 
        project_type: str = None,
        conversation_history: List[Dict] = None,
        missing_info: List[str] = None,
        learning_service = None
    ) -> Dict[str, Any]:
        """
        Generate intelligent follow-up questions based on user query and context
        """
        
        try:
            # Build context for the AI
            system_prompt = self._build_system_prompt(project_type)
            
            # Add learned patterns if learning service available
            if learning_service and project_type:
                try:
                    learned_prompt = await learning_service.get_improved_ai_prompt(project_type)
                    if learned_prompt:
                        system_prompt += learned_prompt
                except Exception as e:
                    print(f"Failed to get learned patterns: {e}")
            
            user_context = self._build_user_context(user_query, conversation_history, missing_info)
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                temperature=0.3,  # Lower temperature for more consistent responses
                max_tokens=400,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            response_content = response.choices[0].message.content.strip()
            if not response_content:
                raise ValueError("Empty response from AI")
            ai_response = json.loads(response_content)
            
            return {
                "success": True,
                "follow_up_question": ai_response.get("follow_up_question", ""),
                "reasoning": ai_response.get("reasoning", ""),
                "information_needed": ai_response.get("information_needed", []),
                "estimated_complexity": ai_response.get("complexity", "medium"),
                "suggested_next_steps": ai_response.get("next_steps", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_question": self._get_fallback_question(project_type, user_query)
            }
    
    def _build_system_prompt(self, project_type: str = None) -> str:
        """Build system prompt for the AI"""
        
        base_prompt = f"""Du er en ekspert innen {self.context['expertise_area']} og jobber som rådgiver for househacker.
        
Din oppgave er å stille intelligente oppfølgingsspørsmål som hjelper med å:
1. Forstå prosjektets omfang og kompleksitet
2. Samle inn nødvendig informasjon for nøyaktig prisestimering
3. Identifisere potensielle utfordringer eller spesielle behov

VIKTIGE RETNINGSLINJER:
- Still kun 1-2 spesifikke spørsmål om gangen
- Spørsmålene skal være relevante for prisberegning
- Bruk norsk språk, vær vennlig og jordnær
- Forstå at detaljer varierer drastisk mellom prosjekttyper

For MALING spesielt, må du forstå:
- Innvendig vs utvendig (helt forskjellige prosjekter)
- Innvendig: vegg/tak, sparkling (skjøter/hel/små sår), gulvflate vs faktiske flater, vinduer/dører (reduserer areal), lister/karmer
- Utvendig: etasjer, stillas/lift behov, ny farge (kan kreve flere strøk)

Returner alltid JSON med følgende struktur:
{{
  "follow_up_question": "Det konkrete spørsmålet du vil stille",
  "reasoning": "Hvorfor dette spørsmålet er viktig for prisestimering", 
  "information_needed": ["liste", "av", "informasjon", "som", "trengs"],
  "complexity": "low/medium/high",
  "next_steps": ["hva", "som", "skjer", "etter", "dette", "spørsmålet"]
}}"""

        # Add project-specific context
        if project_type == "maling":
            base_prompt += """

SPESIELT FOR MALING:
- Første spørsmål bør alltid være innvendig vs utvendig
- Følg opp basert på svar med relevante detaljer
- Husk at maling er komplekst og krever mange spesifikasjoner"""

        return base_prompt
    
    def _build_user_context(
        self, 
        user_query: str, 
        conversation_history: List[Dict] = None,
        missing_info: List[str] = None
    ) -> str:
        """Build user context for the AI"""
        
        context_parts = [
            f"Brukerens spørsmål: '{user_query}'",
            f"Tidspunkt: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ]
        
        if conversation_history:
            context_parts.append("Samtalehistorikk:")
            for msg in conversation_history[-3:]:  # Only last 3 messages for context
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                context_parts.append(f"- {role}: {content}")
        
        if missing_info:
            context_parts.append(f"Manglende informasjon identifisert: {', '.join(missing_info)}")
        
        context_parts.append("\nHva er det beste oppfølgingsspørsmålet for å hjelpe med prisestimering?")
        
        return "\n".join(context_parts)
    
    def _get_fallback_question(self, project_type: str, user_query: str) -> str:
        """Fallback question if AI fails"""
        
        if project_type == "maling" or "mal" in user_query.lower():
            return "Er dette innvendig eller utvendig maling du tenker på?"
        elif "bad" in user_query.lower():
            return "Hvor stort er badet, og tenker du standard kvalitet eller høy standard?"
        elif "kjøkken" in user_query.lower():
            return "Hvor stort er kjøkkenet, og skal det være nye skap eller kun fronter?"
        else:
            return "Kan du fortelle meg litt mer om omfanget av prosjektet?"
    
    async def analyze_project_complexity(
        self, 
        user_query: str, 
        collected_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze the complexity of a project based on user input
        """
        
        try:
            system_prompt = f"""Du er en ekspert innen {self.context['expertise_area']}.
            
Analyser prosjektkompleksiteten basert på brukerens beskrivelse og eventuelle innsamlede informasjon.

Returner JSON med:
{{
  "complexity": "low/medium/high",
  "estimated_timeline": "tidsestimat", 
  "key_challenges": ["utfordring1", "utfordring2"],
  "specialist_needed": ["type håndverker som trengs"],
  "rough_price_range": "prisklasse i norske kroner"
}}"""

            user_context = f"Prosjektbeskrivelse: {user_query}"
            if collected_info:
                user_context += f"\nInnsamlet informasjon: {json.dumps(collected_info, ensure_ascii=False)}"
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                temperature=0.2,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "complexity": "medium",
                "estimated_timeline": "2-4 uker",
                "key_challenges": ["Krever profesjonell vurdering"],
                "specialist_needed": ["Tverrfaglig kompetanse"],
                "rough_price_range": "Avhenger av omfang og kvalitet"
            }