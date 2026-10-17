import { useEffect, useState, useMemo } from 'react'
import { getCategories } from '../api/services'
import './Page.css'

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

export default function Catalog() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    getCategories()
      .then(({ data }) => setCategories(data.results || data))
      .catch(() => setError('Failed to load catalog. Please try again.'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim()
    if (!q) return categories
    return categories.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.description?.toLowerCase().includes(q) ||
        c.accepted_items_list?.some((a) => a.toLowerCase().includes(q))
    )
  }, [categories, search])

  return (
    <div className="page">
      <h2 className="page-heading">📦 Scrap Catalog</h2>
      <p className="page-subtitle">
        Browse all accepted scrap categories. Prices shown are <em>indicative estimates</em> — final payout
        is confirmed on-site after weighing.
      </p>

      {/* Search toolbar */}
      <div className="toolbar">
        <input
          type="search"
          placeholder="🔍  Search by item or category (e.g. iron, newspaper, laptop)"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Loading */}
      {loading && (
        <div className="state-box">
          <div className="spinner" />
          <span>Loading catalog…</span>
        </div>
      )}

      {/* Error */}
      {!loading && error && <div className="error-banner">{error}</div>}

      {/* Empty search */}
      {!loading && !error && filtered.length === 0 && (
        <div className="state-box">
          <span className="state-icon">🔍</span>
          <span>No categories match "<strong>{search}</strong>"</span>
          <button className="btn-clear" onClick={() => setSearch('')}>Clear search</button>
        </div>
      )}

      {/* Catalog grid */}
      {!loading && !error && filtered.length > 0 && (
        <div className="card-grid catalog-grid">
          {filtered.map((cat) => {
            const isExpanded = expandedId === cat.id
            return (
              <div
                className={`card catalog-card${isExpanded ? ' expanded' : ''}`}
                key={cat.id}
                onClick={() => setExpandedId(isExpanded ? null : cat.id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setExpandedId(isExpanded ? null : cat.id)}
                aria-expanded={isExpanded}
              >
                <div className="cat-icon">
                  {cat.icon
                    ? <img src={cat.icon} alt="" style={{ width: 48, height: 48, objectFit: 'contain' }} />
                    : catEmoji(cat.name)}
                </div>
                <h3>{cat.name}</h3>
                <p className="price">
                  ₹{parseFloat(cat.base_price_per_kg).toFixed(2)}&nbsp;
                  <span>/{cat.unit || 'kg'}</span>
                </p>
                <p className="price-estimate-tag">indicative estimate</p>

                {cat.description && (
                  <p className="card-desc">{cat.description}</p>
                )}

                {isExpanded && cat.accepted_items_list?.length > 0 && (
                  <div className="accepted-section">
                    <p className="accepted-label">✅ Accepted items:</p>
                    <div className="accepted-chips">
                      {cat.accepted_items_list.map((item) => (
                        <span className="chip" key={item}>{item}</span>
                      ))}
                    </div>
                  </div>
                )}

                <p className="expand-hint">{isExpanded ? '▲ Less' : '▼ View accepted items'}</p>
              </div>
            )
          })}
        </div>
      )}

      <p className="catalog-footer-note">
        💡 Don't see your item? Contact us — we may still accept it.
        &nbsp;📞 +91 98765 43210
      </p>
    </div>
  )
}
