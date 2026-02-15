# Finance AI App - Development TODO

## Status Legend
- [ ] Not Started
- [x] Completed
- [!] Blocked/Issue

---

## Phase 1: Foundation & Setup

### Backend Setup
- [x] Create backend directory structure (api/, services/, models/, config/)
- [x] Set up Python virtual environment and requirements.txt
- [x] Create .env.example with all required environment variables
- [x] Implement database models using SQLAlchemy (Account, Transaction, AIInsight, PlaidItem)
- [x] Set up FastAPI application with basic configuration
- [x] Add database initialization and migration setup with Alembic
- [x] Create Pydantic models for request/response validation
- [x] Write unit tests for database models

### Frontend Setup
- [ ] Create frontend directory with Vite + React + TypeScript
- [ ] Set up basic routing with React Router
- [ ] Configure Tailwind CSS for styling
- [ ] Create basic layout components (Header, Sidebar, Main)
- [ ] Set up axios for API calls
- [ ] Configure environment variables for frontend

### Configuration
- [ ] Create comprehensive .env.example file
- [ ] Add .env to .gitignore
- [ ] Document setup instructions in README.md

---

## Phase 2: LLM Integration

### LLM Service Layer
- [x] Create abstract BaseLLMProvider class
- [x] Implement OllamaProvider with generate_insight and categorize_transaction methods
- [x] Implement OpenAIProvider with generate_insight and categorize_transaction methods
- [x] Create LLM factory to instantiate correct provider based on config
- [x] Add LLM provider configuration to settings
- [x] Write unit tests for LLM providers (with mocking)
- [x] Add error handling for LLM API failures

---

## Phase 3: Plaid Integration

### Plaid Service
- [x] Install plaid-python SDK
- [x] Create PlaidService class for API interactions
- [x] Implement create_link_token endpoint
- [x] Implement exchange_public_token endpoint
- [x] Implement get_accounts endpoint to fetch account details
- [x] Implement sync_transactions with 24-month date range and pagination
- [x] Add incremental sync logic using last_sync_timestamp
- [x] Implement transaction deduplication logic
- [x] Add background task support for long-running syncs
- [x] Write unit tests for Plaid service (with mocked API)

### Plaid Frontend
- [ ] Install react-plaid-link library
- [ ] Create PlaidLinkButton component
- [ ] Implement Plaid Link flow (connect accounts)
- [ ] Show account connection status
- [ ] Add manual sync trigger button
- [ ] Display sync progress indicator

---

## Phase 4: Venmo Integration

### Venmo Investigation
- [ ] Research PayPal API for Venmo transaction access
- [ ] Check Plaid's current Venmo support status
- [ ] Document findings in VENMO_RESEARCH.md

### Venmo CSV Upload
- [ ] Create Venmo CSV parser service
- [ ] Implement file upload endpoint (/api/transactions/upload-venmo)
- [ ] Map Venmo CSV columns to Transaction model
- [ ] Add reimbursement detection using keywords (reimburse, paid back, split)
- [ ] Create frontend file upload component
- [ ] Display uploaded Venmo transactions
- [ ] Write unit tests for CSV parser

---

## Phase 5: Analytics & Data Visualization

### Backend Analytics Endpoints
- [x] Implement GET /api/analytics/spending-by-card endpoint
- [x] Implement GET /api/analytics/spending-over-time endpoint with granularity
- [x] Implement GET /api/analytics/categories endpoint for category breakdown
- [x] Implement GET /api/analytics/reimbursements endpoint
- [x] Add spending summary endpoint with key metrics
- [ ] Add caching layer for expensive aggregations
- [ ] Write unit tests for analytics endpoints

### Frontend Dashboard
- [ ] Install Chart.js and react-chartjs-2
- [ ] Create SpendingOverTimeChart component (line chart)
- [ ] Create SpendingByCardChart component (bar chart)
- [ ] Create CategoryPieChart component
- [ ] Build main Dashboard page with all charts
- [ ] Add date range filter component
- [ ] Add account filter (show/hide specific cards)

---

## Phase 6: AI-Powered Insights

### AI Analysis Backend
- [x] Implement POST /api/ai/analyze endpoint
- [x] Create prompt templates for spending analysis
- [x] Add transaction-to-text formatting for LLM input
- [x] Implement GET /api/ai/insights endpoint to retrieve cached insights
- [x] Add background job for bulk transaction categorization
- [x] Store insights in ai_insights table with metadata
- [x] Add /api/ai/categorize-transaction endpoint for single transactions
- [ ] Write unit tests for AI analysis logic

### AI Insights Frontend
- [ ] Create AIInsightCard component to display analysis
- [ ] Add "Analyze" button to trigger AI analysis
- [ ] Show loading state during LLM processing
- [ ] Display AI-generated categories and recommendations
- [ ] Add ability to regenerate insights

---

## Phase 7: Transaction Management

### Transaction Views
- [ ] Create GET /api/transactions endpoint with pagination and filters
- [ ] Build TransactionList component with table view
- [ ] Add search/filter by merchant, amount, date
- [ ] Implement transaction detail modal
- [ ] Add manual transaction creation form
- [ ] Allow marking transactions as reimbursements manually

---

## Phase 8: Account Management

### Account Pages
- [ ] Create Accounts page showing all connected accounts
- [ ] Display account details (name, type, last_four, institution)
- [ ] Show last sync timestamp per account
- [ ] Add remove account functionality
- [ ] Display account balance (if available from Plaid)

---

## Phase 9: Testing & Quality

### Backend Tests
- [ ] Write integration tests for Plaid flow (with mocked Plaid API)
- [ ] Write integration tests for AI analysis flow
- [ ] Add tests for 24-month transaction pagination
- [ ] Test incremental sync logic
- [ ] Test CSV upload and parsing

### Frontend Tests
- [ ] Add unit tests for chart components
- [ ] Add integration tests for Plaid Link flow
- [ ] Test date range filtering
- [ ] Test API error handling and display

---

## Phase 10: Polish & Documentation

### UI/UX Improvements
- [ ] Add loading states for all async operations
- [ ] Implement error boundaries and error displays
- [ ] Add toast notifications for success/error messages
- [ ] Improve responsive design for mobile
- [ ] Add empty states for no data scenarios

### Documentation
- [ ] Write comprehensive README with setup instructions
- [ ] Document environment variables in .env.example
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Create user guide for Plaid connection and Venmo upload
- [ ] Document LLM provider selection (Ollama vs OpenAI)

### Performance
- [ ] Add database indexes for common queries
- [ ] Optimize transaction queries for 24-month datasets
- [ ] Add request caching where appropriate
- [ ] Lazy load chart data

---

## Bugs & Issues
*(This section will be populated as issues are discovered)*

---

## Future Enhancements
- [ ] Add budget tracking and alerts
- [ ] Detect recurring transactions automatically
- [ ] Export data to CSV/Excel
- [ ] Multi-user support with authentication
- [ ] Mobile app (React Native)
- [ ] Receipt upload and OCR
- [ ] Investment account tracking

---

**Last Updated:** 2025-02-15
