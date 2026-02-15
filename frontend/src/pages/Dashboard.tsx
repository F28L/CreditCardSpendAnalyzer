import { DollarSign, TrendingUp, TrendingDown, Sparkles, Calendar } from 'lucide-react'

// Sample credit card data
const sampleCards = [
  {
    id: 1,
    name: 'Chase Sapphire Reserve',
    lastFour: '4242',
    balance: 2847.52,
    gradient: 'from-blue-500 to-blue-700',
    icon: '💳',
  },
  {
    id: 2,
    name: 'American Express Gold',
    lastFour: '8392',
    balance: 1234.00,
    gradient: 'from-yellow-600 to-orange-600',
    icon: '🏆',
  },
  {
    id: 3,
    name: 'Capital One Venture',
    lastFour: '5678',
    balance: 567.89,
    gradient: 'from-red-500 to-pink-600',
    icon: '✈️',
  },
]

// Sample spending data
const spendingStats = [
  { category: 'Dining', amount: 856.23, trend: 'up', percentage: 12 },
  { category: 'Shopping', amount: 1203.45, trend: 'down', percentage: 8 },
  { category: 'Transportation', amount: 234.67, trend: 'up', percentage: 5 },
]

function Dashboard() {
  const totalSpending = sampleCards.reduce((sum, card) => sum + card.balance, 0)

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Quick Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="wallet-card">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-wallet-accent-green/20 flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-wallet-accent-green" />
            </div>
            <div>
              <p className="text-wallet-text-secondary text-sm">Total Spent</p>
              <p className="text-2xl font-bold text-wallet-text-primary">
                ${totalSpending.toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="wallet-card">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-wallet-accent-purple/20 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-wallet-accent-purple" />
            </div>
            <div>
              <p className="text-wallet-text-secondary text-sm">AI Insights</p>
              <p className="text-2xl font-bold text-wallet-text-primary">3</p>
            </div>
          </div>
        </div>
      </div>

      {/* Cards Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-wallet-text-primary">Your Cards</h2>
          <span className="text-sm text-wallet-text-secondary">{sampleCards.length} cards</span>
        </div>

        <div className="space-y-4">
          {sampleCards.map((card) => (
            <div
              key={card.id}
              className={`credit-card bg-gradient-to-br ${card.gradient} hover:scale-[1.02] transition-transform duration-300 cursor-pointer`}
            >
              <div className="relative z-10">
                <div className="flex justify-between items-start mb-8">
                  <span className="text-4xl">{card.icon}</span>
                  <div className="text-right">
                    <p className="text-white/70 text-xs">Balance</p>
                    <p className="text-white text-2xl font-bold">${card.balance.toFixed(2)}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <p className="text-white font-semibold text-lg">{card.name}</p>
                  <div className="flex items-center space-x-4">
                    <span className="text-white/70 text-sm">•••• {card.lastFour}</span>
                    <span className="text-white/50 text-xs">Last 30 days</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <button className="w-full py-4 rounded-xl bg-wallet-surfaceElevated text-wallet-accent-blue font-semibold hover:bg-wallet-accent-blue/10 transition-all duration-200 border border-wallet-border">
          + Add New Card
        </button>
      </div>

      {/* Spending Breakdown */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-wallet-text-primary">Top Spending</h2>
          <button className="text-sm text-wallet-accent-blue hover:underline">View All</button>
        </div>

        <div className="space-y-3">
          {spendingStats.map((stat) => (
            <div key={stat.category} className="wallet-card-elevated">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-wallet-text-primary font-semibold">{stat.category}</span>
                    {stat.trend === 'up' ? (
                      <TrendingUp className="w-4 h-4 text-wallet-accent-red" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-wallet-accent-green" />
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 h-2 bg-wallet-bg rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          stat.trend === 'up' ? 'bg-wallet-accent-red' : 'bg-wallet-accent-green'
                        }`}
                        style={{ width: `${stat.percentage * 8}%` }}
                      />
                    </div>
                    <span className="text-wallet-text-secondary text-xs">
                      {stat.trend === 'up' ? '+' : '-'}{stat.percentage}%
                    </span>
                  </div>
                </div>
                <div className="text-right ml-4">
                  <p className="text-wallet-text-primary font-bold">${stat.amount.toFixed(2)}</p>
                  <p className="text-wallet-text-tertiary text-xs">This month</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Insight Card */}
      <div className="wallet-card bg-gradient-to-br from-wallet-accent-purple/20 to-wallet-accent-pink/20 border border-wallet-accent-purple/30">
        <div className="flex items-start space-x-4">
          <div className="w-10 h-10 rounded-full bg-wallet-accent-purple/30 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-5 h-5 text-wallet-accent-purple" />
          </div>
          <div className="flex-1">
            <h3 className="text-wallet-text-primary font-semibold mb-2">AI Insight</h3>
            <p className="text-wallet-text-secondary text-sm leading-relaxed">
              Your dining expenses increased by 23% this month. Consider setting a budget alert
              to track this category more closely.
            </p>
            <button className="mt-3 text-wallet-accent-purple text-sm font-semibold hover:underline">
              Learn more →
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-wallet-text-primary">Recent Activity</h2>
          <Calendar className="w-5 h-5 text-wallet-text-secondary" />
        </div>

        <div className="space-y-2">
          {['Starbucks', 'Uber', 'Amazon', 'Target'].map((merchant, idx) => (
            <div key={idx} className="wallet-card-elevated flex items-center justify-between py-4">
              <div>
                <p className="text-wallet-text-primary font-medium">{merchant}</p>
                <p className="text-wallet-text-tertiary text-xs">Today, {12 - idx * 2}:30 PM</p>
              </div>
              <p className="text-wallet-text-primary font-bold">-${(Math.random() * 50 + 5).toFixed(2)}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
