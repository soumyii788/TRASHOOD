import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  getProfile, getBalance, getPickupHistory,
  getCategories, requestPickup, getAddresses,
} from '../api/services'
import heroImg from '../assets/hero-recycle.jpg'
import recycleBagImg from '../assets/recycle-bag.jpg'
import './Page.css'
import './Dashboard.css'

const CURRENT_YEAR = new Date().getFullYear()

function getMinPickupStr() {
  const d = new Date()
  d.setHours(d.getHours() + 2)
  return d.toISOString().slice(0, 16)
}

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
  return '♻️'
}

// ── How It Works steps ──
const STEPS = [
  { icon: '📦', title: 'Select Your Scrap', desc: 'Browse categories and estimate the weight of items you want to sell.' },
  { icon: '📅', title: 'Schedule a Pickup', desc: 'Pick a date and time. Our collector comes to your doorstep for free.' },
  { icon: '⚖️', title: 'We Weigh & Verify', desc: 'Your scrap is weighed on-site with a calibrated scale. No guesswork.' },
  { icon: '💰', title: 'Instant Wallet Credit', desc: 'Earnings hit your wallet the moment the pickup is marked complete.' },
]

// ── Blog posts (static, honest content) ──
const BLOGS = [
  {
    emoji: '♻️',
    tag: 'Recycling Tips',
    title: 'How to Sort Your Scrap at Home',
    excerpt: 'Separating metals, paper and plastic before pickup increases your payout and speeds up the collection. Here\'s a simple room-by-room guide.',
    readTime: '3 min read',
    color: '#e8f5e9',
    accent: '#2d6a4f',
  },
  {
    emoji: '💡',
    tag: 'Did You Know?',
    title: 'Copper Is the Most Valuable Common Scrap Metal',
    excerpt: 'At ₹480/kg, even a small coil of copper wire from an old appliance can earn you a meaningful payout. Learn which household items hide the most copper.',
    readTime: '4 min read',
    color: '#fff8e1',
    accent: '#b45309',
  },
  {
    emoji: '🌱',
    tag: 'Sustainability',
    title: 'Why Recycling Your E-Waste Matters',
    excerpt: 'A single smartphone contains gold, silver and rare earth metals. Disposing electronics responsibly prevents toxic leaching and recovers valuable materials.',
    readTime: '5 min read',
    color: '#e3f2fd',
    accent: '#1565c0',
  },
]

