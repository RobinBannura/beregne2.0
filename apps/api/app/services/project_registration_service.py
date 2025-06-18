from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class RegistrationStage(Enum):
    INITIAL_INTEREST = "initial_interest"
    PROJECT_TYPE = "project_type"
    CUSTOMER_TYPE = "customer_type"
    LOCATION = "location"
    TIMELINE = "timeline"
    BUDGET = "budget"
    ADDITIONAL_INFO = "additional_info"
    BEFARING_PREFERENCE = "befaring_preference"
    CONTACT_NAME = "contact_name"
    CONTACT_PHONE = "contact_phone"
    CONTACT_EMAIL = "contact_email"
    FINAL_CONFIRMATION = "final_confirmation"
    COMPLETED = "completed"

class ProjectRegistrationService:
    """
    Handles seamless project registration flow with conversational approach
    """
    
    def __init__(self):
        self.registration_questions = {
            RegistrationStage.INITIAL_INTEREST: {
                "question": "Flott! Før vi finner entreprenører til deg, kan du fortelle meg litt kort om prosjektet?",
                "examples": ["f.eks. 'totalrenovering av bad' eller 'male hele leiligheten'"],
                "field": "project_description"
            },
            
            RegistrationStage.CUSTOMER_TYPE: {
                "question": "Er dette for deg som privatperson, eller representerer du en bedrift/borettslag?",
                "options": ["Privatperson", "Næringsdrivende", "Borettslag/Sameie"],
                "field": "customer_type"
            },
            
            RegistrationStage.LOCATION: {
                "question": "Hvor skal prosjektet utføres? Du kan oppgi adresse eller bare postnummer hvis du foretrekker det.",
                "examples": ["f.eks. 'Oslo sentrum' eller '0150'"],
                "field": "location"
            },
            
            RegistrationStage.TIMELINE: {
                "question": "Når ønsker du å starte prosjektet?",
                "options": ["Så snart som mulig", "Innen 1-2 måneder", "Til våren/sommeren", "Jeg er fleksibel"],
                "field": "preferred_timeline"
            },
            
            RegistrationStage.BUDGET: {
                "question": "Har du tenkt på et omtrentlig budsjett? (Dette er valgfritt, men hjelper oss å foreslå riktig løsning)",
                "examples": ["f.eks. 'rundt 200.000' eller 'vet ikke ennå'"],
                "field": "estimated_budget"
            },
            
            RegistrationStage.ADDITIONAL_INFO: {
                "question": "Er det noe spesielt du vil legge til eller spesifikke ønsker du har?",
                "examples": ["f.eks. spesielle materialer, tilgjengelighet, eller andre preferanser"],
                "field": "additional_requirements"
            },
            
            RegistrationStage.BEFARING_PREFERENCE: {
                "question": "Ønsker du at househacker gjennomfører en befaring først for å gi deg enda mer presise tilbud, eller føler du deg klar for å motta tilbud direkte?",
                "options": ["Befaring først (anbefales for større prosjekter)", "Motta tilbud direkte"],
                "field": "befaring_preference"
            },
            
            RegistrationStage.CONTACT_NAME: {
                "question": "Flott! Hva heter du?",
                "field": "contact_name"
            },
            
            RegistrationStage.CONTACT_PHONE: {
                "question": "Kan du oppgi telefonnummeret ditt? Entreprenørene tar gjerne kontakt på telefon.",
                "field": "contact_phone"
            },
            
            RegistrationStage.CONTACT_EMAIL: {
                "question": "Og til slutt - hva er e-postadressen din?",
                "field": "contact_email"
            },
            
            RegistrationStage.FINAL_CONFIRMATION: {
                "question": "Perfekt! Ønsker du at vi sender prosjektet ditt videre til inntil 3 kvalitetssikrede entreprenører i ditt område?",
                "explanation": "Dette er helt gratis og uforpliktende. Du bestemmer selv om du vil gå videre med noen av tilbudene.",
                "field": "final_consent"
            }
        }
    
    def get_registration_stage_question(
        self, 
        stage: RegistrationStage, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Get the appropriate question for current registration stage"""
        
        question_data = self.registration_questions.get(stage)
        if not question_data:
            return {"error": "Invalid registration stage"}
        
        return {
            "stage": stage.value,
            "question": question_data["question"],
            "options": question_data.get("options", []),
            "examples": question_data.get("examples", []),
            "explanation": question_data.get("explanation", ""),
            "field": question_data["field"]
        }
    
    def determine_next_stage(
        self, 
        current_stage: Optional[RegistrationStage], 
        user_response: str,
        registration_data: Dict[str, Any]
    ) -> RegistrationStage:
        """Determine the next registration stage based on current state and response"""
        
        # If no current stage, start with initial interest
        if not current_stage:
            return RegistrationStage.INITIAL_INTEREST
        
        # Define stage progression
        stage_order = [
            RegistrationStage.INITIAL_INTEREST,
            RegistrationStage.CUSTOMER_TYPE,
            RegistrationStage.LOCATION,
            RegistrationStage.TIMELINE,
            RegistrationStage.BUDGET,
            RegistrationStage.ADDITIONAL_INFO,
            RegistrationStage.BEFARING_PREFERENCE,
            RegistrationStage.CONTACT_NAME,
            RegistrationStage.CONTACT_PHONE,
            RegistrationStage.CONTACT_EMAIL,
            RegistrationStage.FINAL_CONFIRMATION,
            RegistrationStage.COMPLETED
        ]
        
        try:
            current_index = stage_order.index(current_stage)
            
            # If we're at the final confirmation and user said yes, complete
            if (current_stage == RegistrationStage.FINAL_CONFIRMATION and 
                any(word in user_response.lower() for word in ['ja', 'yes', 'ok', 'greit', 'send'])):
                return RegistrationStage.COMPLETED
            
            # Move to next stage if not at the end
            if current_index < len(stage_order) - 1:
                return stage_order[current_index + 1]
            
            return RegistrationStage.COMPLETED
            
        except ValueError:
            # If current stage not found, start over
            return RegistrationStage.INITIAL_INTEREST
    
    def extract_registration_data(
        self, 
        stage: RegistrationStage, 
        user_response: str,
        existing_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Extract and structure registration data from user response"""
        
        if not existing_data:
            existing_data = {}
        
        question_data = self.registration_questions.get(stage)
        if not question_data:
            return existing_data
        
        field_name = question_data["field"]
        
        # Clean and store the response
        cleaned_response = user_response.strip()
        
        # Special handling for specific fields
        if field_name == "customer_type":
            if any(word in cleaned_response.lower() for word in ['privatperson', 'privat']):
                cleaned_response = "Privatperson"
            elif any(word in cleaned_response.lower() for word in ['bedrift', 'næring', 'firma']):
                cleaned_response = "Næringsdrivende"
            elif any(word in cleaned_response.lower() for word in ['borettslag', 'sameie']):
                cleaned_response = "Borettslag/Sameie"
        
        elif field_name == "befaring_preference":
            if any(word in cleaned_response.lower() for word in ['befaring', 'besiktigelse']):
                cleaned_response = "Befaring først"
            else:
                cleaned_response = "Direkte tilbud"
        
        existing_data[field_name] = cleaned_response
        existing_data["last_updated"] = datetime.now().isoformat()
        
        return existing_data
    
    def create_project_summary(self, registration_data: Dict[str, Any]) -> str:
        """Create a professional project summary for CRM/email"""
        
        project_desc = registration_data.get("project_description", "Oppussingsprosjekt")
        location = registration_data.get("location", "")
        timeline = registration_data.get("preferred_timeline", "")
        additional = registration_data.get("additional_requirements", "")
        
        summary_parts = [project_desc]
        
        if location:
            summary_parts.append(f"Lokasjon: {location}")
        
        if timeline and timeline != "Jeg er fleksibel":
            summary_parts.append(f"Ønsket oppstart: {timeline}")
        
        if additional and additional.lower() not in ['nei', 'ikke noe', 'ingenting']:
            summary_parts.append(f"Spesielle ønsker: {additional}")
        
        return ". ".join(summary_parts) + "."
    
    def validate_contact_info(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required contact information is present"""
        
        required_fields = ["contact_name", "contact_phone", "contact_email"]
        missing_fields = []
        
        for field in required_fields:
            if not registration_data.get(field) or len(registration_data.get(field, "").strip()) < 2:
                missing_fields.append(field)
        
        # Validate email format
        email = registration_data.get("contact_email", "")
        if email and "@" not in email:
            missing_fields.append("contact_email")
        
        # Validate phone (basic check)
        phone = registration_data.get("contact_phone", "")
        if phone and len(phone.replace(" ", "").replace("+", "")) < 8:
            missing_fields.append("contact_phone")
        
        return {
            "is_valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "data": registration_data
        }
    
    def format_final_confirmation(self, registration_data: Dict[str, Any]) -> str:
        """Format a nice confirmation message with project summary"""
        
        project_summary = self.create_project_summary(registration_data)
        name = registration_data.get("contact_name", "")
        phone = registration_data.get("contact_phone", "")
        email = registration_data.get("contact_email", "")
        
        return f"""
Takk, {name}! 🎉

Her er en oppsummering av prosjektet ditt:
📋 {project_summary}

Kontaktinfo:
📞 {phone}
📧 {email}

Vi sender dette videre til kvalitetssikrede entreprenører i ditt område. De vil ta kontakt med deg innen 1-2 virkedager.

Alle tilbud er helt gratis og uforpliktende. Du bestemmer selv om du vil gå videre! 😊
"""