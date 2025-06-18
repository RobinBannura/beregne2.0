from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from .enhanced_renovation_agent import EnhancedRenovationAgent
from ..services.project_registration_service import ProjectRegistrationService, RegistrationStage
from ..services.intelligent_ai_service import IntelligentAIService
from ..services.conversation_learning_service import ConversationLearningService

class ConversationalRenovationAgent(EnhancedRenovationAgent):
    """
    Human-like conversational renovation agent that combines:
    - Expert pricing knowledge from EnhancedRenovationAgent
    - Natural conversation flow
    - Seamless project registration
    - Personality and warmth
    """
    
    def __init__(self):
        super().__init__()
        self.agent_name = "conversational_renovation"
        
        # Initialize services
        self.registration_service = ProjectRegistrationService()
        
        # Initialize intelligent AI service for smart follow-ups
        try:
            self.intelligent_ai = IntelligentAIService(agent_name="renovation")
        except Exception as e:
            print(f"Intelligent AI service initialization failed: {e}")
            self.intelligent_ai = None
        
        # Initialize conversation learning service
        try:
            self.learning_service = ConversationLearningService(db=self.db)
        except Exception as e:
            print(f"Learning service initialization failed: {e}")
            self.learning_service = None
        
        # Conversation state tracking
        self.conversation_stages = [
            "greeting", "needs_assessment", "pricing_discussion", 
            "expertise_sharing", "registration_offer", "project_details",
            "contact_collection", "confirmation"
        ]
        
        # Personality traits
        self.personality = {
            "tone": "vennlig og jordnær",
            "expertise_level": "erfaren fagperson",
            "approach": "gir verdi først",
            "style": "ett spørsmål om gangen"
        }
        
        # Current date/time awareness
        self.current_time = datetime.now()
        self.season = self._get_current_season()
        
    def _get_current_season(self) -> str:
        """Get current season for contextual advice"""
        month = self.current_time.month
        if month in [12, 1, 2]:
            return "vinter"
        elif month in [3, 4, 5]:
            return "vår"
        elif month in [6, 7, 8]:
            return "sommer"
        else:
            return "høst"
    
    def _get_seasonal_context(self, project_type: str) -> str:
        """Get seasonal advice for different project types"""
        seasonal_advice = {
            "vinter": {
                "ytterkledning": "Vintermonedene er faktisk perfekt for innendørs planlegging av utvendige prosjekter. Mange entreprenører har bedre tid nå, og du kan få gode avtaler for arbeid til våren! ❄️",
                "bad": "Perfekt timing for badrenovering! Entreprenører har god kapasitet i vintersesongen, og du får prosjektet ferdig før sommeren. 🛁",
                "kjøkken": "Kjøkkenrenovering i vintermonedene? Smart valg! Du slipper støv og støy når du kan holde vinduene lukket. ⛄",
                "default": "Vintermonedene er ofte en god tid for innendørs prosjekter - entreprenører har gjerne bedre kapasitet nå! ❄️"
            },
            "vår": {
                "ytterkledning": "Perfekt timing! Våren er høysesong for utvendige prosjekter. Book tidlig for beste valg av entreprenører! 🌸",
                "gulv": "Våren er ideell for gulvprosjekter - du får tørket ut fuktighet fra vinteren og perfekt temperatur for installasjon. 🌱",
                "default": "Våren er en travel tid for entreprenører - men også når de fleste prosjektene starter! 🌸"
            },
            "sommer": {
                "tak": "Sommersesongen er gullstandard for takarbeid! Tørt vær og lange dager gir perfekte arbeidsforhold. ☀️",
                "ytterkledning": "Ideell tid for fasadeprosjekter! Tørt vær og optimale temperaturer. Men book tidlig - det er høysesong! 🏖️",
                "default": "Sommeren er travel tid for entreprenører, spesielt utendørs arbeid. Planlegg i god tid! ☀️"
            },
            "høst": {
                "isolasjon": "Høsten er perfekt for isolasjonsprosjekter - du rekker å få det ferdig før kulda setter inn for alvor! 🍂",
                "vinduer": "Smart å bytte vinduer nå - du merker forskjellen straks når kulda kommer! 🍁",
                "default": "Høsten er god tid for både innendørs og utendørs prosjekter før vinterpausen! 🍂"
            }
        }
        
        season_advice = seasonal_advice.get(self.season, {})
        return season_advice.get(project_type, season_advice.get("default", ""))
    
    async def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query with conversational approach and learning"""
        
        # Extract session info for logging (with safe fallbacks)
        session = context.get("session") if context else None
        session_id = getattr(session, 'session_id', None) if session else (context.get("session_id", "unknown") if context else "unknown")
        partner_id = context.get("partner_id", "unknown") if context else "unknown"
        
        # Start conversation logging
        if self.learning_service and session_id != "unknown":
            try:
                await self.learning_service.log_conversation_start(
                    session_id=session_id,
                    partner_id=partner_id,
                    agent_used=self.agent_name
                )
            except Exception as e:
                print(f"Failed to log conversation start: {e}")
        
        # Check if we're in registration mode
        registration_stage = self._get_registration_stage(session)
        
        if registration_stage and registration_stage != RegistrationStage.COMPLETED:
            result = await self._handle_registration_flow(query, context, registration_stage)
        elif self._wants_to_register(query):
            result = await self._start_registration_flow(query, context)
        elif self._is_identity_or_general_question(query):
            # Handle identity and general questions directly
            result = self._create_general_conversational_response(query)
        else:
            # First, get the technical analysis and pricing from parent class
            try:
                technical_result = await super().process(query, context)
                if not technical_result:
                    technical_result = {
                        "response": "Jeg forstod ikke spørsmålet helt. Kan du prøve å omformulere det?",
                        "requires_clarification": False,
                        "total_cost": 0,
                        "agent_used": self.agent_name
                    }
            except Exception as e:
                print(f"Parent process failed: {e}")
                technical_result = {
                    "response": "Det oppstod en teknisk feil. Kan du prøve igjen?",
                    "requires_clarification": False, 
                    "total_cost": 0,
                    "agent_used": self.agent_name
                }
            
            # Then wrap it in conversational response
            result = await self._create_conversational_response(
                query, technical_result, context
            )
        
        # Log the complete message exchange
        if self.learning_service and session_id != "unknown":
            try:
                await self.learning_service.log_message_exchange(
                    session_id=session_id,
                    user_message=query,
                    agent_response=result.get("response", ""),
                    ai_powered=result.get("ai_powered", False),
                    ai_reasoning=result.get("ai_reasoning", ""),
                    project_type_detected=result.get("calculation_details", {}).get("project_type", ""),
                    missing_info=result.get("missing_info", []),
                    led_to_pricing=result.get("total_cost", 0) > 0,
                    led_to_registration=result.get("registration_stage") is not None
                )
            except Exception as e:
                print(f"Failed to log message exchange: {e}")
        
        return result
    
    async def _create_conversational_response(
        self, 
        query: str, 
        technical_result: Dict[str, Any], 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a human-like conversational response"""
        
        # Safe fallback if technical_result is None
        if not technical_result:
            technical_result = {
                "response": "Beklager, jeg kunne ikke behandle spørringen din akkurat nå.",
                "requires_clarification": False,
                "total_cost": 0
            }
        
        # Analyze conversation stage
        session = context.get("session") if context else None
        conversation_stage = self._determine_conversation_stage(query, session)
        
        # Get project type for contextual advice (with safe fallbacks)
        calculation_details = technical_result.get("calculation_details") or {}
        project_type = calculation_details.get("project_type", "") if isinstance(calculation_details, dict) else ""
        
        if technical_result.get("requires_clarification"):
            return await self._wrap_clarification_conversationally(
                technical_result, query, project_type
            )
        
        elif technical_result.get("total_cost", 0) > 0:
            return self._wrap_pricing_conversationally(
                technical_result, query, project_type
            )
        
        else:
            return self._create_general_conversational_response(query)
    
    def _determine_conversation_stage(self, query: str, session: Any) -> str:
        """Determine what stage of conversation we're in"""
        query_lower = query.lower()
        
        # Check for greeting patterns
        if any(word in query_lower for word in ['hei', 'hallo', 'god morgen', 'god dag']):
            return "greeting"
        
        # Check for explicit registration interest
        if any(phrase in query_lower for phrase in ['registrere', 'tilbud', 'entreprenør', 'befaring']):
            return "registration_offer"
        
        # Check for project discussion
        if any(word in query_lower for word in ['bad', 'kjøkken', 'gulv', 'tak', 'maling']):
            return "needs_assessment"
        
        return "needs_assessment"
    
    async def _wrap_clarification_conversationally(
        self, 
        technical_result: Dict[str, Any], 
        query: str, 
        project_type: str
    ) -> Dict[str, Any]:
        """Wrap technical clarification in conversational tone using AI"""
        
        # Create a simple, natural response
        if "bad" in query.lower():
            intro = "Badrenovering er en god investering! 😊"
        elif "kjøkken" in query.lower():
            intro = "Kjøkken er hjertet i hjemmet."
        elif "mal" in query.lower():
            intro = "Maling kan virkelig transformere hjemmet!"
        else:
            intro = "Det høres ut som et spennende prosjekt!"
        
        # Use AI for intelligent follow-up if available
        if self.intelligent_ai:
            try:
                ai_response = await self.intelligent_ai.generate_intelligent_followup(
                    user_query=query,
                    project_type=project_type,
                    missing_info=technical_result.get("missing_info", []),
                    learning_service=self.learning_service
                )
                
                if ai_response.get("success"):
                    follow_up = ai_response.get("follow_up_question", "")
                    conversational_response = f"{intro} {follow_up}"
                    
                    return {
                        **technical_result,
                        "response": conversational_response,
                        "conversation_stage": "pricing_discussion",
                        "personality_applied": True,
                        "ai_powered": True,
                        "ai_reasoning": ai_response.get("reasoning", "")
                    }
            except Exception as e:
                print(f"AI follow-up failed: {e}")
        
        # Fallback to simple questions
        response_parts = [intro]
        
        if "bad" in query.lower():
            response_parts.append("For å gi deg et godt prisestimat trenger jeg å vite:")
            response_parts.append("Hvor stort er badet i kvadratmeter? Og tenker du standard kvalitet, høy standard eller enkel standard?")
        elif "mal" in query.lower():
            response_parts.append("Er dette innvendig eller utvendig maling du tenker på?")
        else:
            response_parts.append("Kan du fortelle meg hvor stort det er og hva slags standard du tenker deg?")
        
        conversational_response = " ".join(response_parts)
        
        return {
            **technical_result,
            "response": conversational_response,
            "conversation_stage": "pricing_discussion",
            "personality_applied": True
        }
    
    def _wrap_pricing_conversationally(
        self, 
        technical_result: Dict[str, Any], 
        query: str, 
        project_type: str
    ) -> Dict[str, Any]:
        """Wrap pricing result in conversational response"""
        
        total_cost = technical_result.get("total_cost", 0)
        
        # Create simple conversational response
        if total_cost > 0:
            response = f"Et slikt prosjekt koster typisk rundt {total_cost:,.0f} kr i Oslo-området. "
            
            if total_cost < 100000:
                response += "Det er en fin investering som gir mye verdi. "
            elif total_cost < 300000:
                response += "Det er et solid prosjekt som kan transformere hjemmet ditt. "
            else:
                response += "Det er et omfattende prosjekt, men resultatet blir fantastisk. "
            
            response += "Vil du at jeg hjelper deg å finne 2-3 gode entreprenører som kan gi deg tilbud?"
        else:
            response = "For å gi deg et godt prisanslag trenger jeg litt mer informasjon om prosjektet."
        
        return {
            **technical_result,
            "response": response,
            "conversation_stage": "registration_offer",
            "personality_applied": True,
            "next_action": "offer_registration"
        }
    
    def _get_expert_tips(self, project_type: str, cost: float) -> str:
        """Get contextual expert tips based on project type and cost"""
        
        tips = {
            "bad_komplett": "Badrenovering er en av de beste investeringene du kan gjøre - det gir både komfort og verdiøkning. Husk å tenke på ventilasjon og vanntetting fra starten av.",
            
            "kjøkken_detaljert": "Et nytt kjøkken kan øke boligens verdi betydelig. Tenk langsiktig på layout og funksjonalitet - det er ikke noe du vil gjøre om igjen med det første.",
            
            "maling": "Maling er den rimeligste måten å friske opp hjemmet på. Invester i god kvalitet maling og grundig forberedelse - det holder mye lenger.",
            
            "gulvarbeider": "Nye gulv gir en helt ny følelse i hjemmet. Parkett holder lenge og øker verdien, mens laminat er mer budsjettvenlig men like pent.",
            
            "vinduer_dorer": "Nye vinduer og dører kan spare deg for tusenvis i strømregninger årlig, samtidig som de øker komforten betydelig.",
            
            "tak_ytterkledning": "Utvendige arbeider er en investering i hjemmets langvarige beskyttelse. God utførelse her sparer deg for store kostnader senere.",
            
            "default": "Dette er en god investering i hjemmet ditt. Kvalitet og riktig utførelse er nøkkelen til et resultat du blir fornøyd med i mange år fremover."
        }
        
        return tips.get(project_type, tips["default"])
    
    def _create_general_conversational_response(self, query: str) -> Dict[str, Any]:
        """Create a general conversational response for unclear queries"""
        
        query_lower = query.lower()
        
        # Handle questions about the agent's identity
        if any(phrase in query_lower for phrase in ['hvem er du', 'hva er du', 'kan du presentere', 'fortell om deg']):
            response = "Hei! Jeg er househacker-assistenten din 👋 Jeg hjelper deg med oppussingsprosjekter - fra prisanslag til å finne kvalifiserte håndverkere. Jeg kan gi deg kostnadsestimater for bad, kjøkken, maling og mye mer. Har du et oppussingsprosjekt du tenker på?"
        
        # Handle general help questions
        elif any(phrase in query_lower for phrase in ['hjelp', 'kan du hjelpe', 'hva kan du']):
            response = "Jeg kan hjelpe deg med oppussingsprosjekter! 🔨 Jeg gir deg prisanslag, råd om materialer og kan koble deg med kvalifiserte entreprenører. Bare fortell meg hva du skal pusse opp - bad, kjøkken, maling eller noe annet?"
        
        # Handle househacker questions
        elif 'househacker' in query_lower:
            response = "househacker hjelper folk med oppussingsprosjekter! Vi gir prisanslag og kobler deg med kvalitetssikrede entreprenører i Oslo-området. Jeg er din digitale assistent som kan hjelpe deg komme i gang. Hva skal du pusse opp?"
        
        # Default greeting
        else:
            response = "Hei! Jeg er househacker-assistenten din og brenner for oppussing. Har du et prosjekt du tenker på? Jeg kan hjelpe deg med både prisanslag og å finne gode entreprenører. Bare fortell meg hva du har lyst til å gjøre! 😊"
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "conversation_stage": "greeting",
            "personality_applied": True,
            "requires_clarification": False,
            "total_cost": 0
        }
    
    def _get_registration_stage(self, session: Any) -> Optional[RegistrationStage]:
        """Get current registration stage from session"""
        if not session:
            return None
        
        stage_str = getattr(session, 'registration_stage', None)
        if not stage_str:
            return None
        
        try:
            return RegistrationStage(stage_str)
        except ValueError:
            return None
    
    def _wants_to_register(self, query: str) -> bool:
        """Check if user wants to start registration process"""
        query_lower = query.lower()
        
        registration_keywords = [
            'finn entreprenører', 'hjelp til å finne', 'registrere prosjekt',
            'få tilbud', 'kontakt med håndverkere', 'ja, jeg vil', 'befaring',
            'entreprenør', 'tilbud fra', 'kvalitetssikrede'
        ]
        
        return any(keyword in query_lower for keyword in registration_keywords)
    
    def _is_identity_or_general_question(self, query: str) -> bool:
        """Check if this is a question about the agent's identity or general capabilities"""
        query_lower = query.lower()
        
        identity_keywords = [
            'hvem er du', 'hva er du', 'kan du presentere', 'fortell om deg',
            'hjelp', 'kan du hjelpe', 'hva kan du', 'househacker',
            'info', 'informasjon', 'assistenten'
        ]
        
        return any(keyword in query_lower for keyword in identity_keywords)
    
    async def _start_registration_flow(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Start the registration flow"""
        
        # Set registration stage in session
        session = context.get("session") if context else None
        if session:
            session.registration_stage = RegistrationStage.INITIAL_INTEREST.value
            if self.session_memory:
                self.session_memory.db.commit()
        
        # Get first question
        question_data = self.registration_service.get_registration_stage_question(
            RegistrationStage.INITIAL_INTEREST
        )
        
        response = f"""
<div style="background: {self.LIGHT_BG}; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Perfekt! La oss finne de rette entreprenørene til deg! 🎯</h2>
    
    <div style="background: {self.WHITE_BG}; padding: 20px; border-radius: 6px; margin: 16px 0; border-left: 3px solid {self.BRAND_COLOR};">
        <p style="color: #374151; font-size: 16px; margin-bottom: 16px;">
            {question_data['question']}
        </p>
        
        {f'<p style="color: {self.TEXT_GRAY}; font-size: 14px; margin: 0;"><em>{", ".join(question_data["examples"])}</em></p>' if question_data.get("examples") else ''}
    </div>
    
    <div style="background: #f0f9ff; padding: 16px; border-radius: 6px; margin-top: 16px;">
        <p style="color: #0369a1; font-size: 14px; margin: 0;">
            💡 <strong>Husker du:</strong> Dette er helt gratis og uforpliktende. Du bestemmer selv om du vil gå videre med noen av tilbudene!
        </p>
    </div>
</div>
"""
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "conversation_stage": "project_registration",
            "registration_stage": RegistrationStage.INITIAL_INTEREST.value,
            "personality_applied": True,
            "requires_clarification": False,
            "total_cost": 0
        }
    
    async def _handle_registration_flow(
        self, 
        query: str, 
        context: Dict[str, Any], 
        current_stage: RegistrationStage
    ) -> Dict[str, Any]:
        """Handle ongoing registration flow"""
        
        session = context.get("session") if context else None
        
        # Extract registration data from current response
        existing_data = getattr(session, 'registration_data', {}) if session else {}
        updated_data = self.registration_service.extract_registration_data(
            current_stage, query, existing_data
        )
        
        # Store updated data in session
        if session:
            session.registration_data = updated_data
        
        # Determine next stage
        next_stage = self.registration_service.determine_next_stage(
            current_stage, query, updated_data
        )
        
        # Update session with next stage
        if session:
            session.registration_stage = next_stage.value
            if self.session_memory:
                self.session_memory.db.commit()
        
        # Handle completion
        if next_stage == RegistrationStage.COMPLETED:
            return await self._complete_registration(updated_data)
        
        # Get next question
        question_data = self.registration_service.get_registration_stage_question(next_stage)
        
        # Create conversational response for next question
        response = self._create_registration_question_response(question_data, updated_data)
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "conversation_stage": "project_registration",
            "registration_stage": next_stage.value,
            "personality_applied": True,
            "requires_clarification": False,
            "total_cost": 0
        }
    
    def _create_registration_question_response(
        self, 
        question_data: Dict[str, Any], 
        registration_data: Dict[str, Any]
    ) -> str:
        """Create a conversational response for registration questions"""
        
        question = question_data['question']
        options = question_data.get('options', [])
        examples = question_data.get('examples', [])
        explanation = question_data.get('explanation', '')
        
        response = f"""
<div style="background: {self.LIGHT_BG}; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <div style="background: {self.WHITE_BG}; padding: 20px; border-radius: 6px; border-left: 3px solid {self.BRAND_COLOR};">
        <p style="color: #374151; font-size: 16px; margin-bottom: 16px;">
            {question}
        </p>
        
        {self._format_options_or_examples(options, examples)}
        
        {f'<p style="color: {self.TEXT_GRAY}; font-size: 14px; margin-top: 16px;"><em>{explanation}</em></p>' if explanation else ''}
    </div>
</div>
"""
        
        return response
    
    def _format_options_or_examples(self, options: List[str], examples: List[str]) -> str:
        """Format options or examples for registration questions"""
        
        if options:
            options_html = ""
            for option in options:
                options_html += f"""
                <button onclick="askQuestion('{option}')" 
                        style="background: {self.WHITE_BG}; border: 2px solid {self.BRAND_COLOR}; color: {self.BRAND_COLOR}; 
                               padding: 10px 16px; border-radius: 6px; font-size: 14px; cursor: pointer; 
                               margin: 4px; display: block; width: 100%; text-align: left; transition: all 0.2s;"
                        onmouseover="this.style.background='{self.BRAND_COLOR}'; this.style.color='white';"
                        onmouseout="this.style.background='{self.WHITE_BG}'; this.style.color='{self.BRAND_COLOR}';">
                    {option}
                </button>"""
            
            return f'<div style="margin: 16px 0;">{options_html}</div>'
        
        elif examples:
            return f'<p style="color: {self.TEXT_GRAY}; font-size: 14px; margin: 0;"><em>{", ".join(examples)}</em></p>'
        
        return ""
    
    async def _complete_registration(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete the registration process"""
        
        # Validate contact information
        validation = self.registration_service.validate_contact_info(registration_data)
        
        if not validation['is_valid']:
            return await self._handle_invalid_registration(validation)
        
        # Create final confirmation
        confirmation_message = self.registration_service.format_final_confirmation(registration_data)
        
        # TODO: Send to CRM/Google Sheets here
        # await self._send_to_crm(registration_data)
        
        response = f"""
<div style="background: #dcfce7; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #16a34a;">
    <h2 style="color: #15803d; margin-bottom: 16px; font-size: 20px;">Registrering fullført! 🎉</h2>
    
    <div style="background: white; padding: 20px; border-radius: 6px; margin: 16px 0;">
        <pre style="color: #374151; font-family: inherit; white-space: pre-wrap; font-size: 14px; line-height: 1.6; margin: 0;">
{confirmation_message}
        </pre>
    </div>
    
    <div style="background: #f0f9ff; padding: 16px; border-radius: 6px; margin-top: 16px;">
        <p style="color: #0369a1; font-size: 14px; margin: 0;">
            <strong>Hva skjer nå?</strong> Entreprenørene vil ta kontakt innen 1-2 virkedager. 
            Du kan også kontakte oss på <strong>post@househacker.no</strong> hvis du har spørsmål! 😊
        </p>
    </div>
</div>
"""
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "conversation_stage": "registration_completed",
            "registration_stage": RegistrationStage.COMPLETED.value,
            "personality_applied": True,
            "requires_clarification": False,
            "total_cost": 0,
            "registration_completed": True,
            "registration_data": registration_data
        }
    
    async def _handle_invalid_registration(self, validation: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invalid registration data"""
        
        missing_fields = validation['missing_fields']
        
        response = f"""
<div style="background: #fef3cd; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid #f59e0b;">
    <h3 style="color: #92400e; margin-bottom: 16px; font-size: 18px;">Nesten ferdig! 😊</h3>
    
    <p style="color: #374151; font-size: 16px; margin-bottom: 16px;">
        Jeg trenger bare litt mer informasjon for å fullføre registreringen:
    </p>
    
    <ul style="color: #374151; font-size: 14px; margin: 0; padding-left: 20px;">
        {f'<li>Navn</li>' if 'contact_name' in missing_fields else ''}
        {f'<li>Telefonnummer (gyldig format)</li>' if 'contact_phone' in missing_fields else ''}
        {f'<li>E-postadresse (gyldig format)</li>' if 'contact_email' in missing_fields else ''}
    </ul>
    
    <p style="color: {self.TEXT_GRAY}; font-size: 14px; margin-top: 16px;">
        Kan du oppgi den manglende informasjonen?
    </p>
</div>
"""
        
        return {
            "response": response,
            "agent_used": self.agent_name,
            "conversation_stage": "registration_validation",
            "personality_applied": True,
            "requires_clarification": True,
            "total_cost": 0
        }
    
    def can_handle(self, query: str) -> bool:
        """Conversational agent is more liberal - can handle contextual responses and general queries"""
        query_lower = query.lower()
        
        # First check if parent class can handle it (renovation-specific queries)
        if super().can_handle(query):
            return True
        
        # Handle contextual responses that contain size/quality information
        # These might be responses to previous questions
        contextual_indicators = [
            # Size indicators
            r'\d+\s*(?:m²|m2|kvadratmeter|kvm)',
            r'\d+\s*kvadrat',
            
            # Quality indicators  
            'standard', 'kvalitet', 'normal', 'høy', 'enkel', 'premium', 'billig', 'dyr',
            
            # General indicators that this might be a response
            'og', 'med', 'ca', 'cirka', 'rundt',
            
            # Numbers that could be quantities or sizes
            r'\d+\s*(?:stk|vindu|vinduer|dør|dører|rom)'
        ]
        
        for indicator in contextual_indicators:
            if isinstance(indicator, str):
                if indicator in query_lower:
                    return True
            else:
                # Regex pattern
                import re
                if re.search(indicator, query_lower):
                    return True
        
        # Handle questions about the agent itself
        agent_questions = [
            'hvem er du', 'hva er', 'kan du', 'hjelpe', 'hjelp',
            'househacker', 'info', 'informasjon'
        ]
        
        if any(phrase in query_lower for phrase in agent_questions):
            return True
        
        # Handle very short responses that might be contextual
        words = query_lower.strip().split()
        if len(words) <= 5 and any(char.isdigit() for char in query_lower):
            return True
        
        return False