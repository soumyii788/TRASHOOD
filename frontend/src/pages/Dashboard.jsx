import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProfile, getBalance, getPickupHistory, getCategories, requestPickup, getAddresses } from '../api/services'
import './Page.css'
import './Dashboard.css'

const CURRENT_YEAR = new Date().getFullYear()

/** Returns an ISO datetime string 2 hours from now – safe to call outside render. */
function getMinPickupStr() {
  const d = new Date()
  d.setHours(d.getHours() + 2)
  return d.toISOString().slice(0, 16)
}

// How it works steps
const STEPS = [
  { icon: '📦', title: 'Select Your Scrap', desc: 'Browse categories and estimate the weight of items you want to sell.' },
  { icon: '📅', title: 'Schedule a Pickup', desc: 'Pick a date and time that works for you. We come to your doorstep.' },
  { icon: '⚖️', title: 'We Weigh & Verify', desc: 'Our trained collector weighs your scrap on-site and confirms the items.' },
  { icon: '💰', title: 'Instant Payout', desc: 'Earn credits to your wallet instantly. Withdraw anytime.' },
]

// Category emoji fallbacks by keyword
function catEmoji(name) {
  const n = name.toLowerCase()
  if (n.includes('iron') || n.includes('steel')) return '🔩'
  if (n.includes('paper') || n.includes('newspaper') || n.includes('card')) return '📰'
  if (n.includes('plastic')) return '🧴'
  if (n.includes('copper')) return '🟤'
  if (n.includes('aluminium') || n.includes('aluminum')) return '🥫'
  if (n.includes('e-waste') || n.includes('electron')) return '💻'
  if (n.includes('glass')) return '🫙'
  if (n.includes('rubber') || n.includes('tyre')) return '⚙️'
  if (n.includes('wood')) return '🪵'
  return '♻️'
}

