import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Wallet, TrendingUp, CreditCard, Sparkles, Home, LogOut } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Register from './pages/Register'
import ProtectedRoute from './components/ProtectedRoute'
import PlaidLinkButton from './components/PlaidLink'
import { AuthProvider, useAuth } from './contexts/AuthContext'

function Navigation() {
  const location = useLocation()
  const { isAuthenticated } = useAuth()

  // Don't show navigation on auth pages
  if (!isAuthenticated) {
    return null
  }

  const navItems = [
    { path: '/', icon: Home, label: 'Home' },
    { path: '/cards', icon: CreditCard, label: 'Cards' },
    { path: '/insights', icon: Sparkles, label: 'Insights' },
    { path: '/analytics', icon: TrendingUp, label: 'Analytics' },
  ]

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-wallet-surface border-t border-wallet-border glass z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-around items-center h-20">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center justify-center space-y-1 px-4 py-2 rounded-xl transition-all duration-200 ${
                  isActive
                    ? 'text-wallet-accent-blue'
                    : 'text-wallet-text-secondary hover:text-wallet-text-primary'
                }`}
              >
                <Icon className={`w-6 h-6 ${isActive ? 'animate-pulse-slow' : ''}`} />
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}

function Header() {
  const { user, logout, isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return null
  }

  const handlePlaidSuccess = () => {
    // Optionally refresh accounts or show a success message
    console.log('Bank account connected successfully!')
    // You can add a toast notification here
  }

  return (
    <header className="sticky top-0 z-40 bg-wallet-surface/80 backdrop-blur-wallet border-b border-wallet-border">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-wallet-accent-blue to-wallet-accent-purple flex items-center justify-center shadow-glow-blue">
              <Wallet className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-wallet-text-primary">Finance AI</h1>
              <p className="text-xs text-wallet-text-secondary">
                {user?.full_name || user?.username}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <PlaidLinkButton onSuccess={handlePlaidSuccess} />
            <button
              onClick={logout}
              className="p-2 rounded-xl bg-wallet-surfaceElevated text-wallet-text-secondary hover:text-wallet-text-primary hover:bg-wallet-border transition-all duration-200"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

function AppContent() {
  return (
    <div className="min-h-screen bg-wallet-bg pb-24">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cards"
            element={
              <ProtectedRoute>
                <div className="text-center py-20 text-wallet-text-secondary">
                  Cards page coming soon...
                </div>
              </ProtectedRoute>
            }
          />
          <Route
            path="/insights"
            element={
              <ProtectedRoute>
                <div className="text-center py-20 text-wallet-text-secondary">
                  Insights page coming soon...
                </div>
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <div className="text-center py-20 text-wallet-text-secondary">
                  Analytics page coming soon...
                </div>
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>

      {/* Bottom Navigation */}
      <Navigation />
    </div>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  )
}

export default App
