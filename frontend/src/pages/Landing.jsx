import React, { useEffect, useRef } from 'react'
import Nav from '../components/Nav'
import { Link } from 'react-router-dom'

export default function Landing() {
  const chatRef = useRef(null)

  useEffect(() => {
    const onScroll = () => {
      const nav = document.querySelector('nav')
      if (!nav) return
      if (window.scrollY > 50) nav.classList.add('scrolled')
      else nav.classList.remove('scrolled')
    }
    window.addEventListener('scroll', onScroll)
    const t = setTimeout(() => {
      if (chatRef.current) chatRef.current.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' })
    }, 10000)
    return () => { window.removeEventListener('scroll', onScroll); clearTimeout(t) }
  }, [])

  return (
    <div className="font-sans text-slate-800 bg-white antialiased relative">
      <Nav />

      {/* HERO */}
      <section id="home" className="min-h-screen flex items-center w-full text-center relative overflow-hidden">
        <div className="hero-blob-container">
          <div className="blob blob-1"></div><div className="blob blob-2"></div>
          <div className="blob blob-3"></div><div className="blob blob-4"></div>
          <div className="blob blob-5"></div>
          <div className="hero-darken" aria-hidden="true"></div>
          <div className="light-sweep" aria-hidden="true"></div>
        </div>
        <div className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 text-brand-600 font-medium text-sm mb-6 border border-brand-100">
            <span className="flex h-2 w-2 rounded-full bg-brand-500 animate-pulse"></span>
            Secured by Setu Account Aggregator
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-slate-900 tracking-tight mb-6 leading-tight">
            Your Smart <br /><span className="gradient-text">Finance Copilot</span>
          </h1>
          <p className="text-lg md:text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            Aggregate all your bank accounts, get AI-driven insights, and take control of your money with FinSight. Smart decisions, every day.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap mb-8">
            <Link to="/signup" className="cta-btn bg-brand-600 hover:bg-brand-700 text-white px-10 py-4 rounded-full font-semibold text-lg transition-all shadow-xl shadow-brand-500/40 inline-block">Get Started Free</Link>
            <a href="#how-it-works" className="px-8 py-4 rounded-full font-semibold text-slate-700 border-2 border-slate-200 hover:border-brand-300 hover:text-brand-600 transition-all text-lg">See How It Works</a>
          </div>
          <div className="flex items-center justify-center gap-6 flex-wrap text-sm text-slate-500">
            {['RBI Compliant','Bank-grade Encryption','No Hidden Fees','Consent-First'].map(t => (
              <div key={t} className="flex items-center gap-1.5">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/></svg>
                <span className="font-medium">{t}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="py-24 bg-gradient-to-b from-white to-brand-50 border-t border-slate-100 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">How FinSight Works</h2>
            <p className="text-slate-600 max-w-2xl mx-auto">Four simple steps to financial clarity and control.</p>
          </div>
          <div className="relative steps-container">
            <div className="progress-line"></div>
            {[
              {icon:'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',title:'Create Account',desc:'Sign up in 30 seconds. No credit card needed.'},
              {icon:'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',title:'Secure Consent',desc:'Link your banks via Setu Account Aggregator with explicit consent.'},
              {icon:'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4',title:'Data Processing',desc:'We fetch and clean your transactions securely in real-time.'},
              {icon:'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',title:'AI Analysis',desc:'Our AI processes patterns and delivers intelligent insights.'},
            ].map(s => (
              <div key={s.title} className="step-item">
                <div className="step-icon w-20 h-20 mx-auto bg-gradient-to-br from-brand-50 to-brand-100 rounded-3xl flex items-center justify-center mb-6 border-2 border-brand-200 shadow-lg relative z-10">
                  <svg className="w-10 h-10 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={s.icon}/></svg>
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{s.title}</h3>
                <p className="step-description text-sm text-slate-600">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI CHAT */}
      <section className="py-24 bg-white border-t border-slate-100 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-6">Talk to your money. Literally.</h2>
              <p className="text-lg text-slate-600 mb-8 leading-relaxed">Your AI Financial Copilot understands your spending patterns and gives personalized advice instantly. No more confusion with numbers.</p>
              <ul className="space-y-4">
                {['Spot hidden subscriptions and recurring charges.','Get real-time savings recommendations.','Analyze multi-account spending patterns instantly.'].map(item => (
                  <li key={item} className="flex items-start gap-3">
                    <div className="w-6 h-6 mt-1 rounded-full bg-brand-100 flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"/></svg>
                    </div>
                    <span className="text-slate-700 font-medium">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden">
              <div className="bg-gradient-to-r from-slate-50 to-brand-50 border-b border-slate-100 px-6 py-4 flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                <div><p className="font-bold text-sm text-slate-900">FinSight AI</p><p className="text-xs text-brand-600">Online · Always here</p></div>
              </div>
              <div ref={chatRef} className="chat-container p-6 h-96 overflow-y-auto bg-gradient-to-b from-white to-brand-50/30">
                <div className="chat-message-wrapper user-message delay-1"><div className="message-bubble user-bubble">How much did I spend on food last month?</div></div>
                <div className="chat-message-wrapper bot-message delay-2"><div className="message-bubble bot-bubble"><p className="font-semibold text-brand-700 mb-1">🍔 Food & Dining</p><p className="text-sm">You spent <span className="font-bold text-brand-600">₹12,450</span> on food last month. That's 18% of your monthly budget.</p></div></div>
                <div className="chat-message-wrapper user-message delay-3"><div className="message-bubble user-bubble">Can I reduce that?</div></div>
                <div className="chat-message-wrapper bot-message delay-4"><div className="message-bubble bot-bubble"><p className="font-semibold text-brand-700 mb-1">💡 Smart Suggestions</p><p className="text-sm mb-2">• Cut dining out by 30% = ₹3,735 saved<br/>• Meal prep 2 days a week = ₹2,000 saved<br/>• Skip 1 coffee/day = ₹1,500 saved</p><p className="text-xs text-brand-600 font-medium">Total potential savings: ₹7,235/month!</p></div></div>
                <div className="chat-message-wrapper user-message delay-5"><div className="message-bubble user-bubble">That sounds great! Set it up.</div></div>
                <div className="chat-message-wrapper bot-message delay-6"><div className="message-bubble bot-bubble">✅ Budget alerts set! I'll notify you when you reach 80% of your food budget.</div></div>
              </div>
              <div className="px-6 py-4 border-t border-slate-100 bg-slate-50 flex gap-2">
                <input type="text" placeholder="Ask anything about your finances..." className="flex-1 bg-white border border-slate-200 rounded-full px-4 py-2 text-sm text-slate-600 focus:outline-none focus:border-brand-400 transition-colors" readOnly/>
                <button className="w-10 h-10 rounded-full bg-brand-600 flex items-center justify-center flex-shrink-0 cursor-default shadow-md">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className="py-24 bg-gradient-to-b from-white to-slate-50 border-t border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">Powerful Features, Simple Control</h2>
            <p className="text-slate-600 max-w-2xl mx-auto text-lg">Everything you need to understand, manage, and grow your money intelligently.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {icon:'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4',title:'Link All Banks',desc:'Secure connection to multiple accounts via RBI Account Aggregator — read-only, encrypted, and consent-based.',badge:<span className="inline-block px-3 py-1 text-xs font-semibold text-brand-600 bg-brand-50 rounded-full border border-brand-100">RBI AA Compliant</span>},
              {icon:'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01',title:'Smart Categorization',desc:'Automatic tagging of every transaction — groceries, bills, investments, travel — with 99.2% accuracy.',badge:<div className="text-sm text-brand-600 font-semibold">Accuracy 99.2%</div>},
              {icon:'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',title:'Priority Budgeting',desc:'Set meaningful spending limits across categories, get gentle alerts before overspending, and track your goals.',badge:<div className="text-sm text-brand-600 font-semibold">Smart Alerts Enabled</div>},
              {icon:'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',title:'EMI Calculator',desc:'Plan any loan — home, car, personal. Compare offers, calculate total interest and payoff timeline.',badge:<span className="inline-block px-3 py-1 text-xs font-semibold text-brand-600 bg-brand-50 rounded-full border border-brand-100">Financial Tools</span>},
              {icon:'M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z',title:'Receipt Scanner',desc:'Snap a photo of any receipt. AI extracts and categorizes the expense automatically — no manual entry needed.',badge:<span className="inline-block px-3 py-1 text-xs font-semibold text-brand-600 bg-brand-50 rounded-full border border-brand-100">OCR Powered</span>},
              {icon:'M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',title:'Investment Dashboard',desc:'Track equity portfolio, mutual funds, FDs, NPS and PPF in one place with real-time NAV updates.',badge:<div className="text-sm text-brand-600 font-semibold">Real-time NAV</div>},
            ].map(f => (
              <div key={f.title} className="feature-card bg-white rounded-2xl border border-slate-200 p-8 hover:border-brand-200 hover:shadow-lg transition-all">
                <div className="feature-icon mb-6 w-12 h-12 bg-brand-50 rounded-xl flex items-center justify-center">
                  <svg className="w-6 h-6 text-brand-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d={f.icon}/></svg>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{f.title}</h3>
                <p className="text-slate-600 mb-4">{f.desc}</p>
                {f.badge}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* SECURITY */}
      <section id="security" className="py-24 bg-white border-t border-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">Your Security is Our Priority</h2>
            <p className="text-slate-600 max-w-2xl mx-auto text-lg">Bank-grade encryption and strict compliance standards protect your financial data.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="security-card bg-gradient-to-br from-green-50/80 to-emerald-50/80 rounded-2xl border border-green-200 p-8">
              <div className="w-14 h-14 rounded-full bg-green-100 flex items-center justify-center mb-6"><svg className="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">RBI Regulated</h3>
              <p className="text-slate-700">Fully compliant with Reserve Bank of India's Account Aggregator framework and data protection standards.</p>
              <div className="mt-4 pt-4 border-t border-green-200"><span className="text-xs font-semibold text-green-700">✓ Certified & Verified</span></div>
            </div>
            <div className="security-card bg-gradient-to-br from-blue-50/80 to-cyan-50/80 rounded-2xl border border-blue-200 p-8">
              <div className="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center mb-6"><svg className="w-7 h-7 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg></div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">End-to-End Encryption</h3>
              <p className="text-slate-700">Military-grade AES-256 encryption combined with TLS 1.3 ensures your financial data remains private.</p>
              <div className="mt-4 pt-4 border-t border-blue-200"><span className="text-xs font-semibold text-blue-700">✓ ISO 27001 Certified</span></div>
            </div>
            <div className="security-card bg-gradient-to-br from-purple-50/80 to-violet-50/80 rounded-2xl border border-purple-200 p-8">
              <div className="w-14 h-14 rounded-full bg-purple-100 flex items-center justify-center mb-6"><svg className="w-7 h-7 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m7 0a9 9 0 11-18 0 9 9 0 0118 0z"/></svg></div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">Consent-Based Access</h3>
              <p className="text-slate-700">You remain in complete control. Every data access requires your explicit consent, revocable anytime.</p>
              <div className="mt-4 pt-4 border-t border-purple-200"><span className="text-xs font-semibold text-purple-700">✓ GDPR & CCPA Compliant</span></div>
            </div>
          </div>
          <div className="mt-16 bg-gradient-to-r from-brand-50 to-purple-50 rounded-2xl border border-brand-100 p-12">
            <h3 className="text-2xl font-bold text-slate-900 mb-8">Additional Safeguards</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {[['2FA Authentication','Two-factor authentication on all accounts.'],['Data Isolation','Strict data segmentation per user.'],['No Data Sharing','Never shared or sold to third parties.'],['Audit Logs','Complete transparency with audit trails.']].map(([title,desc]) => (
                <div key={title}>
                  <div className="flex items-center gap-3 mb-2">
                    <svg className="w-5 h-5 text-brand-600" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/></svg>
                    <h4 className="font-bold text-slate-900">{title}</h4>
                  </div>
                  <p className="text-sm text-slate-600">{desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className="py-32 bg-gradient-to-b from-white to-brand-50 border-t border-slate-100 relative overflow-hidden">
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-brand-200 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-pulse"></div>
          <div className="absolute top-0 right-1/4 w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-10"></div>
        </div>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6 leading-tight">Take Control of Your Money Today</h2>
          <p className="text-xl text-slate-600 mb-12 max-w-2xl mx-auto leading-relaxed">Join thousands of smart Indians who are already using FinSight to understand, manage, and grow their wealth with AI-powered insights.</p>
          <div className="flex justify-center gap-4 flex-wrap mb-16">
            <Link to="/signup" className="cta-btn bg-brand-600 hover:bg-brand-700 text-white px-12 py-5 rounded-full font-semibold text-lg transition-all shadow-xl shadow-brand-500/40 inline-block">Signup Now</Link>
            <Link to="/signin" className="px-10 py-5 rounded-full font-semibold text-slate-700 border-2 border-slate-200 hover:border-brand-300 hover:text-brand-600 transition-all text-lg inline-block">Sign In</Link>
          </div>
          <div className="inline-flex flex-wrap justify-center gap-8 pt-8 border-t border-slate-200">
            {['RBI Compliant','End-to-End Encryption','No Hidden Fees'].map(t => (
              <div key={t} className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/></svg>
                <span className="font-semibold text-slate-700">{t}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-slate-900 text-white py-8 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-slate-400 text-sm">© 2026 FinSight. All rights reserved. Your Finance Copilot.</p>
        </div>
      </footer>
    </div>
  )
}