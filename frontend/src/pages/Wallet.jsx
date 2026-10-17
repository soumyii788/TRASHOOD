import { useEffect, useState } from 'react'
import { getBalance, getTransactions } from '../api/services'
import './Page.css'

export default function Wallet() {
  const [balance, setBalance] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getBalance(), getTransactions()])
      .then(([balRes, txRes]) => {
        setBalance(balRes.data.balance)
        setTransactions(txRes.data.results || txRes.data)
      })
      .catch(() => setError('Failed to load wallet data. Please try again.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page">
      <h2 className="page-heading">💰 Wallet</h2>
      <p className="page-subtitle">Your earnings from scrap pickups.</p>

      {/* Loading */}
      {loading && (
        <div className="state-box">
          <div className="spinner" />
          <span>Loading wallet…</span>
        </div>
      )}

      {/* Error */}
      {!loading && error && <div className="error-banner">{error}</div>}

      {!loading && !error && (
        <>
          <div className="balance-card">
            <span>Total Balance</span>
            <h1>₹{parseFloat(balance || 0).toFixed(2)}</h1>
            <p style={{ opacity: 0.7, fontSize: '0.8rem', marginTop: '0.5rem' }}>
              Credits from completed scrap pickups
            </p>
          </div>

          <h3 style={{ marginTop: '2rem', marginBottom: '1rem', color: '#111', fontSize: '1.1rem' }}>
            Transaction History
          </h3>

          {transactions.length === 0 ? (
            <div className="state-box" style={{ padding: '3rem 1rem' }}>
              <span className="state-icon">📄</span>
              <span>No transactions yet.</span>
              <p style={{ fontSize: '0.85rem', color: '#aaa', margin: 0 }}>
                Complete a scrap pickup to earn wallet credits.
              </p>
            </div>
          ) : (
            <table className="txn-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((t) => (
                  <tr key={t.id}>
                    <td>{new Date(t.created_at).toLocaleDateString('en-IN', { dateStyle: 'medium' })}</td>
                    <td><span className={`badge ${t.txn_type.toLowerCase()}`}>{t.txn_type}</span></td>
                    <td><strong>₹{parseFloat(t.amount).toFixed(2)}</strong></td>
                    <td><span className={`badge ${t.status.toLowerCase()}`}>{t.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}
    </div>
  )
}
