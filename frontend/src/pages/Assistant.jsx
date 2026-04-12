import React, { useState, useEffect, useRef, useMemo } from 'react'
import DashboardLayout from '../components/DashboardLayout'
import { useAuth } from '../context/AuthContext'
import { pennyAPI } from '../services/api'

const SUGGESTIONS = [
  "Give me a summary of my finances",
  "Which category am I spending the most on?",
  "How can I save more based on my spending?",
  "Compare my income vs expenses",
  "What's my biggest expense this period?",
  "Give me a budget plan based on my data",
  "Which transactions look unusual?",
  "How close am I to the 50/30/20 rule?",
]

const insightColors = {
  warning:  { bg: 'bg-orange-50', border: 'border-orange-200', icon: '⚠️', text: 'text-orange-700' },
  tip:      { bg: 'bg-blue-50',   border: 'border-blue-200',   icon: '💡', text: 'text-blue-700'   },
  positive: { bg: 'bg-green-50',  border: 'border-green-200',  icon: '✅', text: 'text-green-700'  },
  saving:   { bg: 'bg-purple-50', border: 'border-purple-200', icon: '💰', text: 'text-purple-700' },
}

function PennyAvatar({ size = 'md' }) {
  const s = size === 'sm' ? 'w-7 h-7 text-sm' : 'w-10 h-10 text-base'
  return (
    <div className={`${s} rounded-full bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center font-bold text-white flex-shrink-0 shadow-md`}>
      P
    </div>
  )
}

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {!isUser && <PennyAvatar size="sm" />}
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
        isUser
          ? 'bg-brand-600 text-white rounded-tr-sm'
          : 'bg-slate-100 text-slate-800 rounded-tl-sm'
      }`}>
        {msg.content.split('\n').map((line, i) => (
          <p key={i} className={line === '' ? 'h-2' : ''}>{line}</p>
        ))}
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <PennyAvatar size="sm" />
      <div className="bg-slate-100 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
        {[0,1,2].map(i => (
          <div key={i} className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}/>
        ))}
      </div>
    </div>
  )
}

export default function Assistant() {
  const { user } = useAuth()
  const [messages, setMessages]     = useState([])
  const [input, setInput]           = useState('')
  const [sending, setSending]       = useState(false)
  const [insights, setInsights]     = useState([])
  const [insightsLoading, setInsightsLoading] = useState(true)
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

  // Load initial insights
  useEffect(() => {
    if (!user) return
    setInsightsLoading(true)
    pennyAPI.getInsights()
      .then(({ data }) => setInsights(data.insights ?? []))
      .catch(() => setInsights([]))
      .finally(() => setInsightsLoading(false))

    // Welcome message
    setMessages([{
      role:    'assistant',
      content: `Hi ${user.full_name?.split(' ')[0] || 'there'}! 👋 I'm Penny, your personal finance assistant.\n\nI've analysed your accounts and transactions. Ask me anything — from spending patterns to budget advice, or just say "Give me a summary"!`,
    }])
  }, [user?.id])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const sendMessage = async (text) => {
    const q = (text || input).trim()
    if (!q || sending) return
    setInput('')
    setSending(true)

    const userMsg = { role: 'user', content: q }
    setMessages(prev => [...prev, userMsg])

    try {
      const { data } = await pennyAPI.chat({
        messages: messages.slice(-10),
        question: q,
      })
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Sorry, I'm having trouble connecting right now. Please try again in a moment."
      }])
    } finally {
      setSending(false)
      inputRef.current?.focus()
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  }

  return (
    <DashboardLayout title="Penny — AI Assistant">
      <div className="max-w-6xl mx-auto h-[calc(100vh-10rem)] flex gap-6">

        {/* ── Left: Insights panel ── */}
        <div className="w-72 flex-shrink-0 hidden lg:flex flex-col gap-4">

          <div className="bg-gradient-to-br from-brand-600 to-purple-700 rounded-2xl p-5 text-white">
            <div className="flex items-center gap-3 mb-3">
              <PennyAvatar />
              <div>
                <p className="font-bold text-base">Penny</p>
                <p className="text-xs text-white/70">Your Finance Copilot</p>
              </div>
            </div>
            <p className="text-xs text-white/80 leading-relaxed">
              I know your transactions, accounts and spending patterns. Ask me anything!
            </p>
          </div>

          {/* Proactive insights */}
          <div className="flex-1 overflow-y-auto space-y-3">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Your Insights</p>
            {insightsLoading ? (
              <div className="space-y-2">
                {[1,2,3].map(i => (
                  <div key={i} className="h-16 bg-slate-100 rounded-xl animate-pulse"/>
                ))}
              </div>
            ) : insights.map((ins, i) => {
              const style = insightColors[ins.type] ?? insightColors.tip
              return (
                <div key={i} className={`${style.bg} ${style.border} border rounded-xl p-3`}>
                  <p className={`text-xs font-semibold ${style.text} mb-1`}>
                    {style.icon} {ins.title}
                  </p>
                  <p className="text-xs text-slate-600 leading-relaxed">{ins.message}</p>
                  <button
                    onClick={() => sendMessage(`Tell me more about: ${ins.title}`)}
                    className="mt-2 text-xs text-brand-600 hover:underline"
                  >
                    Ask Penny →
                  </button>
                </div>
              )
            })}
          </div>
        </div>

        {/* ── Right: Chat window ── */}
        <div className="flex-1 flex flex-col border border-slate-200 rounded-2xl overflow-hidden bg-white shadow-sm">

          {/* Chat header */}
          <div className="flex items-center gap-3 px-5 py-4 border-b border-slate-100 bg-slate-50">
            <PennyAvatar />
            <div>
              <p className="font-semibold text-slate-900 text-sm">Penny</p>
              <p className="text-xs text-green-500">● Online · Analysing your data</p>
            </div>
            <div className="ml-auto flex gap-2">
              <button
                onClick={() => setMessages([{
                  role: 'assistant',
                  content: `Hi again ${user?.full_name?.split(' ')[0]}! Fresh start — what would you like to know?`
                }])}
                className="text-xs text-slate-400 hover:text-slate-600 px-2 py-1 rounded-lg hover:bg-slate-100"
              >
                Clear chat
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
            {messages.map((msg, i) => <Message key={i} msg={msg} />)}
            {sending && <TypingIndicator />}
            <div ref={bottomRef}/>
          </div>

          {/* Quick suggestions */}
          {messages.length <= 1 && (
            <div className="px-5 py-2 border-t border-slate-50">
              <p className="text-xs text-slate-400 mb-2">Try asking:</p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTIONS.slice(0, 4).map(s => (
                  <button key={s} onClick={() => sendMessage(s)}
                    className="text-xs px-3 py-1.5 bg-brand-50 text-brand-700 border border-brand-200 rounded-full hover:bg-brand-100 transition-colors">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="px-4 py-3 border-t border-slate-200 bg-white">
            <div className="flex items-end gap-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                placeholder="Ask Penny anything about your finances..."
                rows={1}
                className="flex-1 resize-none border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent max-h-32 overflow-y-auto"
                style={{ minHeight: '42px' }}
              />
              <button
                onClick={() => sendMessage()}
                disabled={!input.trim() || sending}
                className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all ${
                  input.trim() && !sending
                    ? 'bg-brand-600 hover:bg-brand-700 text-white shadow-sm'
                    : 'bg-slate-100 text-slate-300 cursor-not-allowed'
                }`}
              >
                {sending ? (
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                  </svg>
                )}
              </button>
            </div>
            <p className="text-xs text-slate-400 mt-1.5 text-center">
              Penny uses your actual transaction data · Press Enter to send
            </p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
