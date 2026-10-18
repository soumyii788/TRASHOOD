import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Catalog from './pages/Catalog'
import Pickups from './pages/Pickups'
import Wallet from './pages/Wallet'
import PriceList from './pages/PriceList'
import Profile from './pages/Profile'
import Navbar from './components/Navbar'

function PrivateRoute({ children }) {
  const token = localStorage.getItem('access_token')
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <>
                <Navbar />
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/catalog" element={<Catalog />} />
                  <Route path="/pickups" element={<Pickups />} />
                  <Route path="/wallet" element={<Wallet />} />
                  <Route path="/prices" element={<PriceList />} />
                  <Route path="/profile" element={<Profile />} />
                </Routes>
              </>
            </PrivateRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
