import { useEffect, useState } from 'react'
import { getProfile, getBalance, getPickupHistory } from '../api/services'
import './Page.css'

export default function Dashboard() {
  const [profile, setProfile] = useState(null)
  const [balance, setBalance] = useState(0)
  const [pickupCount, setPickupCount] = useState(0)

  useEffect(() => {
    getProfile().then(({ data }) => setProfile(data)).catch(() => {})
    getBalance().then(({ data }) => setBalance(data.balance)).catch(() => {})
    getPickupHistory().then(({ data }) => {
      const list = data.results || data
      setPickupCount(list.length)
    }).catch(() => {})
  }, [])

  return (
    <div className="page">
      <h2>👋 Welcome{profile?.first_name ? `, ${profile.first_name}` : ''}!</h2>
      <p className="page-subtitle">Here's your overview</p>

      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-icon">💰</span>
          <div>
            <p className="stat-label">Wallet Balance</p>
            <h3>₹{parseFloat(balance || 0).toFixed(2)}</h3>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">🚚</span>
          <div>
            <p className="stat-label">Total Pickups</p>
            <h3>{pickupCount}</h3>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">✅</span>
          <div>
            <p className="stat-label">Account Status</p>
            <h3>Active</h3>
          </div>
        </div>
      </div>
    </div>
  )
}
