# 🚀 Finance AI - Setup & Run Guide

## ⚡ Quick Start (2 Steps)

### Step 1: Start Backend (Terminal 1)
```bash
cd /Users/s.ramesh/Workspace/PersonalProjects/CreditCardSpendAnalyzer/backend
./start.sh
```

### Step 2: Start Frontend (Terminal 2)
```bash
cd /Users/s.ramesh/Workspace/PersonalProjects/CreditCardSpendAnalyzer/frontend
./start.sh
```

**Open Browser:** http://localhost:5173

---

## 🐛 Fixing Import Errors

If you see errors like:
```
ModuleNotFoundError: No module named 'models'
ImportError: cannot import name 'Account' from 'models.account'
```

### Solution: Always run from the backend directory

```bash
# ✅ CORRECT - Run from backend directory
cd /Users/s.ramesh/Workspace/PersonalProjects/CreditCardSpendAnalyzer/backend
poetry run python main.py

# ❌ WRONG - Don't run from project root
cd /Users/s.ramesh/Workspace/PersonalProjects/CreditCardSpendAnalyzer
python backend/main.py  # This will fail!
```

### Why?
Python resolves imports relative to where you run the command. The backend code expects to be run from the `backend/` directory.

---

## 🔄 Restart Everything

### Kill All Running Processes

```bash
# Kill backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Kill frontend (port 5173)
lsof -ti:5173 | xargs kill -9
```

### Fresh Start

**Terminal 1:**
```bash
cd /Users/s.ramesh/Workspace/PersonalProjects/CreditCardSpendAnalyzer/backend
poetry run python main.py
```

**Terminal 2:**
```bash
cd /Users/s.ramesh/Workspace/PersonalProjects/CreditCardSpendAnalyzer/frontend
npm run dev
```

---

## 📦 First Time Setup

### Backend Setup

```bash
cd backend

# Install dependencies
poetry install

# Verify .env file exists
ls -la .env

# If not, copy from example
cp .env.example .env
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

---

## 🧪 Verify It's Working

### Backend Health Check

```bash
# Should return: {"status": "healthy"}
curl http://localhost:8000/health
```

### Frontend Check

Open browser: http://localhost:5173

You should see:
- Dark mode Apple Wallet interface
- Sample credit cards
- Spending stats
- Bottom navigation

---

## 📊 API Documentation

Once backend is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Test endpoints directly from the browser!

---

## 🔧 Common Issues

### Issue: "Address already in use"

**Solution:** Kill the process
```bash
lsof -ti:8000 | xargs kill -9   # Backend
lsof -ti:5173 | xargs kill -9   # Frontend
```

### Issue: "Poetry command not found"

**Solution:** Install Poetry
```bash
pip install poetry
```

### Issue: "npm: command not found"

**Solution:** Install Node.js from nodejs.org

### Issue: Import errors in IDE/Editor

**Solution:** Your IDE needs to recognize the backend directory as the Python root:

**VS Code:**
1. Open Command Palette (Cmd+Shift+P)
2. Select "Python: Select Interpreter"
3. Choose the `.venv` environment from backend folder

**PyCharm:**
1. Right-click `backend` folder
2. Mark Directory as → Sources Root

---

## 🎯 Environment Variables

Your credentials are already configured in `backend/.env`:

```bash
# Plaid (Sandbox)
PLAID_CLIENT_ID=699147cbeea30900214a8b4e
PLAID_SECRET=3c012345dfe16beaca8e09c040a5c7

# OpenAI
OPENAI_API_KEY=sk-proj-vnKGJc...
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini
```

---

## 📱 What You'll See

### Backend (http://localhost:8000)
- API running message
- `/docs` - Interactive API documentation
- `/health` - Health check endpoint

### Frontend (http://localhost:5173)
- 🎨 Beautiful dark mode UI
- 💳 Credit card components
- 📊 Spending stats
- ✨ AI insights
- 📱 Bottom navigation

---

## 🛑 Stop the App

Press `Ctrl + C` in both terminals

Or use:
```bash
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend
```

---

## 💡 Pro Tips

1. **Keep terminals open** - You need both running simultaneously
2. **Backend first** - Start backend before frontend
3. **Check logs** - If something breaks, look at terminal output
4. **Hot reload enabled** - Changes auto-refresh (no restart needed)

---

## 🎉 Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] http://localhost:8000/health returns {"status": "healthy"}
- [ ] http://localhost:5173 shows dark mode UI
- [ ] No import errors in terminal

**If all checked ✅ - You're ready to go!**

---

Last Updated: 2025-02-15