// ── Schedule Pickup Modal ──
function ScheduleModal({ addresses, onClose, onSuccess }) {
  const [addressId, setAddressId] = useState(addresses[0]?.id || '')
  const [dateTime, setDateTime] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const minStr = getMinPickupStr()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!addressId) { setError('Please add a pickup address first.'); return }
    if (!dateTime) { setError('Please choose a date & time.'); return }
    setError(''); setLoading(true)
    try {
      await requestPickup({ pickup_address: addressId, scheduled_time: new Date(dateTime).toISOString(), notes })
      onSuccess()
    } catch (err) {
      const d = err?.response?.data
      setError(d?.detail || d?.scheduled_time?.[0] || 'Failed to schedule. Please try again.')
    } finally { setLoading(false) }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <div className="modal-icon">📅</div>
        <h2>Schedule a Free Pickup</h2>
        <p className="modal-subtitle">We'll send a verified collector to your door.</p>
        <form onSubmit={handleSubmit} className="pickup-form">
          {addresses.length === 0 ? (
            <div className="error-banner">No saved address found. Update your profile first.</div>
          ) : (
            <div className="form-group">
              <label>Pickup Address</label>
              <select value={addressId} onChange={(e) => setAddressId(e.target.value)}>
                {addresses.map((a) => (
                  <option key={a.id} value={a.id}>{a.label} — {a.address_line1}, {a.city}</option>
                ))}
              </select>
            </div>
          )}
          <div className="form-group">
            <label>Date & Time</label>
            <input type="datetime-local" value={dateTime} min={minStr}
              onChange={(e) => setDateTime(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Notes <span style={{ fontWeight: 400, color: '#aaa' }}>(optional)</span></label>
            <textarea rows={2} placeholder="e.g. 3 bags of newspaper, old iron rod"
              value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>
          {error && <div className="error-banner">{error}</div>}
          <button type="submit" className="modal-submit-btn" disabled={loading || addresses.length === 0}>
            {loading ? '⏳ Scheduling…' : '✅ Confirm Pickup'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ── Wave Divider ──
function WaveDivider({ flip = false, topColor = '#fff', bottomColor = '#f0faf4' }) {
  return (
    <div className="wave-divider" style={{ background: bottomColor, transform: flip ? 'scaleX(-1)' : 'none' }}>
      <svg viewBox="0 0 1440 80" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M0,40 C360,80 1080,0 1440,40 L1440,0 L0,0 Z" fill={topColor} />
      </svg>
    </div>
  )
}

// ── Main Dashboard ──
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
    getPickupHistory().then(({ data }) => setPickupCount((data.results || data).length)).catch(() => {})
    getCategories().then(({ data }) => setCategories((data.results || data).slice(0, 6))).catch(() => {})
    getAddresses().then(({ data }) => setAddresses(data.results || data)).catch(() => {})
  }, [])

  const handleSuccess = () => {
    setShowModal(false)
    setSuccessMsg('🎉 Pickup scheduled! Track it under "My Pickups".')
    setPickupCount((c) => c + 1)
  }

  return (
    <div className="dashboard-root">

      {/* ══════════════════════════════════
           SECTION 1 — HERO
         ══════════════════════════════════ */}
      <section className="hero" style={{ backgroundImage: `url(${heroImg})` }}>
        <div className="hero-overlay" />
        <div className="hero-inner">
          <span className="hero-badge">♻️ India's Trusted Scrap Marketplace</span>
          <h1 className="hero-title">
            Trade.<br />
            <span className="hero-line2">Transform.</span><br />
            <span className="hero-accent">Renew.</span>
          </h1>
          <p className="hero-sub">
            Schedule a <strong>free doorstep pickup</strong>. We weigh your scrap on-site
            and credit your wallet <strong>instantly</strong>.
          </p>
          <div className="hero-actions">
            <button className="btn-hero-primary" onClick={() => setShowModal(true)}>
              📅 Schedule Free Pickup
            </button>
            <button className="btn-hero-secondary" onClick={() => navigate('/prices')}>
              💰 View Price List
            </button>
          </div>
          {successMsg && <div className="success-banner">{successMsg}</div>}
        </div>
      </section>

      {/* Wave break: hero → stats */}
      <WaveDivider topColor="#0d2b17" bottomColor="#f7fbf8" />

      {/* ══════════════════════════════════
           SECTION 2 — STATS + QUICK ACTIONS
         ══════════════════════════════════ */}
      <section className="section-light">
        <div className="page" style={{ paddingTop: '1rem', paddingBottom: '3rem' }}>
          <p className="section-eyebrow">Your Dashboard</p>
          <h2 className="section-title">
            Welcome back{profile?.first_name ? `, ${profile.first_name}` : ''}! 👋
          </h2>
          <div className="stats-grid" style={{ marginTop: '1.5rem' }}>
            {[
              { icon: '💰', label: 'Wallet Balance', value: `₹${parseFloat(balance || 0).toFixed(2)}` },
              { icon: '🚚', label: 'Total Pickups', value: pickupCount },
              { icon: '✅', label: 'Account Status', value: 'Active' },
              { icon: '🎁', label: 'Referral Bonus', value: '₹0.00' },
            ].map((s) => (
              <div className="stat-card" key={s.label}>
                <span className="stat-icon">{s.icon}</span>
                <div>
                  <p className="stat-label">{s.label}</p>
                  <h3>{s.value}</h3>
                </div>
              </div>
            ))}
          </div>

          <div className="quick-actions" style={{ marginTop: '1.75rem' }}>
            {[
              { icon: '📅', label: 'Schedule Pickup', primary: true, action: () => setShowModal(true) },
              { icon: '📦', label: 'Browse Catalog', action: () => navigate('/catalog') },
              { icon: '🚚', label: 'Track Pickups', action: () => navigate('/pickups') },
              { icon: '💰', label: 'My Wallet', action: () => navigate('/wallet') },
              { icon: '💎', label: 'Price List', action: () => navigate('/prices') },
            ].map((q) => (
              <button key={q.label} className={`quick-btn${q.primary ? ' primary' : ''}`} onClick={q.action}>
                <span className="qb-icon">{q.icon}</span>
                <span>{q.label}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Wave break: stats → how it works */}
      <WaveDivider topColor="#f7fbf8" bottomColor="#1a472a" />

      {/* ══════════════════════════════════
           SECTION 3 — HOW IT WORKS
         ══════════════════════════════════ */}
      <section className="section-dark">
        <div className="page" style={{ paddingTop: '3.5rem', paddingBottom: '4rem' }}>
          <p className="section-eyebrow light">Simple. Transparent. Rewarding.</p>
          <h2 className="section-title light">How It Works</h2>
          <p className="section-sub light">Four steps from doorstep to wallet credit</p>
          <div className="hiw-grid">
            {STEPS.map((s, i) => (
              <div className="hiw-card dark-card" key={i}>
                <div className="hiw-num">{i + 1}</div>
                <div className="hiw-icon">{s.icon}</div>
                <h3>{s.title}</h3>
                <p>{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Wave break: dark → white */}
      <WaveDivider topColor="#1a472a" bottomColor="#fff" />

      {/* ══════════════════════════════════
           SECTION 4 — CATEGORY PREVIEWS
         ══════════════════════════════════ */}
      {categories.length > 0 && (
        <section className="section-white">
          <div className="page" style={{ paddingTop: '1rem', paddingBottom: '3.5rem' }}>
            <p className="section-eyebrow">Live Prices</p>
            <div className="section-header">
              <div>
                <h2 className="section-title">Popular Categories</h2>
                <p className="section-sub">Indicative prices — confirmed on-site after weighing</p>
              </div>
              <button className="btn-link" onClick={() => navigate('/prices')}>
                Full price list →
              </button>
            </div>
            <div className="card-grid preview-grid">
              {categories.map((cat) => (
                <div className="card cat-card" key={cat.id}>
                  <div className="cat-icon">
                    {cat.icon
                      ? <img src={cat.icon} alt="" style={{ width: 48, height: 48, objectFit: 'contain' }} />
                      : catEmoji(cat.name)}
                  </div>
                  <h3>{cat.name}</h3>
                  <p className="price">
                    ₹{parseFloat(cat.base_price_per_kg).toFixed(0)}
                    <span>/{cat.unit || 'kg'}</span>
                  </p>
                  <p className="price-estimate-tag">est. price</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── Diagonal image breaker ── */}
      <div className="img-breaker">
        <img src={recycleBagImg} alt="Recycle before and after" />
        <div className="img-breaker-overlay">
          <p className="breaker-tagline">
            "Every kg of scrap you sell <strong>saves energy</strong>, reduces landfill, and puts <strong>money in your pocket</strong>."
          </p>
          <button className="btn-hero-primary" onClick={() => setShowModal(true)}>
            Start Recycling Today
          </button>
        </div>
      </div>

      {/* ══════════════════════════════════
           SECTION 5 — BLOGS
         ══════════════════════════════════ */}
      <section className="section-blogs">
        <div className="page" style={{ paddingTop: '3.5rem', paddingBottom: '4rem' }}>
          <p className="section-eyebrow">Knowledge Hub</p>
          <h2 className="section-title">From Our Blog</h2>
          <p className="section-sub">Tips, facts and sustainability stories from the ScrapMarket team</p>
          <div className="blog-grid">
            {BLOGS.map((b, i) => (
              <article className="blog-card" key={i} style={{ '--card-accent': b.accent, '--card-bg': b.color }}>
                <div className="blog-tag-row">
                  <span className="blog-emoji">{b.emoji}</span>
                  <span className="blog-tag" style={{ background: b.color, color: b.accent }}>{b.tag}</span>
                </div>
                <h3 className="blog-title">{b.title}</h3>
                <p className="blog-excerpt">{b.excerpt}</p>
                <div className="blog-footer">
                  <span className="blog-read-time">⏱ {b.readTime}</span>
                  <button className="blog-read-btn" style={{ color: b.accent }}>Read more →</button>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Wave break: blogs → trust */}
      <WaveDivider topColor="#f8fdf9" bottomColor="#1a472a" />

      {/* ══════════════════════════════════
           SECTION 6 — TRUST INDICATORS
         ══════════════════════════════════ */}
      <section className="section-trust">
        <div className="page" style={{ paddingTop: '3rem', paddingBottom: '3.5rem' }}>
          <p className="section-eyebrow light">Why Choose Us</p>
          <h2 className="section-title light">Built on Trust</h2>
          <div className="trust-grid">
            {[
              { icon: '🏠', title: 'Doorstep Pickup', desc: 'No trips to a scrap dealer. We come to you.' },
              { icon: '⚖️', title: 'On-Site Weighing', desc: 'Calibrated scales. Transparent measurement.' },
              { icon: '💸', title: 'Instant Credit', desc: 'Wallet credited the same day, every time.' },
              { icon: '🔒', title: 'Verified Collectors', desc: 'KYC-verified, trained and rated collectors only.' },
              { icon: '📊', title: 'Fair Prices', desc: 'Admin-set rates. No haggling, no surprises.' },
              { icon: '🌍', title: 'Eco-Responsible', desc: 'All scrap is responsibly recycled or upcycled.' },
            ].map((t) => (
              <div className="trust-item-card" key={t.title}>
                <span className="trust-item-icon">{t.icon}</span>
                <h4>{t.title}</h4>
                <p>{t.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════
           FOOTER
         ══════════════════════════════════ */}
      <footer className="site-footer">
        <div className="footer-inner">
          <div className="footer-top">
            <div className="footer-brand-block">
              <div className="footer-brand">♻️ ScrapMarket</div>
              <p className="footer-tagline">Responsible recycling, rewarding you.</p>
              <div className="footer-social">
                <span title="Facebook">📘</span>
                <span title="Instagram">📸</span>
                <span title="Twitter/X">🐦</span>
              </div>
            </div>
            <div className="footer-links-block">
              <h4>Navigate</h4>
              <button className="footer-link" onClick={() => navigate('/catalog')}>Catalog</button>
              <button className="footer-link" onClick={() => navigate('/prices')}>Price List</button>
              <button className="footer-link" onClick={() => navigate('/pickups')}>My Pickups</button>
              <button className="footer-link" onClick={() => navigate('/wallet')}>Wallet</button>
            </div>
            <div className="footer-links-block">
              <h4>Contact Us</h4>
              <p className="footer-contact-line">✉️ support@scrapmarket.example.com</p>
              <p className="footer-contact-line">📞 +91 98765 43210</p>
              <p className="footer-contact-line">🕘 Mon–Sat, 8am – 8pm IST</p>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© {CURRENT_YEAR} ScrapMarket. All rights reserved.</p>
            <p className="footer-disclaimer">All prices shown are indicative estimates. Actual payout confirmed on-site.</p>
          </div>
        </div>
      </footer>

      {showModal && (
        <ScheduleModal addresses={addresses} onClose={() => setShowModal(false)} onSuccess={handleSuccess} />
      )}
    </div>
  )
}
