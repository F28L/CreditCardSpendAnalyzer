# Finance AI App - Personal Finance Analytics with AI

A full-stack application for analyzing credit card and bank spending using AI-powered insights. Fetches 24 months of transaction history from Plaid, analyzes spending patterns using local (Ollama) or cloud (OpenAI) LLMs, and provides interactive visualizations.

## 🎯 Features

### ✅ Implemented (Backend Complete)
- **Multi-source Data Ingestion**
  - 24-month transaction history via Plaid API
  - Automatic pagination for large datasets (500+ transactions)
  - Incremental sync with deduplication
  - Venmo CSV upload support (planned)

- **AI-Powered Analysis**
  - Swappable LLM providers (Ollama or OpenAI)
  - Spending insights and pattern detection
  - Automatic transaction categorization
  - Reimbursement detection with confidence scores

- **Comprehensive Analytics**
  - Per-card spending breakdown
  - Time-series analysis (daily/weekly/monthly)
  - Category-based spending analysis
  - Reimbursement tracking
  - Key spending metrics and summaries

### 🚧 In Progress
- React frontend with Vite + TypeScript
- Interactive charts with Chart.js
- Plaid Link integration for account connection
- Dashboard and insights UI

## 🏗️ Architecture

```
├── backend/                    # FastAPI Backend
│   ├── api/routes/            # API Endpoints
│   │   ├── plaid.py           # Plaid integration routes
│   │   ├── ai.py              # AI insights routes
│   │   └── analytics.py       # Analytics routes
│   ├── services/
│   │   ├── llm/               # LLM abstraction layer
│   │   │   ├── base.py        # Abstract interface
│   │   │   ├── ollama_provider.py
│   │   │   ├── openai_provider.py
│   │   │   └── factory.py     # Provider selection
│   │   └── plaid_service.py   # Plaid API wrapper
│   ├── models/                # SQLAlchemy models
│   │   ├── account.py
│   │   ├── transaction.py
│   │   ├── ai_insight.py
│   │   └── plaid_item.py
│   ├── schemas/               # Pydantic schemas
│   ├── tests/                 # Unit tests
│   ├── config.py              # Settings management
│   ├── database.py            # Async DB session
│   └── main.py                # FastAPI app
│
├── frontend/                  # React Frontend (Coming)
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
│
└── TODO.md                    # Development roadmap
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL 15+ or SQLite
- **LLM Provider (choose one):**
  - Ollama (local, free) - [Download](https://ollama.ai)
  - OpenAI API key - [Get key](https://platform.openai.com/api-keys)
- Plaid Developer Account - [Sign up](https://plaid.com/developer)

### Backend Setup

1. **Clone and Navigate**
   ```bash
   cd CreditCardSpendAnalyzer/backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # - PLAID_CLIENT_ID and PLAID_SECRET
   # - LLM_PROVIDER (ollama or openai)
   # - OPENAI_API_KEY (if using OpenAI)
   ```

5. **Set Up LLM Provider**

   **Option A: Ollama (Local, Free)**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3  # or mistral, phi3
   ```

   **Option B: OpenAI (Cloud, Paid)**
   ```bash
   # Add to .env:
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-your-key-here
   OPENAI_MODEL=gpt-4o-mini
   ```

6. **Run the Backend**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Frontend Setup (Coming Soon)
```bash
cd frontend
npm install
npm run dev
```

## 📚 API Documentation

### Plaid Integration
- **POST** `/api/plaid/create-link-token` - Create Plaid Link token
- **POST** `/api/plaid/exchange-public-token` - Exchange token & sync accounts
- **POST** `/api/plaid/sync-transactions` - Manual transaction sync
- **GET** `/api/plaid/accounts` - List connected accounts

### AI Insights
- **POST** `/api/ai/analyze` - Generate spending insights
  ```json
  {
    "date_range_start": "2024-01-01",
    "date_range_end": "2024-01-31",
    "insight_type": "spending_analysis"
  }
  ```
