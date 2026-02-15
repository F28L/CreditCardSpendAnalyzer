# Financial Analytics App - Technical Plan

## Project Overview

### Goal
Build a personal finance analytics application that:
- Pulls **24 months** of transaction data from multiple credit cards and bank accounts via Plaid
- Ingests Venmo transactions to track peer-to-peer payments and reimbursements
- Uses either **Ollama (local)** or **OpenAI API** to analyze spending patterns
- Displays interactive visualizations of spending per card over time
- Identifies reimbursements and payment flows

### Recent Updates
- ✅ Added **OpenAI API support** as alternative to Ollama
- ✅ Changed transaction history from 30 days to **24 months**
- ✅ Added pagination strategy for large data fetches
- ✅ Added investigation plan for PayPal/Venmo API access

### Key Features
1. **Multi-source data ingestion** (Plaid + Venmo) with **24-month history**
2. **AI-powered spending analysis** using **Ollama (local) or OpenAI API**
3. **Per-card spending breakdown**
4. **Time-series visualization** of transactions
5. **Reimbursement tracking** (paid back vs paid out)
6. **Category-based spending insights**

---

## Architecture

```
┌─────────────────┐
│   Web Browser   │
│   (React UI)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  FastAPI Server │◄─────┐
│   (Python 3.11+)│      │
└────────┬────────┘      │
         │                │
         ├────────────────┼──────────────┬──────────┐
         ▼                ▼              ▼          ▼
┌────────────┐   ┌──────────┐  ┌──────────┐  ┌──────────┐
│ PostgreSQL │   │  Plaid   │  │  Ollama  │  │  OpenAI  │
│  Database  │   │   API    │  │  (Local) │  │   API    │
└────────────┘   └──────────┘  └──────────┘  └──────────┘
                                      └──────────┘
                                    (Choose One)
```

---

## Technology Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (async support, automatic OpenAPI docs)
- **Database ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL (production) / SQLite (development)
- **LLM Integration:** `ollama` Python package + `openai` Python package
- **API Client:** `plaid-python` SDK
- **Data Processing:** pandas (for CSV parsing)

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Charting:** Chart.js + react-chartjs-2
- **UI Components:** shadcn/ui or Tailwind CSS
- **State Management:** React Query (for server state)
- **HTTP Client:** axios

### Infrastructure
- **LLM:** Ollama (local, models: llama3 or mistral) OR OpenAI API (gpt-4/gpt-3.5-turbo)
- **API Gateway:** Plaid Link (for secure account linking)
- **Version Control:** Git

---

## LLM Provider Configuration

The application supports **two LLM providers**:

### Option 1: Ollama (Local, Free)
**Pros:**
- Completely free
- Data stays on your machine (privacy)
- No API rate limits
- Works offline

**Cons:**
- Requires decent hardware (8GB+ RAM recommended)
- Slower inference (5-15 seconds per query)
- Lower quality responses compared to GPT-4

**Recommended Models:**
- `llama3:8b` - Best balance of speed and quality
- `mistral:7b` - Faster, good for simple categorization
- `llama3:70b` - Highest quality (requires 48GB+ RAM)

### Option 2: OpenAI API (Cloud, Paid)
**Pros:**
- Fast responses (1-3 seconds)
- Higher quality analysis (GPT-4)
- No local hardware requirements

**Cons:**
- Costs money ($0.01-0.03 per analysis)
- Requires internet connection
- Sends transaction data to OpenAI servers

**Recommended Models:**
- `gpt-3.5-turbo` - Fast and cheap ($0.001/1K tokens)
- `gpt-4-turbo` - Best quality ($0.01/1K tokens)
- `gpt-4o-mini` - Good balance ($0.00015/1K tokens)

