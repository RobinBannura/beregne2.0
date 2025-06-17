# Beregne 2.0 - Claude Code Memory

## 🎯 Project Status
Complete AI-powered calculator platform for Norway with partner embedding system.

## 🚀 Live Production URLs
- **Marketing**: https://beregne2-0-marketing.vercel.app
- **API**: https://beregne20-production.up.railway.app  
- **Dashboard**: https://beregne20-production.up.railway.app/dashboard
- **househacker Widget**: https://beregne20-production.up.railway.app/widget/househacker

## 🏗️ Architecture
- **Marketing Site**: Next.js 14 + Tailwind (Vercel)
- **API Backend**: FastAPI + SQLite → PostgreSQL (Railway)
- **Widget System**: Embeddable HTML/JS widgets
- **Partner System**: Configurable branding and agent selection

## 🤖 AI Agents
- **Enhanced Renovation Agent**: Complete building cost calculator with CRM integration (ACTIVE)
  - Material and labor calculations with realistic Norwegian pricing
  - Complete project estimates (materials, labor, overhead, project management)
  - Lead generation for projects over 50,000 NOK
  - Monday.com CRM integration active (Board ID: 2004442153)
  - Automatic lead capture with consultation booking
- **Loan Agent**: Norwegian lending rules (PLANNED)
- **Energy Agent**: Real-time electricity prices (PLANNED)

## 👥 Partners
- **househacker**: Active partner with renovation agent
  - Brand color: #e11d48
  - Widget position: bottom-right
  - Agents: ["renovation"]

## 🔧 Development Commands
```bash
# Start all services locally
cd /Users/robin/beregne-2.0
cd apps/api && python3 -m uvicorn app.main:app --reload --port 8000 &
cd apps/marketing && npm run dev &

# Test enhanced renovation agent
cd apps/api && python3 -c "
import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent
async def test():
    agent = EnhancedRenovationAgent()
    result = await agent.process('Jeg skal pusse opp badet komplett - 15 m²')
    print(f'Total cost: {result.get(\"total_cost\", 0):,.0f} NOK')
asyncio.run(test())
"

# Deploy
git add . && git commit -m "message" && git push
```

## 📋 Next Tasks
- [x] Add PostgreSQL database to Railway ✅ DONE
- [x] Update Start Command: `python init_db.py; python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT` ✅ DONE
- [x] Test persistent database with househacker partner ✅ DONE
- [x] Enhanced renovation agent with complete building cost calculator ✅ DONE
- [x] Monday.com CRM integration for lead generation ✅ DONE
- [x] Set up Monday.com API credentials (MONDAY_API_TOKEN, MONDAY_BOARD_ID) ✅ DONE
- [x] Test lead generation workflow with real Monday.com board ✅ DONE
- [ ] Consider custom domains (beregne.no)
- [ ] Add real-time pricing API integrations (Maxbo, Byggmax)

## 🔗 GitHub
Repository: https://github.com/RobinBannura/beregne2.0

## 💾 Database Schema
```sql
partners (
  id, partner_id, name, brand_name, brand_color, 
  logo_url, enabled_agents, agent_display_name,
  welcome_message, widget_position, widget_theme,
  show_branding, is_active, created_at, updated_at
)
```

## 🎯 Embed Code for househacker
```html
<iframe src="https://beregne20-production.up.railway.app/widget/househacker" 
        width="400" height="600" 
        style="border:none; border-radius:12px;">
</iframe>
```