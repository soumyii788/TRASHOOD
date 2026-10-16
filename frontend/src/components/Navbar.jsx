import { Link, useNavigate } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  const navigate = useNavigate()

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">♻️ ScrapMarket</div>
      <div className="navbar-links">
        <Link to="/">Dashboard</Link>
        <Link to="/catalog">Catalog</Link>
        <Link to="/pickups">Pickups</Link>
        <Link to="/wallet">Wallet</Link>
      </div>
      <button className="logout-btn" onClick={logout}>Logout</button>
    </nav>
  )
}
