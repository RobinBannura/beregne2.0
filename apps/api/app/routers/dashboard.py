from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.partner import Partner

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/", response_class=HTMLResponse)
async def partner_dashboard(request: Request, db: Session = Depends(get_db)):
    """Partner dashboard for managing agents and embedding"""
    
    # Get all partners
    partners = db.query(Partner).filter(Partner.is_active == True).all()
    
    # Generate partner cards
    partner_cards = ""
    for partner in partners:
        agent_badges = "".join([f'<span class="agent-badge">{agent}</span>' for agent in partner.enabled_agents or []])
        
        partner_cards += f"""
        <div class="partner-card" data-partner-id="{partner.partner_id}">
            <div class="partner-header" style="background: {partner.brand_color};">
                <h3>{partner.brand_name}</h3>
                <div class="partner-status">
                    <span class="status-dot active"></span>
                    Aktiv
                </div>
            </div>
            
            <div class="partner-body">
                <div class="partner-info">
                    <p><strong>Partner ID:</strong> {partner.partner_id}</p>
                    <p><strong>Domene:</strong> {partner.domain or 'Ikke angitt'}</p>
                    <p><strong>Agenter:</strong> {agent_badges}</p>
                    <p><strong>Tema:</strong> {partner.widget_theme}</p>
                    <p><strong>Posisjon:</strong> {partner.widget_position}</p>
                </div>
                
                <div class="partner-actions">
                    <button onclick="previewWidget('{partner.partner_id}')" class="btn btn-primary">
                        👁️ Forhåndsvis
                    </button>
                    <button onclick="showEmbedCode('{partner.partner_id}')" class="btn btn-secondary">
                        📋 Embed-kode
                    </button>
                    <button onclick="editPartner('{partner.partner_id}')" class="btn btn-outline">
                        ✏️ Rediger
                    </button>
                </div>
            </div>
        </div>
        """
    
    dashboard_html = f"""
<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Partner Dashboard - Beregne 2.0</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2563eb, #3b82f6);
            color: white;
            padding: 2rem 0;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .dashboard-nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }}
        
        .btn {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-block;
        }}
        
        .btn-primary {{
            background: #2563eb;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #1d4ed8;
        }}
        
        .btn-secondary {{
            background: #64748b;
            color: white;
        }}
        
        .btn-secondary:hover {{
            background: #475569;
        }}
        
        .btn-outline {{
            background: transparent;
            color: #2563eb;
            border: 2px solid #2563eb;
        }}
        
        .btn-outline:hover {{
            background: #2563eb;
            color: white;
        }}
        
        .btn-success {{
            background: #059669;
            color: white;
        }}
        
        .btn-success:hover {{
            background: #047857;
        }}
        
        .partners-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .partner-card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .partner-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        }}
        
        .partner-header {{
            padding: 1.5rem;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .partner-header h3 {{
            font-size: 1.5rem;
            font-weight: 700;
        }}
        
        .partner-status {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }}
        
        .status-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
        }}
        
        .partner-body {{
            padding: 1.5rem;
        }}
        
        .partner-info {{
            margin-bottom: 1.5rem;
        }}
        
        .partner-info p {{
            margin-bottom: 0.5rem;
            font-size: 0.95rem;
        }}
        
        .agent-badge {{
            display: inline-block;
            background: #e0e7ff;
            color: #3730a3;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }}
        
        .partner-actions {{
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}
        
        .partner-actions .btn {{
            flex: 1;
            min-width: 120px;
            text-align: center;
            font-size: 0.9rem;
            padding: 0.6rem 1rem;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #2563eb;
            display: block;
        }}
        
        .stat-label {{
            color: #64748b;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }}
        
        .modal.show {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .modal-content {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }}
        
        .modal-header h3 {{
            font-size: 1.5rem;
            color: #1e293b;
        }}
        
        .close-btn {{
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #64748b;
        }}
        
        .form-group {{
            margin-bottom: 1rem;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #374151;
        }}
        
        .form-group input,
        .form-group select,
        .form-group textarea {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
        }}
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {{
            outline: none;
            border-color: #2563eb;
        }}
        
        .code-block {{
            background: #1e293b;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9rem;
            overflow-x: auto;
            margin: 1rem 0;
        }}
        
        .copy-btn {{
            background: #059669;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}
        
        .copy-btn:hover {{
            background: #047857;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 3rem;
            color: #64748b;
        }}
        
        .empty-state h3 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        @media (max-width: 768px) {{
            .partners-grid {{
                grid-template-columns: 1fr;
            }}
            
            .partner-actions {{
                flex-direction: column;
            }}
            
            .partner-actions .btn {{
                flex: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤝 Partner Dashboard</h1>
        <p>Administrer AI-agenter og widgets for dine partnere</p>
    </div>
    
    <div class="container">
        <div class="dashboard-nav">
            <h2>Oversikt</h2>
            <button onclick="showNewPartnerForm()" class="btn btn-success">
                ➕ Ny Partner
            </button>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{len(partners)}</span>
                <div class="stat-label">Aktive Partnere</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">1</span>
                <div class="stat-label">Tilgjengelige Agenter</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">{sum(len(p.enabled_agents or []) for p in partners)}</span>
                <div class="stat-label">Agent-konfigurasjoner</div>
            </div>
        </div>
        
        <div class="partners-grid">
            {partner_cards if partner_cards else '''
            <div class="empty-state">
                <h3>Ingen partnere ennå</h3>
                <p>Klikk "Ny Partner" for å komme i gang</p>
            </div>
            '''}
        </div>
    </div>
    
    <!-- Preview Modal -->
    <div id="previewModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Widget Forhåndsvisning</h3>
                <button class="close-btn" onclick="closeModal('previewModal')">&times;</button>
            </div>
            <iframe id="previewFrame" width="100%" height="600" style="border:none; border-radius:8px;"></iframe>
        </div>
    </div>
    
    <!-- Embed Code Modal -->
    <div id="embedModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Embed-kode</h3>
                <button class="close-btn" onclick="closeModal('embedModal')">&times;</button>
            </div>
            <div id="embedContent"></div>
        </div>
    </div>
    
    <!-- New Partner Modal -->
    <div id="newPartnerModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h3>Ny Partner</h3>
                <button class="close-btn" onclick="closeModal('newPartnerModal')">&times;</button>
            </div>
            <form id="newPartnerForm">
                <div class="form-group">
                    <label>Partner ID</label>
                    <input type="text" name="partner_id" placeholder="eks: byggmester-nord" required>
                </div>
                <div class="form-group">
                    <label>Firmanavn</label>
                    <input type="text" name="name" placeholder="eks: Byggmester Nord AS" required>
                </div>
                <div class="form-group">
                    <label>Merkenavn</label>
                    <input type="text" name="brand_name" placeholder="eks: Byggmester Nord" required>
                </div>
                <div class="form-group">
                    <label>Domene</label>
                    <input type="text" name="domain" placeholder="eks: byggmester-nord.no">
                </div>
                <div class="form-group">
                    <label>Merke-farge</label>
                    <input type="color" name="brand_color" value="#2563eb">
                </div>
                <div class="form-group">
                    <label>Logo URL</label>
                    <input type="url" name="logo_url" placeholder="https://...">
                </div>
                <div class="form-group">
                    <label>Agent Navn</label>
                    <input type="text" name="agent_display_name" value="Oppussingsrådgiver">
                </div>
                <div class="form-group">
                    <label>Velkomstmelding</label>
                    <textarea name="welcome_message" rows="3" placeholder="Hei! Jeg kan hjelpe deg med..."></textarea>
                </div>
                <div class="form-group">
                    <label>Widget Posisjon</label>
                    <select name="widget_position">
                        <option value="bottom-right">Høyre hjørne</option>
                        <option value="bottom-left">Venstre hjørne</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Tema</label>
                    <select name="widget_theme">
                        <option value="light">Lyst</option>
                        <option value="dark">Mørkt</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-success">Opprett Partner</button>
            </form>
        </div>
    </div>
    
    <script>
        const API_BASE = window.location.origin;
        
        function previewWidget(partnerId) {{
            const iframe = document.getElementById('previewFrame');
            iframe.src = `${{API_BASE}}/widget/${{partnerId}}`;
            showModal('previewModal');
        }}
        
        function showEmbedCode(partnerId) {{
            const embedContent = document.getElementById('embedContent');
            const iframeCode = `<iframe src="${{API_BASE}}/widget/${{partnerId}}" 
        width="400" 
        height="600" 
        style="border:none; border-radius:12px; box-shadow: 0 8px 24px rgba(0,0,0,0.15);">
</iframe>`;
            
            const jsCode = `<script src="${{API_BASE}}/widget/${{partnerId}}/embed.js"></script>`;
            
            embedContent.innerHTML = `
                <h4>Iframe Embed</h4>
                <div class="code-block">${{iframeCode.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</div>
                <button class="copy-btn" onclick="copyToClipboard('${{iframeCode.replace(/'/g, "\\'")}}')" >📋 Kopier</button>
                
                <h4 style="margin-top: 2rem;">JavaScript Widget</h4>
                <div class="code-block">${{jsCode.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</div>
                <button class="copy-btn" onclick="copyToClipboard('${{jsCode.replace(/'/g, "\\'")}}')" >📋 Kopier</button>
            `;
            
            showModal('embedModal');
        }}
        
        function showNewPartnerForm() {{
            showModal('newPartnerModal');
        }}
        
        function showModal(modalId) {{
            document.getElementById(modalId).classList.add('show');
        }}
        
        function closeModal(modalId) {{
            document.getElementById(modalId).classList.remove('show');
        }}
        
        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(() => {{
                alert('Kopiert til utklippstavle!');
            }});
        }}
        
        // Handle new partner form
        document.getElementById('newPartnerForm').addEventListener('submit', async (e) => {{
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            data.enabled_agents = ['renovation'];
            data.show_branding = true;
            
            try {{
                const response = await fetch(`${{API_BASE}}/api/partners/`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(data)
                }});
                
                if (response.ok) {{
                    alert('Partner opprettet!');
                    location.reload();
                }} else {{
                    const error = await response.json();
                    alert('Feil: ' + error.detail);
                }}
            }} catch (error) {{
                alert('Feil: ' + error.message);
            }}
        }});
        
        // Close modals on outside click
        document.querySelectorAll('.modal').forEach(modal => {{
            modal.addEventListener('click', (e) => {{
                if (e.target === modal) {{
                    modal.classList.remove('show');
                }}
            }});
        }});
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=dashboard_html)