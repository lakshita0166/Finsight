import React, { useState, useEffect } from 'react'
import DashboardLayout from '../components/DashboardLayout'
import { goalsAPI, aaAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

const CATEGORY_ICONS = {
  'Food & Dining': '🍴',
  'Transportation': '🚗',
  'Shopping & Retail': '🛒',
  'Bills & Utilities': '🧾',
  'Housing & Rent': '🏠',
  'Healthcare & Medical': '🏥',
  'Entertainment & Leisure': '🍿',
  'Travel': '✈️',
  'Education': '🎓',
  'Investments & Savings': '💰',
  'Insurance': '🛡️',
  'Salary & Income': '💵',
  'Transfers': '🔄',
  'Taxes & Government': '🏛️',
  'ATM / Cash Withdrawal': '🏧',
  'Fees & Charges': '⚠️',
  'Donations & Charity': '🎗️',
  'Business / Professional Expenses': '💼',
  'Subscription Services': '🔄',
  'Uncategorized / Unknown': '🔹',
}

const fmt = (n) => '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })

export default function Goals() {
  const { user } = useAuth()
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)
  const [categories, setCategories] = useState([])
  const [accounts, setAccounts] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [newGoal, setNewGoal] = useState({
    goal_type: 'SPENDING_LIMIT',
    category: 'Food & Dining',
    title: '',
    fi_data_id: '',
    target_amount: '',
    period: 'MONTHLY',
    start_month: new Date().getMonth() + 1,
    start_year: new Date().getFullYear(),
    end_month: new Date().getMonth() + 1,
    end_year: new Date().getFullYear()
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const gRes = await goalsAPI.getGoals()
      setGoals(gRes.data.goals)
      const cRes = await aaAPI.getCategories()
      setCategories(cRes.data.categories || Object.keys(CATEGORY_ICONS))
      const fRes = await aaAPI.getFIData()
      setAccounts(fRes.data.accounts || [])
    } catch (e) {
      console.error('Failed to load goals:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    try {
      await goalsAPI.createGoal(newGoal)
      setShowModal(false)
      loadData()
    } catch (e) {
      alert('Failed to create goal')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this goal?')) return
    try {
      await goalsAPI.deleteGoal(id)
      loadData()
    } catch (e) {
      alert('Failed to delete goal')
    }
  }

  return (
    <DashboardLayout title="Goals & Budgets">
      <div className="max-w-6xl mx-auto space-y-8">
        
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-black text-slate-800 tracking-tight">Financial Targets</h2>
            <p className="text-sm text-slate-500 font-medium">Set limits and track your savings goals in real-time.</p>
          </div>
          <button 
            onClick={() => setShowModal(true)}
            className="bg-brand-600 hover:bg-brand-700 text-white font-bold py-2.5 px-6 rounded-xl shadow-lg shadow-brand-200 transition-all flex items-center gap-2"
          >
            <span className="text-xl">+</span> Add Goal
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <svg className="animate-spin h-8 w-8 text-brand-500" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {goals.map(goal => (
              <div key={goal.id} className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm relative group">
                <button 
                  onClick={() => handleDelete(goal.id)}
                  className="absolute top-4 right-4 text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                </button>

                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-2xl bg-slate-50 flex items-center justify-center text-2xl">
                    {goal.goal_type === 'SAVINGS_GOAL' ? '💰' : (CATEGORY_ICONS[goal.category] || '🔹')}
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-800 leading-none mb-1">
                      {goal.title || (goal.goal_type === 'SAVINGS_GOAL' ? 'Savings Target' : goal.category)}
                    </h4>
                    <div className="flex flex-col gap-0.5">
                      <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">
                        {goal.goal_type === 'SAVINGS_GOAL' ? 'Savings Goal' : goal.category} • {goal.period}
                      </p>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {goal.fi_data_id && (
                          <span className="text-[9px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-bold">
                            Account: {accounts.find(a => a.fi_data_id === goal.fi_data_id)?.masked_acc_number || 'Linked Account'}
                          </span>
                        )}
                        {goal.period === 'RANGE' && goal.timeframe && (
                          <span className="text-[9px] bg-brand-50 text-brand-600 px-1.5 py-0.5 rounded font-bold">
                            {new Date(2000, goal.timeframe.start_month-1).toLocaleString('default', { month: 'short' })} {goal.timeframe.start_year} - {new Date(2000, goal.timeframe.end_month-1).toLocaleString('default', { month: 'short' })} {goal.timeframe.end_year}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between items-end">
                    <div>
                      <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mb-1">Current</p>
                      <p className="text-lg font-black text-slate-800">{fmt(goal.current_amount)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[10px] uppercase tracking-widest text-slate-400 font-bold mb-1">Target</p>
                      <p className="text-lg font-black text-brand-600">{fmt(goal.target_amount)}</p>
                    </div>
                  </div>

                  <div className="relative">
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full transition-all duration-1000 ${goal.progress_percentage > 100 ? 'bg-red-500' : 'bg-brand-500'}`}
                        style={{ width: `${Math.min(100, goal.progress_percentage)}%` }}
                      ></div>
                    </div>
                    {goal.progress_percentage > 90 && (
                      <p className={`text-[10px] font-bold mt-2 ${goal.progress_percentage > 100 ? 'text-red-500' : 'text-amber-500'}`}>
                        {goal.progress_percentage > 100 ? '⚠️ Limit Exceeded' : '⚠️ Near Limit'}
                      </p>
                    )}
                  </div>

                  <p className="text-xs text-slate-500 font-medium">
                    {goal.goal_type === 'SAVINGS_GOAL' 
                      ? `${fmt(goal.target_amount - goal.current_amount)} more to reach your goal.`
                      : goal.progress_percentage > 100 
                        ? `You are ${fmt(goal.current_amount - goal.target_amount)} over your budget.`
                        : `${fmt(goal.target_amount - goal.current_amount)} remaining in this category.`}
                  </p>
                </div>
              </div>
            ))}

            {goals.length === 0 && (
              <div className="col-span-full py-20 bg-slate-50 rounded-3xl border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-center">
                <div className="text-4xl mb-4">🎯</div>
                <h3 className="text-lg font-bold text-slate-800">No goals set yet</h3>
                <p className="text-sm text-slate-500 max-w-xs mb-6">Start by setting a monthly spending limit or a yearly savings target.</p>
                <button 
                  onClick={() => setShowModal(true)}
                  className="text-brand-600 font-bold hover:underline"
                >
                  Create your first goal →
                </button>
              </div>
            )}
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white w-full max-w-md rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
              <div className="p-8">
                <h3 className="text-xl font-black text-slate-800 mb-2">Create New Goal</h3>
                <p className="text-sm text-slate-500 mb-6">Define your target and we'll track it automatically.</p>
                
                <form onSubmit={handleCreate} className="space-y-4">
                  <div>
                    <label className="block text-[10px] uppercase tracking-widest text-slate-400 font-black mb-1.5">Goal Type</label>
                    <div className="grid grid-cols-2 gap-2">
                      <button 
                        type="button"
                        onClick={() => setNewGoal({ ...newGoal, goal_type: 'SPENDING_LIMIT', period: 'MONTHLY' })}
                        className={`py-3 px-4 rounded-xl text-xs font-bold border-2 transition-all ${newGoal.goal_type === 'SPENDING_LIMIT' ? 'border-brand-500 bg-brand-50 text-brand-600' : 'border-slate-100 text-slate-500 hover:border-slate-200'}`}
                      >
                        Spending Limit
                      </button>
                      <button 
                        type="button"
                        onClick={() => setNewGoal({ ...newGoal, goal_type: 'SAVINGS_GOAL', category: null })}
                        className={`py-3 px-4 rounded-xl text-xs font-bold border-2 transition-all ${newGoal.goal_type === 'SAVINGS_GOAL' ? 'border-brand-500 bg-brand-50 text-brand-600' : 'border-slate-100 text-slate-500 hover:border-slate-200'}`}
                      >
                        Savings Target
                      </button>
                    </div>
                  </div>

                  {newGoal.goal_type === 'SAVINGS_GOAL' && (
                    <div>
                      <label className="block text-[10px] uppercase tracking-widest text-slate-400 font-black mb-1.5">Track Account</label>
                      <select 
                        value={newGoal.fi_data_id}
                        onChange={(e) => setNewGoal({ ...newGoal, fi_data_id: e.target.value })}
                        className="w-full bg-slate-50 border-none rounded-xl px-4 py-3 text-sm font-bold text-slate-700 outline-none focus:ring-2 focus:ring-brand-500"
                      >
                        <option value="">Consolidated (All Accounts)</option>
                        {accounts.map(acc => (
                          <option key={acc.fi_data_id} value={acc.fi_data_id}>
                            {acc.masked_acc_number} ({acc.account_type})
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {newGoal.goal_type === 'SAVINGS_GOAL' && (
                    <div>
                      <label className="block text-[10px] uppercase tracking-widest text-slate-400 font-black mb-1.5">Period Type</label>
                      <div className="grid grid-cols-2 gap-2">
                        <button 
                          type="button"
                          onClick={() => setNewGoal({ ...newGoal, period: 'MONTHLY' })}
                          className={`py-2 px-3 rounded-lg text-xs font-bold border ${newGoal.period === 'MONTHLY' ? 'bg-brand-500 text-white border-brand-500' : 'bg-slate-50 text-slate-500 border-slate-100'}`}
                        >
                          Single Month
                        </button>
                        <button 
                          type="button"
                          onClick={() => setNewGoal({ ...newGoal, period: 'RANGE' })}
                          className={`py-2 px-3 rounded-lg text-xs font-bold border ${newGoal.period === 'RANGE' ? 'bg-brand-500 text-white border-brand-500' : 'bg-slate-50 text-slate-500 border-slate-100'}`}
                        >
                          Custom Range
                        </button>
                      </div>
                    </div>
                  )}

                  {newGoal.goal_type === 'SAVINGS_GOAL' && newGoal.period === 'RANGE' && (
                    <div className="bg-slate-50 p-4 rounded-2xl space-y-4 border border-slate-100">
                      <div>
                        <label className="block text-[9px] uppercase tracking-widest text-slate-400 font-black mb-1">Start Month</label>
                        <div className="grid grid-cols-2 gap-2">
                          <select 
                            value={newGoal.start_month}
                            onChange={(e) => setNewGoal({ ...newGoal, start_month: parseInt(e.target.value) })}
                            className="bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs font-bold"
                          >
                            {Array.from({length: 12}, (_, i) => (
                              <option key={i+1} value={i+1}>{new Date(2000, i).toLocaleString('default', { month: 'short' })}</option>
                            ))}
                          </select>
                          <select 
                            value={newGoal.start_year}
                            onChange={(e) => setNewGoal({ ...newGoal, start_year: parseInt(e.target.value) })}
                            className="bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs font-bold"
                          >
                            {[2024, 2025, 2026].map(y => <option key={y} value={y}>{y}</option>)}
                          </select>
                        </div>
                      </div>
                      <div>
                        <label className="block text-[9px] uppercase tracking-widest text-slate-400 font-black mb-1">End Month</label>
                        <div className="grid grid-cols-2 gap-2">
                          <select 
                            value={newGoal.end_month}
                            onChange={(e) => setNewGoal({ ...newGoal, end_month: parseInt(e.target.value) })}
                            className="bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs font-bold"
                          >
                            {Array.from({length: 12}, (_, i) => (
                              <option key={i+1} value={i+1}>{new Date(2000, i).toLocaleString('default', { month: 'short' })}</option>
                            ))}
                          </select>
                          <select 
                            value={newGoal.end_year}
                            onChange={(e) => setNewGoal({ ...newGoal, end_year: parseInt(e.target.value) })}
                            className="bg-white border border-slate-200 rounded-lg px-2 py-1.5 text-xs font-bold"
                          >
                            {[2024, 2025, 2026].map(y => <option key={y} value={y}>{y}</option>)}
                          </select>
                        </div>
                      </div>
                    </div>
                  )}

                  <div>
                    <label className="block text-[10px] uppercase tracking-widest text-slate-400 font-black mb-1.5">Goal Title (Optional)</label>
                    <input 
                      type="text"
                      placeholder={newGoal.goal_type === 'SAVINGS_GOAL' ? "e.g. New iPhone, Vacation" : "e.g. Monthly Dining Out"}
                      value={newGoal.title}
                      onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
                      className="w-full bg-slate-50 border-none rounded-xl px-4 py-3 text-sm font-bold text-slate-700 outline-none focus:ring-2 focus:ring-brand-500 placeholder:text-slate-300"
                    />
                  </div>

                  {newGoal.goal_type === 'SPENDING_LIMIT' && (
                    <div>
                      <label className="block text-[10px] uppercase tracking-widest text-slate-400 font-black mb-1.5">Category</label>
                      <select 
                        value={newGoal.category}
                        onChange={(e) => setNewGoal({ ...newGoal, category: e.target.value })}
                        className="w-full bg-slate-50 border-none rounded-xl px-4 py-3 text-sm font-bold text-slate-700 outline-none focus:ring-2 focus:ring-brand-500"
                      >
                        {categories.map(c => <option key={c} value={c}>{c}</option>)}
                      </select>
                    </div>
                  )}

                  <div>
                    <label className="block text-[10px] uppercase tracking-widest text-slate-400 font-black mb-1.5">Target Amount (₹)</label>
                    <input 
                      type="number"
                      required
                      placeholder="e.g. 10000"
                      value={newGoal.target_amount}
                      onChange={(e) => setNewGoal({ ...newGoal, target_amount: e.target.value })}
                      className="w-full bg-slate-50 border-none rounded-xl px-4 py-3 text-sm font-bold text-slate-700 outline-none focus:ring-2 focus:ring-brand-500 placeholder:text-slate-300"
                    />
                  </div>

                  <div className="pt-4 flex gap-3">
                    <button 
                      type="button"
                      onClick={() => setShowModal(false)}
                      className="flex-1 py-3 text-sm font-bold text-slate-500 hover:text-slate-700"
                    >
                      Cancel
                    </button>
                    <button 
                      type="submit"
                      className="flex-2 bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 px-8 rounded-xl"
                    >
                      Set Goal
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

      </div>
    </DashboardLayout>
  )
}
