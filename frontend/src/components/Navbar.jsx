import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import logoIcon from '../assets/trashhood-icon.png'
import './Navbar.css'

export default function Navbar() {
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  const close = () => setMenuOpen(false)

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand" onClick={close}>
        <img src={logoIcon} alt="" className="navbar-logo" />
        <span>trash<span className="brand-hood">hood</span></span>
      </Link>

      {/* Desktop links */}
      <div className="navbar-links">
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/catalog">Catalog</NavLink>
        <NavLink to="/pickups">My Pickups</NavLink>
        <NavLink to="/wallet">Wallet</NavLink>
        <NavLink to="/prices">Price List</NavLink>
        <NavLink to="/profile">Profile</NavLink>
      </div>

      <button className="logout-btn" onClick={logout}>Logout</button>

      {/* Mobile hamburger */}
      <button
        className="hamburger"
        aria-label="Toggle menu"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((o) => !o)}
      >
        <span /><span /><span />
      </button>

      {/* Mobile drawer */}
      {menuOpen && (
        <div className="mobile-menu">
          <NavLink to="/" end onClick={close}>Dashboard</NavLink>
          <NavLink to="/catalog" onClick={close}>Catalog</NavLink>
          <NavLink to="/pickups" onClick={close}>My Pickups</NavLink>
          <NavLink to="/wallet" onClick={close}>Wallet</NavLink>
          <NavLink to="/prices" onClick={close}>Price List</NavLink>
          <NavLink to="/profile" onClick={close}>Profile</NavLink>
          <button className="logout-btn mobile-logout" onClick={logout}>Logout</button>
        </div>
      )}
    </nav>
  )
}
