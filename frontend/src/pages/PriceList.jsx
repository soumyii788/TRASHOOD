import { useEffect, useState, useMemo } from 'react'
import { getCategories } from '../api/services'
import './Page.css'

const UNIT_LABELS = { kg: '/kg', unit: '/unit', litre: '/litre' }

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

export default function PriceList() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [unitFilter, setUnitFilter] = useState('all')
  const [sortBy, setSortBy] = useState('default')

  useEffect(() => {
    getCategories()
      .then(({ data }) => setCategories(data.results || data))
      .catch(() => setError('Unable to load prices. Please refresh or try again later.'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    let list = [...categories]
    const q = search.toLowerCase().trim()
    if (q) {
      list = list.filter(
        (c) =>
          c.name.toLowerCase().includes(q) ||
          c.description?.toLowerCase().includes(q) ||
          c.accepted_items_list?.some((a) => a.toLowerCase().includes(q))
      )
    }
    if (unitFilter !== 'all') {
      list = list.filter((c) => c.unit === unitFilter)
    }
    if (sortBy === 'price-asc') list.sort((a, b) => a.base_price_per_kg - b.base_price_per_kg)
    if (sortBy === 'price-desc') list.sort((a, b) => b.base_price_per_kg - a.base_price_per_kg)
    if (sortBy === 'name') list.sort((a, b) => a.name.localeCompare(b.name))
    return list
  }, [categories, search, unitFilter, sortBy])

  const units = useMemo(() => {
    const all = [...new Set(categories.map((c) => c.unit).filter(Boolean))]
    return all
  }, [categories])

  return (
    <div className="page">
      <h2 className="page-heading">💰 Scrap Price List</h2>
      <p className="page-subtitle">
        All prices are <strong>indicative estimates</strong> set by our admin team. The actual payout is confirmed
        on-site after your scrap is weighed by the collector.
      </p>

      {/* Estimate disclaimer */}
      <div className="price-disclaimer">
        ⚠️ <strong>Prices shown are estimates only.</strong> Final buyback rate depends on item condition,
        quantity, and current market rates. No purchase guarantee.
      </div>

      {/* Toolbar */}
      <div className="toolbar">
        <input
          type="search"
          placeholder="🔍  Search categories or items…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {units.length > 1 && (
          <select value={unitFilter} onChange={(e) => setUnitFilter(e.target.value)}>
            <option value="all">All units</option>
            {units.map((u) => (
              <option key={u} value={u}>{UNIT_LABELS[u] || u}</option>
            ))}
          </select>
        )}
        <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
          <option value="default">Default order</option>
          <option value="name">A → Z</option>
          <option value="price-asc">Price: Low → High</option>
          <option value="price-desc">Price: High → Low</option>
        </select>
      </div>

      {/* Loading */}
      {loading && (
        <div className="state-box">
          <div className="spinner" />
          <span>Loading prices…</span>
        </div>
      )}

      {/* Error */}
      {!loading && error && <div className="error-banner">{error}</div>}

      {/* Empty */}
      {!loading && !error && filtered.length === 0 && (
        <div className="state-box">
          <span className="state-icon">🔍</span>
          <span>No results for "<strong>{search}</strong>"</span>
          <button className="btn-clear" onClick={() => { setSearch(''); setUnitFilter('all') }}>
            Clear filters
          </button>
        </div>
      )}

      {/* Price table */}
      {!loading && !error && filtered.length > 0 && (
        <>
          <p className="result-count">{filtered.length} categor{filtered.length === 1 ? 'y' : 'ies'} found</p>
          <table className="price-table">
            <thead>
              <tr>
                <th style={{ width: 40 }} />
                <th>Category</th>
                <th>Description</th>
                <th>Accepted Items</th>
                <th className="price-col">Est. Price</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((cat) => (
                <tr key={cat.id}>
                  <td className="emoji-col">{cat.icon ? <img src={cat.icon} alt="" width={32} /> : catEmoji(cat.name)}</td>
                  <td className="cat-name-col"><strong>{cat.name}</strong></td>
                  <td className="desc-col">{cat.description || '—'}</td>
                  <td className="items-col">
                    {cat.accepted_items_list?.length
                      ? <div className="accepted-chips" style={{ justifyContent: 'flex-start' }}>
                          {cat.accepted_items_list.map((i) => <span key={i} className="chip">{i}</span>)}
                        </div>
                      : '—'}
                  </td>
                  <td className="price-col">
                    <span className="price-value">
                      ₹{parseFloat(cat.base_price_per_kg).toFixed(2)}
                    </span>
                    <span className="price-unit">{UNIT_LABELS[cat.unit] || `/${cat.unit}`}</span>
                    <span className="est-label">est.</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <p className="catalog-footer-note">
            Prices last updated by admin. Contact us to schedule a free pickup: 📞 +91 98765 43210
          </p>
        </>
      )}
    </div>
  )
}