- **GET** `/api/ai/insights` - Retrieve stored insights
- **POST** `/api/ai/categorize-transaction/{id}` - Categorize single transaction
- **POST** `/api/ai/bulk-categorize` - Bulk categorization (background)

### Analytics
- **GET** `/api/analytics/spending-by-card` - Per-card spending
- **GET** `/api/analytics/spending-over-time` - Time-series data
  - Query params: `granularity` (daily/weekly/monthly)
- **GET** `/api/analytics/categories` - Category breakdown
- **GET** `/api/analytics/reimbursements` - List reimbursements
- **GET** `/api/analytics/summary` - Overall spending metrics

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
pytest --cov=. tests/  # With coverage
```

Current test coverage:
- ✅ Database models (7 tests)
- ✅ LLM providers (12 tests)
- ✅ Plaid service (6 tests)
- 🚧 API routes (coming)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./finance.db` |
| `PLAID_CLIENT_ID` | Plaid API client ID | Required |
| `PLAID_SECRET` | Plaid API secret | Required |
| `PLAID_ENV` | Plaid environment | `sandbox` |
| `LLM_PROVIDER` | LLM provider (ollama/openai) | `ollama` |
| `OLLAMA_MODEL` | Ollama model name | `llama3` |
| `OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `OPENAI_MODEL` | OpenAI model | `gpt-4o-mini` |

### LLM Provider Comparison

| Feature | Ollama | OpenAI |
|---------|--------|--------|
| Cost | Free | ~$0.001-0.03/query |
| Speed | 5-15 seconds | 1-3 seconds |
| Privacy | 100% local | Cloud-based |
| Quality | Good | Excellent |
| Hardware | 8GB+ RAM | None |
| Internet | Not required | Required |

## 🗺️ Roadmap

See [TODO.md](TODO.md) for detailed development plan.

### Phase Status
- ✅ **Phase 1:** Backend Foundation (Complete)
- ✅ **Phase 2:** LLM Integration (Complete)
- ✅ **Phase 3:** Plaid Integration (Complete)
- 🚧 **Phase 4:** Venmo Integration (CSV upload)
- ✅ **Phase 5:** Analytics API (Complete)
- ✅ **Phase 6:** AI Insights API (Complete)
- 🚧 **Phase 7:** Frontend Development (In Progress)
- ⏳ **Phase 8-10:** Testing, Polish, Documentation

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (async)
- **Database:** SQLAlchemy 2.0 (async) + PostgreSQL/SQLite
- **LLM:** Ollama / OpenAI
- **Financial Data:** Plaid API
- **Testing:** pytest + pytest-asyncio

### Frontend (In Progress)
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Charts:** Chart.js + react-chartjs-2
- **Styling:** Tailwind CSS
- **State:** React Query

## 📊 Database Schema

### Tables
- **accounts:** Financial accounts (credit cards, checking, savings)
- **transactions:** Individual transactions from all sources
- **ai_insights:** Stored LLM-generated insights
- **plaid_items:** Plaid access tokens and item metadata

### Key Relationships
- Account → Transactions (one-to-many)
- Transaction deduplication via `external_id` (unique)

## 🔐 Security Considerations

- **API Keys:** Never commit `.env` file (already in `.gitignore`)
- **Plaid Tokens:** Access tokens encrypted at rest (recommended)
- **Data Privacy:**
  - Ollama: All data stays local
  - OpenAI: Transaction data sent to OpenAI servers
- **Rate Limiting:** Implemented for LLM API calls

## 🤝 Contributing

This is a personal project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [Claude Code](https://claude.com/claude-code)
- Financial data via [Plaid](https://plaid.com)
- LLM providers: [Ollama](https://ollama.ai) / [OpenAI](https://openai.com)

---

**Status:** Backend Complete (95%) | Frontend In Progress (10%) | Tests (40%)

**Last Updated:** 2025-02-15
