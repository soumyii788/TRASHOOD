import { useEffect, useState } from 'react'
import { getPickupHistory } from '../api/services'
import './Page.css'

const STATUS_COLOR = {
  REQUESTED: '#f6ad55',
  ASSIGNED: '#63b3ed',
  ON_THE_WAY: '#68d391',
  COMPLETED: '#48bb78',
  CANCELLED: '#fc8181',
}

export default function Pickups() {
  const [pickups, setPickups] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getPickupHistory()
      .then(({ data }) => setPickups(data.results || data))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page">
      <h2>🚚 My Pickups</h2>
      {loading ? <p>Loading…</p> : pickups.length === 0 ? (
        <p>No pickups yet. Request one from the dashboard!</p>
      ) : (
        <div className="pickup-list">
          {pickups.map((p) => (
            <div className="pickup-card" key={p.id}>
              <div className="pickup-header">
                <span className="pickup-id">#{p.id.slice(0, 8)}</span>
                <span className="pickup-status" style={{ background: STATUS_COLOR[p.status] }}>
                  {p.status}
                </span>
              </div>
              <p>📅 {new Date(p.scheduled_time).toLocaleString()}</p>
              <p>💵 Payout: ₹{p.total_payout}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
