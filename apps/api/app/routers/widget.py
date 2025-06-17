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
            background: linear-gradient(135deg, {partner.brand_color} 0%, #c53030 100%);
            color: white;
            padding: 24px 20px;
            text-align: center;
            position: relative;
        }}
        
        .widget-header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
        }}
        
        .widget-header h1 {{
            font-size: 22px;
            margin-bottom: 8px;
            font-weight: 700;
            position: relative;
            z-index: 1;
        }}
        
        .widget-header p {{
            opacity: 0.95;
            font-size: 15px;
            position: relative;
            z-index: 1;
            margin-bottom: 12px;
        }}
        
        .househacker-badge {{
            display: inline-flex;
            align-items: center;
            background: rgba(255,255,255,0.2);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            position: relative;
            z-index: 1;
        }}
        
        .househacker-badge::before {{
            content: '🏠';
            margin-right: 6px;
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
            background: {partner.widget_theme == 'dark' and '#3a3a3a' or '#f8fafc'};
            color: {partner.widget_theme == 'dark' and '#ffffff' or '#1a1a1a'};
            border-left: 4px solid {partner.brand_color};
        }}
        
        .message.bot h2, .message.bot h3, .message.bot h4 {{
            color: {partner.brand_color};
            margin-top: 1em;
            margin-bottom: 0.5em;
        }}
        
        .message.bot table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
        }}
        
        .message.bot th {{
            background: {partner.brand_color};
            color: white;
        }}
        
        .message.bot button {{
            background: {partner.brand_color};
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .message.bot button:hover {{
            background: #c53030;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
            padding: 16px;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            border-top: 1px solid {partner.widget_theme == 'dark' and '#3a3a3a' or '#e5e7eb'};
        }}
        
        .branding-content {{
            font-size: 13px;
            color: #64748b;
            margin-bottom: 10px;
        }}
        
        .cta-button {{
            display: inline-flex;
            align-items: center;
            background: {partner.brand_color};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .cta-button:hover {{
            background: #c53030;
            transform: translateY(-1px);
        }}
        
        .cta-button::before {{
            content: '🏠';
            margin-right: 6px;
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
            <h1>💰 Oppussings&shy;kalkulator</h1>
            <p>Få realistiske kostnadsestimater for ditt oppussingsprosjekt</p>
            <div class="househacker-badge">Powered by househacker</div>
        </div>
        
        <div class="chat-container">
            <div class="messages" id="messages">
                <div class="message bot">
                    👋 Hei! Jeg hjelper deg med kostnadsestimater for oppussingsprosjekter i Oslo-området. 
                    <br><br>
                    Få realistiske priser på materialer, arbeid og totalkostnader - og la househacker hjelpe deg med gjennomføringen! 🏠
                </div>
            </div>
            
            <div class="examples">
                <div class="example" onclick="askQuestion('Jeg skal totalrenovere badet - 15 m²')">
                    🚿 Badrenovering 15 m²
                </div>
                <div class="example" onclick="askQuestion('Komplett kjøkken Oslo - 20 m²')">
                    🍳 Kjøkken 20 m²
                </div>
                <div class="example" onclick="askQuestion('Hvor mye maling trenger jeg til 40 m²?')">
                    🎨 Maling 40 m²
                </div>
                <div class="example" onclick="askQuestion('Jeg skal pusse opp!')">
                    🏠 Generell oppussing
                </div>
            </div>
            
            <div class="input-container">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="F.eks: Jeg skal pusse opp badet - 12 m²"
                    onkeypress="handleKeyPress(event)"
                >
                <button onclick="sendMessage()" id="sendButton">Send</button>
            </div>
            
            <div class="loading" id="loading">
                <p>⏳ Beregner...</p>
            </div>
        </div>
        
        <div class="branding">
            <div class="branding-content">
                Trenger du hjelp med oppussingen? househacker kobler deg med kvalifiserte håndverkere.
            </div>
            <a href="https://househacker.no" target="_blank" class="cta-button">
                Besøk househacker.no
            </a>
        </div>
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