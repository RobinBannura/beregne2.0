# Beregne 2.0 - AI-Powered Calculator Platform

> Norway's most intelligent calculator platform, powered by AI to provide expert calculations and advice across loans, energy, and general mathematics.

## 🏗️ Architecture

This is a monorepo containing:

- **Frontend** (`apps/web`): Next.js 14 application with Tailwind CSS
- **Backend** (`apps/api`): FastAPI with SQLite and AI orchestration
- **Widget** (`apps/embed`): Embeddable JavaScript widget for partners
- **Shared** (`packages/shared`): Common types and utilities

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- OpenAI API key

### Development Setup

1. **Clone and install dependencies**
```bash
git clone https://github.com/RobinBannura/beregne2.0.git
cd beregne2.0
npm install
```

2. **Set up environment variables**
```bash
# Backend
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env with your API keys

# Frontend
cp apps/web/.env.example apps/web/.env.local
# Edit with your configuration
```

3. **Start development servers**
```bash
# All services (recommended)
npm run dev

# Or individually:
npm run dev:api     # Backend on port 8000
npm run dev:web     # Frontend on port 3000
npm run dev:widget  # Widget on port 3002
```

4. **Initialize database**
```bash
cd apps/api
python -m alembic upgrade head
```

## 🧠 AI Agents

### Loan Agent
- Mortgage calculations with Norwegian rules (5x income, 85% LTV)
- Car and personal loans
- Effective interest rate calculations
- Debt-to-income analysis

### Energy Agent
- Real-time electricity prices from hvakosterstrommen.no
- Energy saving calculations
- Heat pump vs electric heating comparisons
- Power consumption estimates

### General Agent
- Mathematical calculations
- Unit conversions (metric/imperial)
- Building material calculations
- Everyday calculations (tips, discounts, etc.)

## 📊 Features

### Core Platform
- ✅ AI-powered calculation routing
- ✅ Multi-agent architecture with specialized expertise
- ✅ Norwegian financial rules and regulations
- ✅ Real-time electricity price integration
- ✅ HTML-formatted responses with tables

### Partner System
- ✅ Embeddable widget (iframe and JavaScript)
- ✅ Partner dashboard with analytics
- ✅ Custom agent filtering per partner
- ✅ Revenue sharing from sponsors

## 🔧 API Usage

### Chat Endpoint
```bash
POST /api/chat
Content-Type: application/json

{
  "message": "Hvor mye kan jeg låne til bolig med 800k i årslønn?",
  "session_id": "optional-session-id",
  "partner_id": "optional-partner-id"
}
```

### Response
```json
{
  "response": "<h3>Boliglån beregning:</h3><table>...</table>",
  "session_id": "session-123",
  "agent_used": "loan",
  "routing": {
    "agent_used": "loan",
    "confidence": 0.95,
    "reasoning": "Boliglån spørsmål"
  }
}
```

## 🔌 Widget Integration

### Basic Integration
```html
<script src="https://cdn.beregne.no/widget/beregne-widget.min.js"></script>
<div id="beregne-widget"></div>
<script>
new BeregneWidget('beregne-widget', {
  apiUrl: 'https://api.beregne.no',
  partnerId: 'your-partner-id',
  theme: 'light',
  position: 'bottom-right'
});
</script>
```

## 🚀 Deployment

### Environment Variables
```bash
# Production environment variables
DATABASE_URL=sqlite:///beregne.db
OPENAI_API_KEY=sk-...
SECRET_KEY=...
ENVIRONMENT=production
DEBUG=false
```

### Build Commands
```bash
# Build all apps
npm run build

# Build specific app
npm run build:web
npm run build:api
npm run build:widget
```

## 🛠️ Development

### Project Structure
```
beregne2.0/
├── apps/
│   ├── api/          # FastAPI backend
│   ├── web/          # Next.js frontend
│   └── embed/        # Embeddable widget
├── packages/
│   └── shared/       # Shared utilities
├── assets/           # Static assets
└── infrastructure/   # Deployment configs
```

### Scripts
```bash
npm run dev           # Start all development servers
npm run build         # Build all applications
npm run lint          # Lint all code
npm run test          # Run all tests
npm run clean         # Clean build artifacts
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- 📧 Email: support@beregne.no
- 💬 Issues: [GitHub Issues](https://github.com/RobinBannura/beregne2.0/issues)

---

Made with ❤️ in Norway 🇳🇴