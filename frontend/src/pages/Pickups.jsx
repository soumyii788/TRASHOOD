import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getPickupHistory } from '../api/services'
import './Page.css'

const STATUS_COLOR = {
  REQUESTED: '#f6ad55',
  ASSIGNED: '#63b3ed',
  ON_THE_WAY: '#68d391',
  COMPLETED: '#48bb78',
  CANCELLED: '#fc8181',
}

const STATUS_LABEL = {
  REQUESTED: 'Requested',
  ASSIGNED: 'Assigned',
  ON_THE_WAY: 'On The Way',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
}

export default function Pickups() {
  const navigate = useNavigate()
  const [pickups, setPickups] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getPickupHistory()
      .then(({ data }) => setPickups(data.results || data))
      .catch(() => setError('Failed to load pickups. Please try again.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <h2 className="page-heading">🚚 My Pickups</h2>
          <p className="page-subtitle" style={{ margin: 0 }}>Track all your scrap collection requests.</p>
        </div>
        <button className="schedule-cta-btn" onClick={() => navigate('/')}>
          + Schedule Pickup
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="state-box">
          <div className="spinner" />
          <span>Loading your pickups…</span>
        </div>
      )}

      {/* Error */}
      {!loading && error && <div className="error-banner">{error}</div>}

      {/* Empty */}
      {!loading && !error && pickups.length === 0 && (
        <div className="state-box">
          <span className="state-icon">🚚</span>
          <span>No pickups yet.</span>
          <p style={{ fontSize: '0.88rem', color: '#aaa', margin: 0 }}>
            Schedule your first pickup from the dashboard.
          </p>
          <button className="btn-primary" style={{ background: '#1a472a', color: 'white', border: 'none', borderRadius: 8, padding: '0.6rem 1.25rem', cursor: 'pointer', fontSize: '0.9rem' }} onClick={() => navigate('/')}>
            Schedule Now
          </button>
        </div>
      )}

      {/* Pickup list */}
      {!loading && !error && pickups.length > 0 && (
        <div className="pickup-list">
          {pickups.map((p) => (
            <div className="pickup-card" key={p.id}>
              <div className="pickup-header">
                <span className="pickup-id">#{String(p.id).slice(0, 8).toUpperCase()}</span>
                <span className="pickup-status" style={{ background: STATUS_COLOR[p.status] || '#aaa' }}>
                  {STATUS_LABEL[p.status] || p.status}
                </span>
              </div>
              <p>📅 {new Date(p.scheduled_time).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}</p>
              {p.total_payout > 0 && (
                <p>💵 Payout: <strong>₹{parseFloat(p.total_payout).toFixed(2)}</strong></p>
              )}
              {p.notes && <p>📝 {p.notes}</p>}
              {p.items?.length > 0 && (
                <div className="pickup-items">
                  {p.items.map((item) => (
                    <span key={item.id} className="chip">
                      {item.category_name} — {item.actual_weight_kg} kg
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
