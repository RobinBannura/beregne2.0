from typing import Dict, Any, List, Optional
import re
from datetime import datetime
from .enhanced_renovation_agent import EnhancedRenovationAgent
from ..services.project_registration_service import ProjectRegistrationService, RegistrationStage

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
        
        # Initialize registration service
        self.registration_service = ProjectRegistrationService()
        
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
        """Process query with conversational approach"""
        
        # Check if we're in registration mode
        session = context.get("session") if context else None
        registration_stage = self._get_registration_stage(session)
        
        if registration_stage and registration_stage != RegistrationStage.COMPLETED:
            return await self._handle_registration_flow(query, context, registration_stage)
        
        # Check if user wants to start registration
        if self._wants_to_register(query):
            return await self._start_registration_flow(query, context)
        
        # First, get the technical analysis and pricing from parent class
        technical_result = await super().process(query, context)
        
        # Then wrap it in conversational response
        conversational_result = await self._create_conversational_response(
            query, technical_result, context
        )
        
        return conversational_result
    
    async def _create_conversational_response(
        self, 
        query: str, 
        technical_result: Dict[str, Any], 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a human-like conversational response"""
        
        # Analyze conversation stage
        session = context.get("session") if context else None
        conversation_stage = self._determine_conversation_stage(query, session)
        
        # Get project type for contextual advice
        project_type = technical_result.get("calculation_details", {}).get("project_type", "")
        
        if technical_result.get("requires_clarification"):
            return self._wrap_clarification_conversationally(
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
    
    def _wrap_clarification_conversationally(
        self, 
        technical_result: Dict[str, Any], 
        query: str, 
        project_type: str
    ) -> Dict[str, Any]:
        """Wrap technical clarification in conversational tone"""
        
        # Get the original technical response
        original_response = technical_result.get("response", "")
        
        # Add conversational introduction
        intro_phrases = [
            "Det høres ut som et spennende prosjekt! 😊",
            "Flott at du tenker på oppussing!",
            "Jeg skjønner hva du er ute etter!",
            "Det er et populært prosjekt akkurat nå!"
        ]
        
        # Choose intro based on query
        if "bad" in query.lower():
            intro = "Badrenovering er alltid en god investering! 🛁"
        elif "kjøkken" in query.lower():
            intro = "Kjøkken er hjertet i hjemmet - smart å oppgradere! 👨‍🍳"
        elif "dør" in query.lower():
            intro = "Nye dører kan virkelig friske opp hjemmet! 🚪"
        else:
            intro = intro_phrases[0]
        
        # Add seasonal context if relevant
        seasonal_advice = self._get_seasonal_context(project_type)
        
        # Rebuild response with conversational wrapper
        conversational_response = f"""
<div style="background: {self.LIGHT_BG}; padding: 24px; border-radius: 8px; margin: 16px 0; border-left: 3px solid {self.BRAND_COLOR};">
    <div style="margin-bottom: 16px;">
        <p style="color: #374151; font-size: 16px; margin-bottom: 8px;">
            {intro}
        </p>
        {f'<p style="color: {self.TEXT_GRAY}; font-size: 14px; margin-bottom: 16px;">{seasonal_advice}</p>' if seasonal_advice else ''}
    </div>
    
    {original_response.replace('<div style="background: #f9fafb;', '<div style="background: #ffffff;')}
    
    <div style="background: #f8fafc; padding: 16px; border-radius: 6px; margin-top: 16px; border-left: 2px solid {self.BRAND_COLOR};">
        <p style="color: #374151; font-size: 14px; margin: 0;">
            💡 <strong>Tips:</strong> Når vi har fått avklart detaljene kan jeg hjelpe deg med å finne kvalitetssikrede entreprenører i ditt område!
        </p>
    </div>
</div>
"""
        
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
        original_response = technical_result.get("response", "")
        
        # Conversational introduction based on price range
        if total_cost < 50000:
            price_context = "Det er et rimelig til middels prosjekt"
        elif total_cost < 150000:
            price_context = "Det er et solid prosjekt med god verdi"
        elif total_cost < 300000:
            price_context = "Det er et større prosjekt som kan gi mye verdi til hjemmet"
        else:
            price_context = "Det er et omfattende prosjekt som virkelig kan transformere hjemmet ditt"
        
        # Add expertise and tips
        expert_tips = self._get_expert_tips(project_type, total_cost)
        seasonal_advice = self._get_seasonal_context(project_type)
        
        # Build conversational response
        conversational_response = f"""
<div style="background: {self.LIGHT_BG}; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <div style="margin-bottom: 20px;">
        <p style="color: #374151; font-size: 16px; margin-bottom: 12px;">
            Her er et realistisk prisestimat basert på dagens markedspriser i Oslo/Viken-området: 📊
        </p>
    </div>
    
    {original_response}
    
    <div style="background: {self.WHITE_BG}; padding: 20px; border-radius: 6px; margin: 16px 0; border-left: 3px solid {self.BRAND_COLOR};">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">💡 Mine råd som fagperson:</h3>
        
        <p style="color: #374151; font-size: 14px; margin-bottom: 12px;">
            <strong>{price_context}.</strong> {expert_tips}
        </p>
        
        {f'<p style="color: {self.TEXT_GRAY}; font-size: 14px; margin-bottom: 12px;">{seasonal_advice}</p>' if seasonal_advice else ''}
        
        <p style="color: #374151; font-size: 14px; margin: 0;">
            Prisene kan variere ±15-20% avhengig av kvalitet, tilgjengelighet og spesielle ønsker. 
            Vil du at jeg hjelper deg med å finne 2-3 kvalitetssikrede entreprenører som kan gi deg konkrete tilbud? 🤝
        </p>
    </div>
    
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="askQuestion('Ja, jeg vil gjerne ha hjelp til å finne entreprenører')" 
                style="background: {self.BRAND_COLOR}; color: white; padding: 12px 24px; border: none; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; margin-right: 8px;">
            Finn entreprenører
        </button>
        
        <button onclick="askQuestion('Kan du fortelle mer om prosessen?')" 
                style="background: transparent; color: {self.BRAND_COLOR}; border: 1px solid {self.BRAND_COLOR}; padding: 11px 23px; border-radius: 6px; font-size: 14px; cursor: pointer;">
            Fortell mer
        </button>
    </div>
</div>
"""
        
        return {
            **technical_result,
            "response": conversational_response,
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
        
        return {
            "response": f"""
<div style="background: {self.LIGHT_BG}; padding: 24px; border-radius: 8px; margin: 16px 0;">
    <h2 style="color: #111827; margin-bottom: 16px; font-size: 20px;">Hei! Hyggelig å høre fra deg! 👋</h2>
    
    <p style="color: #374151; font-size: 16px; margin-bottom: 16px;">
        Jeg er din househacker-assistent og brenner for å hjelpe folk med oppussingsprosjekter. 
        Med over 15 års erfaring fra byggebransjen kan jeg hjelpe deg med både prisanslag og å finne 
        riktige entreprenører.
    </p>
    
    <div style="background: {self.WHITE_BG}; padding: 20px; border-radius: 6px; margin: 16px 0;">
        <h3 style="color: #374151; margin-bottom: 12px; font-size: 16px;">Hva tenker du på? 🤔</h3>
        <p style="color: #374151; font-size: 14px; margin-bottom: 16px;">
            Jeg kan hjelpe deg med:
        </p>
        <ul style="color: #374151; font-size: 14px; margin: 0; padding-left: 20px;">
            <li>Realistiske kostnadsestimater</li>
            <li>Faglige råd og tips</li>
            <li>Kobling med kvalitetssikrede entreprenører</li>
            <li>Veiledning gjennom hele prosessen</li>
        </ul>
    </div>
    
    <p style="color: {self.TEXT_GRAY}; font-size: 14px; margin-top: 16px;">
        Bare fortell meg hva du har lyst til å gjøre - jeg gir deg en ærlig vurdering! 😊
    </p>
</div>
""",
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