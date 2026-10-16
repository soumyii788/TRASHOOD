import { useEffect, useState } from 'react'
import { getBalance, getTransactions } from '../api/services'
import './Page.css'

export default function Wallet() {
  const [balance, setBalance] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getBalance(), getTransactions()])
      .then(([balRes, txRes]) => {
        setBalance(balRes.data.balance)
        setTransactions(txRes.data.results || txRes.data)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page">
      <h2>💰 Wallet</h2>
      {loading ? <p>Loading…</p> : (
        <>
          <div className="balance-card">
            <span>Total Balance</span>
            <h1>₹{parseFloat(balance || 0).toFixed(2)}</h1>
          </div>

          <h3 style={{ marginTop: '2rem' }}>Transaction History</h3>
          {transactions.length === 0 ? <p>No transactions yet.</p> : (
            <table className="txn-table">
              <thead>
                <tr><th>Date</th><th>Type</th><th>Amount</th><th>Status</th></tr>
              </thead>
              <tbody>
                {transactions.map((t) => (
                  <tr key={t.id}>
                    <td>{new Date(t.created_at).toLocaleDateString()}</td>
                    <td><span className={`badge ${t.txn_type.toLowerCase()}`}>{t.txn_type}</span></td>
                    <td>₹{t.amount}</td>
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
