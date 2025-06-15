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
- **Renovation Agent**: Material calculations, Norwegian pricing (ACTIVE)
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

# Deploy
git add . && git commit -m "message" && git push
```

## 📋 Next Tasks
- [ ] Add PostgreSQL database to Railway
- [ ] Update Start Command: `python init_db.py; python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Test persistent database with househacker partner
- [ ] Consider custom domains (beregne.no)

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