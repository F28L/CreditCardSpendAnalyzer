# 🚀 How to Run the Finance AI App

This guide will help you get the Finance AI app running on your machine.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** installed
- **Poetry** installed (`pip install poetry`)
- **OpenAI API key** (already configured)
- **Plaid sandbox credentials** (already configured)

---

## 🏃 Quick Start (5 minutes)

### Step 1: Start the Backend API

```bash
# Navigate to backend directory
cd /Users/s.ramesh/Workspace/PersonalProjects/CreditCardSpendAnalyzer/backend

# Activate Poetry virtual environment
poetry shell

# Run the FastAPI server
python main.py
```

**Backend will be running on:** `http://localhost:8000`

✅ **Verify it's working:** Open http://localhost:8000/docs in your browser

---

### Step 2: Start the Frontend UI

Open a **new terminal window** (keep backend running):

```bash
# Navigate to frontend directory
cd /Users/s.ramesh/Workspace/PersonalProjects/CreditCardSpendAnalyzer/frontend

# Start Vite dev server
npm run dev
```

**Frontend will be running on:** `http://localhost:5173`

✅ **Open your browser:** http://localhost:5173

You should see the beautiful Apple Wallet-style dark mode UI! 🎨

---

## 🎯 Alternative: Run with Single Commands

### Backend (Terminal 1)
```bash
cd backend && poetry run python main.py
```

### Frontend (Terminal 2)
```bash
cd frontend && npm run dev
```

---

## 🔍 API Endpoints

Once backend is running, explore these URLs:

| Endpoint | Description |
|----------|-------------|
| http://localhost:8000 | API info |
| http://localhost:8000/health | Health check |
| http://localhost:8000/docs | **Interactive API docs** (Swagger UI) |
| http://localhost:8000/redoc | Alternative API docs |

---

## 📱 Frontend Pages

| Page | Description |
|------|-------------|
| http://localhost:5173/ | Dashboard (Home) |
| http://localhost:5173/cards | Credit Cards |
| http://localhost:5173/insights | AI Insights |
| http://localhost:5173/analytics | Analytics |

---

## 🧪 Testing the Integrations

### 1. Test OpenAI Integration

From API docs (http://localhost:8000/docs):

```bash
POST /api/ai/analyze

Request body:
{
  "date_range_start": "2024-01-01",
  "date_range_end": "2024-01-31",
  "insight_type": "spending_analysis"
}
```

### 2. Test Plaid Integration

From API docs:

```bash
POST /api/plaid/create-link-token
```

This will return a `link_token` that can be used with Plaid Link in the frontend.

---

## 🐛 Troubleshooting

### Backend won't start?

**Issue:** `ModuleNotFoundError: No module named 'models'`

**Solution:**
```bash
cd backend
poetry install  # Reinstall dependencies
poetry run python main.py
```

---

### Frontend won't start?

**Issue:** `Cannot find module 'react'`

**Solution:**
```bash
cd frontend
npm install  # Reinstall dependencies
npm run dev
```

---

### Port already in use?

**Backend (8000):**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

**Frontend (5173):**
```bash
# Find and kill process
lsof -ti:5173 | xargs kill -9
```

---

### Database issues?

**Reset database:**
```bash
cd backend
rm finance.db  # Delete old database
poetry run python main.py  # Will create new database
```

---

## 🎨 What You Should See

### Backend (http://localhost:8000/docs)
- Interactive Swagger UI
- 15+ API endpoints organized by:
  - Plaid Integration
  - AI Insights
  - Analytics

### Frontend (http://localhost:5173)
- Dark mode Apple Wallet interface
- Credit card components with gradients
- Spending stats and trends
- AI insights card
- Recent activity feed
- Bottom navigation bar

---

## 🔑 Environment Configuration

Your credentials are already set in `backend/.env`:

```bash
# Plaid (Sandbox)
PLAID_CLIENT_ID=699147cbeea30900214a8b4e
PLAID_SECRET=3c012345dfe16beaca8e09c040a5c7

# OpenAI
OPENAI_API_KEY=sk-proj-vnKGJc...
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini

# Database
DATABASE_URL=sqlite+aiosqlite:///./finance.db
```

---

## 📊 Data Flow

```
Frontend (React)
    ↓ HTTP Requests
Backend API (FastAPI)
    ↓
   ├─→ Plaid API (fetch transactions)
   ├─→ OpenAI API (analyze spending)
   └─→ SQLite Database (store data)
```

---

## 🛑 Stopping the App

### Stop Backend
- Press `Ctrl + C` in the backend terminal

### Stop Frontend
- Press `Ctrl + C` in the frontend terminal

### Or Kill All Processes
```bash
# Kill backend
lsof -ti:8000 | xargs kill -9

# Kill frontend
lsof -ti:5173 | xargs kill -9
```

---

## 🎯 Next Steps After Running

1. **Connect a Bank Account:**
   - Click "Connect Bank" button in the UI
   - Use Plaid sandbox credentials
   - Test with dummy data

2. **View API Documentation:**
   - Explore http://localhost:8000/docs
   - Try out different endpoints
   - See request/response formats

3. **Test AI Analysis:**
   - Add some sample transactions via API
   - Trigger AI analysis
   - View insights in the UI

---

## 💡 Development Tips

### Hot Reload Enabled

- **Backend:** Changes to Python files auto-reload the server
- **Frontend:** Changes to React files auto-refresh the browser

### View Logs

**Backend logs:**
- Terminal where you ran `python main.py`
- Shows SQL queries, API requests, errors

**Frontend logs:**
- Browser Developer Console (F12)
- Network tab for API calls

---

## 🎉 Success!

If you see:

✅ Backend running on http://localhost:8000
✅ Frontend running on http://localhost:5173
✅ Beautiful dark mode UI loads
✅ API docs accessible

**You're all set! The app is running successfully.** 🚀

---

## 📞 Need Help?

- Check backend logs for errors
- Open browser console (F12) for frontend errors
- Verify both servers are running
- Check that ports 8000 and 5173 are not in use

---

**Last Updated:** 2025-02-15
**Version:** 1.0.0