### Configuration in `.env`
```bash
# Choose LLM provider: 'ollama' or 'openai'
LLM_PROVIDER=ollama

# Ollama settings (if using Ollama)
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI settings (if using OpenAI)
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

---

## Database Schema

### Tables

#### 1. `accounts`
```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plaid_account_id VARCHAR(255) UNIQUE,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50), -- 'credit', 'checking', 'savings'
    institution_name VARCHAR(255),
    last_four VARCHAR(4),
    last_sync_timestamp TIMESTAMP, -- Track last successful sync
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 2. `transactions`
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(255) UNIQUE NOT NULL, -- Plaid transaction ID or Venmo ID
    account_id UUID REFERENCES accounts(id),
    amount DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    merchant_name VARCHAR(255),
    description TEXT,
    category VARCHAR(100),
    source VARCHAR(20) CHECK (source IN ('plaid', 'venmo', 'manual')),
    is_reimbursement BOOLEAN DEFAULT FALSE,
    ai_category VARCHAR(100), -- LLM-generated category
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_date (date),
    INDEX idx_account_date (account_id, date),
    INDEX idx_source (source)
);
```

#### 3. `ai_insights`
```sql
CREATE TABLE ai_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    insight_type VARCHAR(50), -- 'monthly_summary', 'anomaly', 'category_breakdown'
    date_range_start DATE,
    date_range_end DATE,
    content TEXT NOT NULL,
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. `plaid_items`
```sql
CREATE TABLE plaid_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    access_token VARCHAR(255) NOT NULL,
    item_id VARCHAR(255) UNIQUE NOT NULL,
    institution_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Storage Considerations for 24 Months of Data

**Estimated Storage Requirements:**
- Average credit card user: ~100-300 transactions/month
- 24 months × 250 transactions = ~6,000 transactions per card
- 3-5 credit cards = ~18,000-30,000 transactions total
- Database size: ~50-100 MB (including indexes)

**Optimization Strategies:**
1. **Indexes:** Add composite indexes on frequently queried columns
   ```sql
   CREATE INDEX idx_transactions_date_account ON transactions(account_id, date DESC);
   CREATE INDEX idx_transactions_category ON transactions(category, date DESC);
   ```

2. **Data Archival (Optional for future):**
   - Keep last 12 months in "hot" table for fast queries
   - Move older data to archive table
   - Union queries when needed for full history

3. **Caching:**
   - Cache aggregated analytics (monthly totals, category summaries)
   - Invalidate cache on new transaction sync

---

## API Design

### Backend Endpoints

#### Authentication & Setup
- `POST /api/plaid/create-link-token` - Generate Plaid Link token
- `POST /api/plaid/exchange-public-token` - Exchange public token for access token
- `GET /api/accounts` - List all connected accounts

#### Data Ingestion
- `POST /api/transactions/sync` - Sync transactions from Plaid (up to 24 months)
  - Query params: `start_date`, `end_date` (defaults to last 24 months)
- `POST /api/transactions/upload-venmo` - Upload Venmo CSV
- `POST /api/transactions/manual` - Manually add a transaction

#### Analytics
- `GET /api/analytics/spending-by-card` - Get spending grouped by account
  - Query params: `start_date`, `end_date`
- `GET /api/analytics/spending-over-time` - Time-series data
  - Query params: `granularity` (daily, weekly, monthly)
- `GET /api/analytics/categories` - Spending breakdown by category
- `GET /api/analytics/reimbursements` - List of reimbursements

#### AI Integration
- `POST /api/ai/analyze` - Trigger AI analysis on transaction set
  - Body: `{ "date_range": {...}, "account_ids": [...] }`
- `GET /api/ai/insights` - Retrieve stored AI insights

---

## LLM Service Architecture

The LLM service uses an **abstraction layer** to support both Ollama and OpenAI seamlessly.

### Backend Structure

```
backend/
├── services/
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract base class
│   │   ├── ollama.py        # Ollama implementation
│   │   ├── openai.py        # OpenAI implementation
│   │   └── factory.py       # Factory to select provider
│   └── plaid_service.py
├── api/
│   └── routes/
│       ├── ai.py
│       └── transactions.py
└── config.py                # Environment config
```

### Implementation

#### 1. Base LLM Interface (`base.py`)
```python
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    async def generate_insight(self, prompt: str, transactions: List[Dict]) -> str:
        """Generate AI insight from transactions"""
        pass

    @abstractmethod
    async def categorize_transaction(self, transaction: Dict) -> str:
        """Categorize a single transaction"""
        pass
```

#### 2. Ollama Provider (`ollama.py`)
```python
import ollama
from .base import BaseLLMProvider
from typing import List, Dict

