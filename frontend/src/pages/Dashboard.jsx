import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import DashboardLayout from '../components/DashboardLayout'
import { useAuth } from '../context/AuthContext'

export default function Dashboard() {
  const [accountFilter, setAccountFilter] = useState('All Accounts (Consolidated)')
  const { user } = useAuth()

  return (
    <DashboardLayout
      title="Dashboard"
      rightElement={
        <div className="relative">
          <select
            value={accountFilter}
            onChange={e => setAccountFilter(e.target.value)}
            className="px-4 py-2 border rounded-md border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option>All Accounts (Consolidated)</option>
            <option>Bank of India • 1234</option>
            <option>HDFC • 5678</option>
          </select>
        </div>
      }
    >
      <section className="max-w-4xl mx-auto">
        <div className="border border-dashed border-slate-200 rounded-xl p-12 text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 rounded-2xl bg-brand-50 border border-brand-100 flex items-center justify-center">
              <svg className="w-8 h-8 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
              </svg>
            </div>
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-2">No User Consents Created</h3>
          <p className="text-sm text-slate-500 mb-6 max-w-sm mx-auto">
            Create a consent to start viewing your financial data and transactions.
          </p>
          <Link
            to="/consent"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-brand-500 to-brand-700 text-white font-medium shadow-md hover:shadow-lg hover:shadow-brand-500/30 transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"/>
            </svg>
            Go to Consent Management
          </Link>

          {/* User info strip */}
          <div className="mt-8 pt-6 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left max-w-xl mx-auto">
            {[
              ['Account',   user?.email ?? '—'],
              ['Mobile',    user?.mobile ?? '—'],
              ['AA Status', user?.aa_consent_status ?? 'Not linked'],
            ].map(([label, val]) => (
              <div key={label} className="bg-slate-50 rounded-lg px-4 py-3">
                <p className="text-xs text-slate-400 mb-0.5">{label}</p>
                <p className="text-sm font-medium text-slate-700 truncate">{val}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </DashboardLayout>
  )
}