// Simple schedule pickup modal
function ScheduleModal({ addresses, onClose, onSuccess }) {
  const [addressId, setAddressId] = useState(addresses[0]?.id || '')
  const [dateTime, setDateTime] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const minStr = getMinPickupStr()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!addressId) { setError('Please add an address first via your profile.'); return }
    if (!dateTime) { setError('Please choose a pickup date & time.'); return }
    setError('')
    setLoading(true)
    try {
      await requestPickup({
        pickup_address: addressId,
        scheduled_time: new Date(dateTime).toISOString(),
        notes,
      })
      onSuccess()
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.response?.data?.scheduled_time?.[0]
      setError(detail || 'Failed to schedule pickup. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2>📅 Schedule a Pickup</h2>
        <p className="modal-subtitle">We'll send a collector to your doorstep.</p>

        <form onSubmit={handleSubmit} className="pickup-form">
          {addresses.length === 0 ? (
            <div className="error-banner">
              No saved address found. Please update your profile with a pickup address first.
            </div>
          ) : (
            <div className="form-group">
              <label>Pickup Address</label>
              <select value={addressId} onChange={(e) => setAddressId(e.target.value)}>
                {addresses.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.label} – {a.address_line1}, {a.city}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="form-group">
            <label>Date & Time</label>
            <input
              type="datetime-local"
              value={dateTime}
              min={minStr}
              onChange={(e) => setDateTime(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Notes (optional)</label>
            <textarea
              rows={2}
              placeholder="e.g. 3 bags of newspaper, old iron rod"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          {error && <div className="error-banner">{error}</div>}

          <button type="submit" className="btn-primary" disabled={loading || addresses.length === 0}>
            {loading ? 'Scheduling…' : 'Confirm Pickup'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [balance, setBalance] = useState(0)
  const [pickupCount, setPickupCount] = useState(0)
  const [categories, setCategories] = useState([])
  const [addresses, setAddresses] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [successMsg, setSuccessMsg] = useState('')

  useEffect(() => {
    getProfile().then(({ data }) => setProfile(data)).catch(() => {})
    getBalance().then(({ data }) => setBalance(data.balance)).catch(() => {})
    getPickupHistory().then(({ data }) => {
      const list = data.results || data
      setPickupCount(list.length)
    }).catch(() => {})
    getCategories().then(({ data }) => setCategories((data.results || data).slice(0, 6))).catch(() => {})
    getAddresses().then(({ data }) => setAddresses(data.results || data)).catch(() => {})
  }, [])

  const handleSuccess = () => {
    setShowModal(false)
    setSuccessMsg('🎉 Pickup scheduled! Check "My Pickups" for status.')
    setPickupCount((c) => c + 1)
  }

  return (
    <div className="dashboard-root">
      {/* ── Hero ── */}
      <section className="hero">
        <div className="hero-inner">
          <div className="hero-badge">♻️ Eco-friendly scrap pickup</div>
          <h1 className="hero-title">
            Turn Your Scrap Into<br />
            <span className="hero-accent">Instant Cash</span>
          </h1>
          <p className="hero-sub">
            Schedule a free doorstep pickup. We weigh your scrap on-site and credit your wallet instantly.
            No haggling. No hidden charges.
          </p>
          <div className="hero-actions">
            <button className="btn-primary hero-cta" onClick={() => setShowModal(true)}>
              📅 Schedule Free Pickup
            </button>
            <button className="btn-secondary hero-cta" onClick={() => navigate('/prices')}>
              View Price List →
            </button>
          </div>
          {successMsg && <div className="success-banner">{successMsg}</div>}
        </div>
      </section>

      <div className="page" style={{ paddingTop: '2.5rem' }}>

        {/* ── Stats ── */}
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-icon">👋</span>
            <div>
              <p className="stat-label">Welcome back</p>
              <h3>{profile?.first_name || 'Friend'}</h3>
            </div>
          </div>
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

        {/* ── Quick action ── */}
        <div className="quick-actions">
          <button className="quick-btn primary" onClick={() => setShowModal(true)}>
            📅 Schedule Pickup
          </button>
          <button className="quick-btn" onClick={() => navigate('/catalog')}>
            📦 Browse Catalog
          </button>
          <button className="quick-btn" onClick={() => navigate('/pickups')}>
            🚚 Track Pickups
          </button>
          <button className="quick-btn" onClick={() => navigate('/wallet')}>
            💰 My Wallet
          </button>
        </div>

        {/* ── How It Works ── */}
        <section className="hiw-section">
          <h2 className="section-title">How It Works</h2>
          <p className="section-sub">Four simple steps to sell your scrap</p>
          <div className="hiw-grid">
            {STEPS.map((s, i) => (
              <div className="hiw-card" key={i}>
                <div className="hiw-num">{i + 1}</div>
                <div className="hiw-icon">{s.icon}</div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Category Previews ── */}
        {categories.length > 0 && (
          <section className="preview-section">
            <div className="section-header">
              <div>
                <h2 className="section-title">Popular Categories</h2>
                <p className="section-sub">Indicative prices — actual payout confirmed at pickup</p>
              </div>
              <button className="btn-link" onClick={() => navigate('/prices')}>
                See full price list →
              </button>
            </div>
            <div className="card-grid">
              {categories.map((cat) => (
                <div className="card" key={cat.id}>
                  <div className="cat-icon">{cat.icon ? <img src={cat.icon} alt="" style={{width:48,height:48,objectFit:'contain'}} /> : catEmoji(cat.name)}</div>
                  <h3>{cat.name}</h3>
                  <p className="price">
                    ₹{parseFloat(cat.base_price_per_kg).toFixed(0)}&nbsp;
                    <span>/{cat.unit || 'kg'}</span>
                  </p>
                  <p className="price-estimate-tag">estimate</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── Trust Indicators ── */}
        <section className="trust-section">
          <div className="trust-grid">
            <div className="trust-item">🏠 <span>Doorstep Pickup</span><small>No transport needed</small></div>
            <div className="trust-item">⚖️ <span>On-Site Weighing</span><small>Transparent measurement</small></div>
            <div className="trust-item">💸 <span>Instant Credit</span><small>Wallet credited same day</small></div>
            <div className="trust-item">🔒 <span>Safe & Secure</span><small>Verified collectors only</small></div>
          </div>
        </section>

      </div>

      {/* ── Footer ── */}
      <footer className="site-footer">
        <div className="footer-inner">
          <div className="footer-brand">♻️ ScrapMarket</div>
          <p className="footer-tagline">Responsible recycling, rewarding you.</p>
          <div className="footer-links">
            <button className="footer-link" onClick={() => navigate('/prices')}>Price List</button>
            <button className="footer-link" onClick={() => navigate('/catalog')}>Catalog</button>
            <span className="footer-sep">·</span>
            <span className="footer-contact">✉️ support@scrapmarket.example.com</span>
            <span className="footer-sep">·</span>
            <span className="footer-contact">📞 +91 98765 43210</span>
          </div>
          <p className="footer-copy">© {CURRENT_YEAR} ScrapMarket. All prices are indicative estimates.</p>
        </div>
      </footer>

      {showModal && (
        <ScheduleModal
          addresses={addresses}
          onClose={() => setShowModal(false)}
          onSuccess={handleSuccess}
        />
      )}
    </div>
  )
}