class OllamaProvider(BaseLLMProvider):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    async def generate_insight(self, prompt: str, transactions: List[Dict]) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a financial analyst AI assistant.'
                },
                {
                    'role': 'user',
                    'content': f"{prompt}\n\nTransactions: {transactions}"
                }
            ]
        )
        return response['message']['content']

    async def categorize_transaction(self, transaction: Dict) -> str:
        prompt = f"""Categorize this transaction into ONE of these categories:
        Groceries, Dining Out, Transportation, Entertainment, Shopping,
        Bills & Utilities, Healthcare, Other

        Transaction: {transaction['merchant_name']} - ${transaction['amount']}
        Description: {transaction.get('description', 'N/A')}

        Respond with ONLY the category name."""

        response = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content'].strip()
```

#### 3. OpenAI Provider (`openai.py`)
```python
from openai import AsyncOpenAI
from .base import BaseLLMProvider
from typing import List, Dict
import json

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_insight(self, prompt: str, transactions: List[Dict]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst AI assistant."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nTransactions: {json.dumps(transactions)}"
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content

    async def categorize_transaction(self, transaction: Dict) -> str:
        prompt = f"""Categorize this transaction into ONE of these categories:
        Groceries, Dining Out, Transportation, Entertainment, Shopping,
        Bills & Utilities, Healthcare, Other

        Transaction: {transaction['merchant_name']} - ${transaction['amount']}
        Description: {transaction.get('description', 'N/A')}

        Respond with ONLY the category name."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
```

#### 4. Factory Pattern (`factory.py`)
```python
from .base import BaseLLMProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from config import settings

def get_llm_provider() -> BaseLLMProvider:
    """Factory function to instantiate the correct LLM provider"""

    if settings.LLM_PROVIDER == "ollama":
        return OllamaProvider(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL
        )
    elif settings.LLM_PROVIDER == "openai":
        return OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")
```

#### 5. Configuration (`config.py`)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./finance.db"

    # Plaid
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENV: str = "sandbox"

    # LLM Configuration
    LLM_PROVIDER: str = "ollama"  # or "openai"

    # Ollama
    OLLAMA_MODEL: str = "llama3"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()
```

#### 6. Usage in API Routes (`api/routes/ai.py`)
```python
from fastapi import APIRouter, Depends
from services.llm.factory import get_llm_provider
from services.llm.base import BaseLLMProvider

router = APIRouter(prefix="/api/ai", tags=["AI"])

@router.post("/analyze")
async def analyze_spending(
    date_range: dict,
    llm: BaseLLMProvider = Depends(get_llm_provider)
):
    # Fetch transactions from DB based on date_range
    transactions = fetch_transactions(date_range)

    # Generate insight using whichever provider is configured
    prompt = "Analyze these transactions and provide spending insights."
    insight = await llm.generate_insight(prompt, transactions)

    return {"insight": insight, "provider": type(llm).__name__}
```

### Benefits of This Architecture

1. **Swappable Providers**: Change `LLM_PROVIDER` in `.env` to switch between Ollama and OpenAI
2. **Testable**: Easy to mock the LLM provider in tests
3. **Extensible**: Can add more providers (Anthropic Claude, Google Gemini) by implementing `BaseLLMProvider`
4. **Type Safe**: Abstract interface ensures all providers implement required methods

---

## Frontend Components

### Page Structure

```
src/
├── pages/
│   ├── Dashboard.tsx          # Main overview
│   ├── Accounts.tsx           # Account management
│   ├── Transactions.tsx       # Transaction list
│   └── Insights.tsx           # AI-generated insights
├── components/
│   ├── PlaidLinkButton.tsx    # Plaid connection flow
│   ├── SpendingChart.tsx      # Line/bar charts
│   ├── CardSpendingCard.tsx   # Per-card spending widget
│   ├── CategoryPieChart.tsx   # Category breakdown
│   └── AIInsightBox.tsx       # Display AI analysis
└── hooks/
    ├── useTransactions.ts
    ├── useAccounts.ts
    └── useAIInsights.ts
```

### Key Visualizations

1. **Spending Over Time (Line Chart)**
   - X-axis: Date
   - Y-axis: Amount spent
   - Multiple lines for different cards

2. **Per-Card Spending (Stacked Bar Chart)**
   - Compare spending across accounts in a given period

3. **Category Breakdown (Pie Chart)**
   - Visualize spending by AI-determined categories

4. **Reimbursement Flow (Sankey Diagram - Future)**
   - Show money flow between accounts and Venmo

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal:** Set up project structure and basic data flow

- [ ] Initialize Git repo
- [ ] Set up Python virtual environment
- [ ] Create FastAPI project structure
- [ ] Set up PostgreSQL database
- [ ] Implement SQLAlchemy models
- [ ] Create React + TypeScript project with Vite
- [ ] Set up basic routing

**Deliverable:** Empty app that connects to database

---

### Phase 2: Plaid Integration (Week 2)
**Goal:** Connect to financial institutions and fetch 24 months of transactions

- [ ] Create Plaid developer account
- [ ] Implement Plaid Link flow in frontend
- [ ] Build backend endpoints for token exchange
- [ ] Implement transaction sync logic with pagination (24 months)
- [ ] Add incremental sync with `last_sync_timestamp` tracking
- [ ] Store transactions in database with deduplication
- [ ] Add background task for long-running syncs
- [ ] Handle Plaid webhooks for updates (optional for MVP)

**Deliverable:** App can connect to banks and pull 24 months of transaction data

---

### Phase 3: Venmo Data Integration (Week 3)
**Goal:** Handle Venmo transactions

- [ ] **Investigate PayPal/Venmo API options** (1-2 days)
  - Research PayPal SDK for Venmo transaction access
  - Check if Plaid has re-added Venmo support
  - Document findings
- [ ] Design Venmo CSV parsing logic (fallback approach)
- [ ] Implement file upload endpoint
- [ ] Map Venmo CSV columns to transaction schema
- [ ] Add reimbursement detection rules (keyword matching)
- [ ] Create transaction deduplication logic

**Deliverable:** Users can upload Venmo CSV and see combined data (+ API investigation report)

---

### Phase 4: Basic Analytics (Week 4)
**Goal:** Display spending data

- [ ] Implement spending-by-card endpoint
- [ ] Implement time-series aggregation
- [ ] Build Chart.js components
- [ ] Create dashboard layout
- [ ] Add date range filters

**Deliverable:** Working dashboard with charts

---

### Phase 5: LLM Integration (Week 5)
**Goal:** Add AI-powered insights

- [ ] Install and configure Ollama OR set up OpenAI API key
- [ ] Pull appropriate model (llama3 or mistral) if using Ollama
- [ ] Design prompt templates for analysis
- [ ] Implement LLM service abstraction layer (supports both providers)
- [ ] Create analysis endpoint
- [ ] Build UI for displaying insights
- [ ] Add caching for LLM responses
- [ ] Add LLM provider selection in settings UI

**Deliverable:** AI can analyze transactions and provide insights using either provider

---

### Phase 6: Polish & Optimization (Week 6)
**Goal:** Improve UX and performance

- [ ] Add loading states
- [ ] Implement error handling
- [ ] Add transaction search/filter
- [ ] Optimize database queries
- [ ] Add data export functionality
- [ ] Write basic tests

**Deliverable:** Production-ready MVP

---

## Challenges & Solutions

### Challenge 1: Venmo API Access
**Problem:** Venmo doesn't offer a public API for personal transaction history.

**Solutions:**
- **Option A (Recommended for MVP):** CSV upload
  - User downloads Venmo transaction history from app
  - App parses and imports CSV
  - Pros: Simple, reliable, no API limits, no ToS violations
  - Cons: Manual process (needs periodic updates)

- **Option B (To Investigate):** PayPal/Venmo API
  - PayPal owns Venmo - investigate if PayPal SDK provides Venmo access
  - Check if PayPal Business accounts can access Venmo transactions
  - Research unofficial APIs or OAuth flows
  - Status: **Needs investigation**
  - Pros: Automated sync
  - Cons: May not be available, might require business account

- **Option C:** Plaid Venmo Integration
  - Plaid previously supported Venmo but removed it
  - Check if Plaid has re-added Venmo support
  - Status: **Unlikely but worth checking**

- **Option D:** Screen scraping (NOT recommended)
  - Use Playwright/Selenium to automate login
  - Pros: Automated
  - Cons: Fragile, violates ToS, security risk, could get account banned

**Decision:**
- **Phase 1 (MVP):** CSV upload
- **Phase 2 (Post-MVP):** Investigate PayPal API options

**Investigation Checklist (Week 3):**
1. Check PayPal Developer Portal for Venmo-specific endpoints
2. Review PayPal REST API documentation for transaction history endpoints
3. Test if PayPal personal accounts can access Venmo data via API
4. Check Plaid's supported institutions list for Venmo
5. Search for unofficial/community Venmo API libraries
6. Review Venmo's Terms of Service for API usage restrictions

**Resources:**
- PayPal Developer Portal: https://developer.paypal.com
- Plaid Supported Institutions: https://plaid.com/institutions
- Venmo API discussions: GitHub, Reddit r/venmo

---

### Challenge 2: Fetching 24 Months of Transaction History
**Problem:** Plaid's `/transactions/get` endpoint has limits on how much data can be fetched at once.

**Key Constraints:**
- **Development/Sandbox:** 24 months of history available
- **Max transactions per request:** 500 transactions
- **Date range limit:** Can request up to 24 months, but need pagination

**Solutions:**
1. **Pagination Strategy:**
   ```python
   # Fetch transactions in chunks
   cursor = None
   all_transactions = []

   while True:
       response = client.transactions_get(
           access_token=access_token,
           start_date=(datetime.now() - timedelta(days=730)).date(),
           end_date=datetime.now().date(),
           options={'count': 500, 'cursor': cursor}
       )
       all_transactions.extend(response['transactions'])

       if response['has_more']:
           cursor = response['next_cursor']
       else:
           break
   ```

2. **Incremental Sync:**
   - Store `last_sync_timestamp` per account in database
   - On subsequent syncs, only fetch transactions since last sync
   - First sync: Fetch all 24 months
   - Daily syncs: Only fetch last 7 days (to catch updates)

3. **Rate Limiting:**
   - Plaid Development: Rate limits exist but generous
   - Add delays between requests if hitting limits
   - Use Plaid webhooks for real-time updates (Production tier)

4. **Background Processing:**
   - Initial 24-month sync can take 30-60 seconds
   - Run as background task with progress indicator
   - Show user "Syncing X of Y accounts..."

---

### Challenge 3: LLM Response Time
**Problem:** Local LLM inference can be slow (5-10 seconds).

**Solutions:**
- Run analysis asynchronously (background task)
- Cache LLM responses by date range
- Show loading spinner with progress indicator
- Pre-generate insights for common queries (daily cron job)

---

### Challenge 4: Transaction Categorization
**Problem:** Plaid categories might not match desired granularity.

**Solutions:**
- Use Plaid's category as a starting point
- Enhance with LLM-based re-categorization
- Allow user to manually override categories
- Build ML model over time based on user corrections

---

### Challenge 5: Reimbursement Detection
**Problem:** Hard to automatically identify which transactions are reimbursements.

**Solutions:**
- Use LLM to analyze transaction descriptions
- Look for keywords: "reimburse", "pay back", "split"
- Match transaction amounts and dates (within 7 days)
- Prompt user to confirm detected reimbursements

---

## Security Considerations

### API Keys & Secrets
- Store Plaid credentials in environment variables
- Store OpenAI API key in environment variables (if using OpenAI)
- Use `.env` file (never commit to Git)
- Add `.env` to `.gitignore`
- Rotate access tokens periodically

### Data Privacy
- **Ollama (Local):** All data stays on your machine - most secure option
- **OpenAI:** Transaction data sent to OpenAI servers for analysis
  - Consider anonymizing merchant names before sending to OpenAI
  - Review OpenAI's data retention policy
  - Be aware of privacy implications for sensitive transactions
- Encrypt Plaid access tokens at rest
- Run locally (no cloud storage of financial data)
- Implement user authentication if multi-user

### Plaid Security
- Use Plaid Link for account connection (secure)
- Never store plaintext Plaid credentials
- Implement webhook signature verification

### LLM Provider Security
- **OpenAI API Key Protection:**
  - Never log or expose API keys in error messages
  - Use environment variables, not hardcoded values
  - Implement rate limiting to prevent API abuse
  - Monitor API usage/costs via OpenAI dashboard
- **Ollama:** No external API calls, runs entirely locally

---

## AI Prompt Engineering

### Example Prompts

#### 1. Spending Analysis
```
You are a financial analyst. Analyze these transactions and provide:
1. Top 3 spending categories
2. Any unusual spending patterns
3. Potential reimbursements or refunds

Transactions:
[JSON data]

Format your response as:
- Category Breakdown: ...
- Anomalies: ...
- Reimbursements: ...
```

#### 2. Category Classification
```
Categorize this transaction into one of these categories:
- Groceries
- Dining Out
- Transportation
- Entertainment
- Shopping
- Bills & Utilities
- Healthcare
- Other

Transaction: {merchant_name} - ${amount} on {date}
Description: {description}

Respond with ONLY the category name.
```

#### 3. Reimbursement Detection
```
Determine if this Venmo transaction is a reimbursement:

Transaction: {description}
Amount: ${amount}
Type: {payment/charge}

Respond with JSON:
{
  "is_reimbursement": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "..."
}
```

---

## Performance Targets

- **Transaction Sync:** < 5 seconds for 500 transactions
- **Chart Rendering:** < 1 second for 1 year of data
- **AI Analysis:** < 10 seconds per insight generation
- **Database Queries:** < 100ms for date range queries

---

## Future Enhancements

### Phase 7 (Post-MVP)
- [ ] Budget tracking and alerts
- [ ] Recurring transaction detection
- [ ] Multi-user support with authentication
- [ ] Mobile app (React Native)
- [ ] Receipt upload and OCR
- [ ] Investment account tracking
- [ ] Bill prediction with ML
- [ ] Export to tax software formats

---

## Testing Strategy

### Unit Tests
- Database models (SQLAlchemy)
- API endpoints (FastAPI TestClient)
- LLM prompt functions
- CSV parsing logic

### Integration Tests
- Plaid API mocking
- Full transaction sync flow
- Chart data aggregation

### Manual Testing Checklist
- [ ] Connect 2+ accounts via Plaid
- [ ] Upload Venmo CSV
- [ ] Generate spending report
- [ ] Trigger AI analysis
- [ ] Verify chart accuracy

---

## Development Environment Setup

### Prerequisites
```bash
# System requirements
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or SQLite for development)

# LLM Provider (Choose One)
- Option A: Ollama (local, free) - Download from ollama.ai
- Option B: OpenAI API - Sign up at platform.openai.com/api-keys

# Plaid Account
- Sign up at plaid.com/developer
- Get Client ID and Secret (Sandbox environment)
```

### Installation Steps
```bash
# 1. Clone repo
git clone <repo-url>
cd finance-ai-app

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env with your credentials:
#   - Add Plaid Client ID and Secret
#   - Choose LLM provider (ollama or openai)
#   - If OpenAI: Add OPENAI_API_KEY
#   - If Ollama: Set OLLAMA_MODEL (default: llama3)

# Example .env:
# PLAID_CLIENT_ID=your_client_id
# PLAID_SECRET=your_secret
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-proj-...
# OPENAI_MODEL=gpt-4o-mini

# 4. Initialize database
alembic upgrade head

# 5. Frontend setup
cd ../frontend
npm install

# 6. Set up LLM (choose based on your .env)
# Option A: If using Ollama
ollama pull llama3

# Option B: If using OpenAI
# (Just make sure OPENAI_API_KEY is in .env - no installation needed)

# 7. Start services
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Ollama (ONLY if using Ollama and not running as service)
ollama serve
```

---

## Questions for Discussion

1. **Database:** SQLite for simplicity or PostgreSQL for robustness?
2. **Frontend Framework:** React or Next.js (if you want SSR)?
3. **LLM Provider:** Ollama (local, free, private) or OpenAI (faster, better quality, costs money)?
   - If Ollama: Which model? Llama3 (8B), Mistral (7B), or Phi-3 (lighter)?
   - If OpenAI: gpt-3.5-turbo (cheap), gpt-4o-mini (balanced), or gpt-4-turbo (best)?
4. **Deployment:** Keep everything local or plan for cloud deployment later?
5. **Venmo:** Are you okay with manual CSV upload, or do you want to explore automation?
6. **Authentication:** Single-user app or multi-user with login?
7. **Real-time Updates:** Should the app auto-sync transactions daily, or manual sync?
8. **Data Retention:** ~~How many years of transaction history to keep?~~ **ANSWERED: 24 months**

---

## Estimated Timeline

- **MVP:** 6 weeks (part-time)
- **Full Feature Set:** 12 weeks

## Next Steps

1. Review this plan and answer the discussion questions
2. Set up development environment
3. Create initial project structure
4. Begin Phase 1 implementation

---

*Last Updated: 2026-02-14*
