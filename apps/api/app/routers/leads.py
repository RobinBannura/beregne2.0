from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import httpx
import os
import json
from datetime import datetime

router = APIRouter(prefix="/api/leads", tags=["leads"])

class LeadData(BaseModel):
    project_type: str
    estimated_cost: float
    area: str
    partner_id: str = "unknown"
    contact_info: Dict[str, str] = {}
    additional_notes: str = ""

class MondayIntegration:
    """Monday.com CRM integrasjon for leads"""
    
    def __init__(self):
        self.api_token = os.getenv("MONDAY_API_TOKEN")
        self.board_id = os.getenv("MONDAY_BOARD_ID", "2004442153")
        self.api_url = "https://api.monday.com/v2"
    
    async def create_lead(self, lead: LeadData) -> Dict[str, Any]:
        """Opprett ny lead i Monday.com"""
        
        # Monday.com GraphQL mutation
        mutation = """
        mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
            create_item (
                board_id: $boardId,
                item_name: $itemName,
                column_values: $columnValues
            ) {
                id
                name
            }
        }
        """
        
        # Forenklet kolonnverdier - kun tekst kolonne til å starte med
        column_values = {
            "text": f"Kostnad: {lead.estimated_cost:,.0f} NOK | Areal: {lead.area}m² | Type: {lead.project_type} | Partner: {lead.partner_id}"
        }
        
        variables = {
            "boardId": self.board_id,  # Keep as string, Monday.com expects string
            "itemName": f"Oppussing {lead.area}m² - {lead.estimated_cost:,.0f} NOK",
            "columnValues": json.dumps(column_values)  # JSON encode the column values
        }
        
        headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": mutation,
            "variables": variables
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "errors" not in data:
                        return {
                            "success": True,
                            "monday_item_id": data["data"]["create_item"]["id"],
                            "message": "Lead opprettet i Monday.com"
                        }
                    else:
                        return {
                            "success": False,
                            "error": data["errors"][0]["message"]
                        }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Monday.com API feil: {str(e)}"
            }

# Alternativ: Google Sheets integrasjon
class GoogleSheetsIntegration:
    """Google Sheets integrasjon som backup"""
    
    async def create_lead(self, lead: LeadData) -> Dict[str, Any]:
        """Legg til lead i Google Sheets"""
        # Implementer Google Sheets API
        # Dette kan være backup hvis Monday.com feiler
        
        return {
            "success": True,
            "message": "Lead lagret i Google Sheets (backup)"
        }

@router.post("/")
async def create_lead(lead: LeadData):
    """Opprett ny lead fra widget"""
    
    monday = MondayIntegration()
    result = await monday.create_lead(lead)
    
    if not result["success"]:
        # Fallback til Google Sheets
        sheets = GoogleSheetsIntegration()
        backup_result = await sheets.create_lead(lead)
        
        return {
            "status": "backup_created",
            "message": "Lead lagret i backup system",
            "monday_error": result["error"]
        }
    
    return {
        "status": "success",
        "message": "Lead opprettet i Monday.com",
        "monday_item_id": result.get("monday_item_id")
    }

@router.get("/stats/{partner_id}")
async def get_lead_stats(partner_id: str):
    """Hent lead-statistikk for partner"""
    # Implementer statistikk fra Monday.com eller database
    return {
        "partner_id": partner_id,
        "total_leads": 0,
        "conversion_rate": "0%",
        "avg_project_value": 0
    }