import { useEffect, useState } from 'react'
import { getCategories } from '../api/services'
import './Page.css'

export default function Catalog() {
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getCategories()
      .then(({ data }) => setCategories(data.results || data))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="page">
      <h2>📦 Scrap Catalog</h2>
      <p className="page-subtitle">Current prices per kg</p>
      {loading ? <p>Loading…</p> : (
        <div className="card-grid">
          {categories.map((cat) => (
            <div className="card" key={cat.id}>
              <div className="cat-icon">{cat.icon ? <img src={cat.icon} alt="" /> : '🗑️'}</div>
              <h3>{cat.name}</h3>
              <p className="price">₹{cat.base_price_per_kg} <span>/kg</span></p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
