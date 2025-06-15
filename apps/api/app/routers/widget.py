from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.partner import Partner

router = APIRouter(prefix="/widget", tags=["widget"])

@router.get("/{partner_id}", response_class=HTMLResponse)
async def get_widget_html(partner_id: str, db: Session = Depends(get_db)):
    """Generer HTML for embeddbar widget for spesifikk partner"""
    
    # Hent partner konfigurasjon
    partner = db.query(Partner).filter(
        Partner.partner_id == partner_id,
        Partner.is_active == True
    ).first()
    
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    # Generer widget HTML
    widget_html = f"""
<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{partner.brand_name} - Oppussingsrådgiver</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: {partner.widget_theme == 'dark' and '#1a1a1a' or '#ffffff'};
            color: {partner.widget_theme == 'dark' and '#ffffff' or '#1a1a1a'};
            padding: 20px;
        }}
        
        .widget-container {{
            max-width: 600px;
            margin: 0 auto;
            background: {partner.widget_theme == 'dark' and '#2a2a2a' or '#ffffff'};
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .widget-header {{
            background: {partner.brand_color};
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .widget-header h1 {{
            font-size: 24px;
            margin-bottom: 8px;
        }}
        
        .widget-header p {{
            opacity: 0.9;
            font-size: 16px;
        }}
        
        .chat-container {{
            padding: 20px;
            min-height: 400px;
            display: flex;
            flex-direction: column;
        }}
        
        .messages {{
            flex: 1;
            margin-bottom: 20px;
            max-height: 300px;
            overflow-y: auto;
        }}
        
        .message {{
            margin-bottom: 16px;
            padding: 12px 16px;
            border-radius: 8px;
            max-width: 80%;
        }}
        
        .message.user {{
            background: {partner.brand_color};
            color: white;
            margin-left: auto;
        }}
        
        .message.bot {{
            background: {partner.widget_theme == 'dark' and '#3a3a3a' or '#f3f4f6'};
            color: {partner.widget_theme == 'dark' and '#ffffff' or '#1a1a1a'};
        }}
        
        .input-container {{
            display: flex;
            gap: 12px;
        }}
        
        .input-container input {{
            flex: 1;
            padding: 12px 16px;
            border: 2px solid {partner.widget_theme == 'dark' and '#3a3a3a' or '#e5e7eb'};
            border-radius: 8px;
            background: {partner.widget_theme == 'dark' and '#2a2a2a' or '#ffffff'};
            color: {partner.widget_theme == 'dark' and '#ffffff' or '#1a1a1a'};
            font-size: 16px;
        }}
        
        .input-container button {{
            padding: 12px 24px;
            background: {partner.brand_color};
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .input-container button:hover {{
            opacity: 0.9;
        }}
        
        .input-container button:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
        }}
        
        .examples {{
            margin-top: 16px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .example {{
            padding: 8px 12px;
            background: {partner.widget_theme == 'dark' and '#3a3a3a' or '#f3f4f6'};
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            border: 1px solid transparent;
        }}
        
        .example:hover {{
            border-color: {partner.brand_color};
        }}
        
        .branding {{
            text-align: center;
            padding: 12px;
            font-size: 12px;
            opacity: 0.6;
            border-top: 1px solid {partner.widget_theme == 'dark' and '#3a3a3a' or '#e5e7eb'};
        }}
        
        .loading {{
            display: none;
            text-align: center;
            padding: 20px;
        }}
        
        .loading.show {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="widget-container">
        <div class="widget-header">
            <h1>{partner.brand_name}</h1>
            <p>{partner.agent_display_name}</p>
        </div>
        
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="message bot">
                    {partner.welcome_message}
                </div>
            </div>
            
            <div class="examples">
                <div class="example" onclick="askQuestion('Hvor mye maling trenger jeg til 25 m²?')">
                    Maling til 25 m²
                </div>
                <div class="example" onclick="askQuestion('Komplett badrenovering 8 m²')">
                    Badrenovering 8 m²
                </div>
                <div class="example" onclick="askQuestion('Hvor mye fliser til 15 m²?')">
                    Fliser til 15 m²
                </div>
            </div>
            
            <div class="input-container">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="Spør om oppussing og materialer..."
                    onkeypress="handleKeyPress(event)"
                >
                <button onclick="sendMessage()" id="sendButton">Send</button>
            </div>
            
            <div class="loading" id="loading">
                <p>⏳ Beregner...</p>
            </div>
        </div>
        
        {"" if not partner.show_branding else f'''
        <div class="branding">
            Drevet av <a href="https://beregne.no" target="_blank" style="color: {partner.brand_color};">Beregne.no</a>
        </div>
        '''}
    </div>

    <script>
        const API_URL = window.location.origin;
        const PARTNER_ID = '{partner_id}';
        
        function addMessage(message, isUser = false) {{
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{isUser ? 'user' : 'bot'}}`;
            messageDiv.innerHTML = message;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }}
        
        function showLoading(show = true) {{
            const loading = document.getElementById('loading');
            const sendButton = document.getElementById('sendButton');
            loading.className = show ? 'loading show' : 'loading';
            sendButton.disabled = show;
        }}
        
        async function sendMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, true);
            input.value = '';
            
            // Show loading
            showLoading(true);
            
            try {{
                const response = await fetch(`${{API_URL}}/api/chat`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        message: message,
                        partner_id: PARTNER_ID
                    }})
                }});
                
                const data = await response.json();
                
                if (response.ok) {{
                    addMessage(data.response);
                }} else {{
                    addMessage('Beklager, det oppstod en feil. Prøv igjen.');
                }}
            }} catch (error) {{
                console.error('Error:', error);
                addMessage('Beklager, det oppstod en feil. Prøv igjen.');
            }} finally {{
                showLoading(false);
            }}
        }}
        
        function askQuestion(question) {{
            document.getElementById('messageInput').value = question;
            sendMessage();
        }}
        
        function handleKeyPress(event) {{
            if (event.key === 'Enter') {{
                sendMessage();
            }}
        }}
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=widget_html)

@router.get("/{partner_id}/embed.js")
async def get_widget_js(partner_id: str, request: Request, db: Session = Depends(get_db)):
    """JavaScript for embedding widget in iframe"""
    
    partner = db.query(Partner).filter(
        Partner.partner_id == partner_id,
        Partner.is_active == True
    ).first()
    
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    base_url = str(request.base_url).rstrip('/')
    
    js_code = f"""
(function() {{
    const PARTNER_ID = '{partner_id}';
    const BASE_URL = '{base_url}';
    const POSITION = '{partner.widget_position}';
    
    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.src = `${{BASE_URL}}/widget/${{PARTNER_ID}}`;
    iframe.style.cssText = `
        position: fixed;
        bottom: 20px;
        ${{POSITION.includes('right') ? 'right: 20px;' : 'left: 20px;'}}
        width: 400px;
        height: 600px;
        border: none;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        z-index: 999999;
        background: white;
    `;
    
    // Add to page
    document.body.appendChild(iframe);
    
    console.log('{partner.brand_name} widget loaded');
}})();
    """
    
    return Response(content=js_code, media_type="application/javascript")