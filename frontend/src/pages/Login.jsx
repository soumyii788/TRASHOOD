import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { sendOTP, verifyOTP } from '../api/services'
import './Login.css'

export default function Login() {
  const navigate = useNavigate()
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [devOtp, setDevOtp] = useState('')   // shown in dev mode hint
  const [step, setStep] = useState('phone') // 'phone' | 'otp'
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSendOTP = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await sendOTP(phone)
      // In dev mode, the backend returns the OTP in the response
      if (data.otp) {
        setOtp(data.otp)       // auto-fill the OTP field
        setDevOtp(data.otp)    // show the hint box
      }
      setStep('otp')
    } catch {
      setError('Failed to send OTP. Check your number.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { data } = await verifyOTP(phone, otp)
      localStorage.setItem('access_token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      navigate('/')
    } catch {
      setError('Invalid or expired OTP.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>♻️ ScrapMarket</h1>
        <p className="subtitle">Sell your scrap, earn instantly</p>

        {step === 'phone' ? (
          <form onSubmit={handleSendOTP}>
            <label>Phone Number</label>
            <input
              type="tel"
              placeholder="+91 98765 43210"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
            />
            {error && <p className="error">{error}</p>}
            <button type="submit" disabled={loading}>
              {loading ? 'Sending…' : 'Send OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOTP}>
            <label>Enter OTP sent to {phone}</label>
            {devOtp && (
              <div className="dev-otp-hint">
                🛠️ <strong>Dev Mode OTP:</strong> <span className="otp-code">{devOtp}</span>
                <small> (auto-filled below)</small>
              </div>
            )}
            <input
              type="text"
              placeholder="6-digit OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              maxLength={6}
              required
            />
            {error && <p className="error">{error}</p>}
            <button type="submit" disabled={loading}>
              {loading ? 'Verifying…' : 'Verify & Login'}
            </button>
            <button type="button" className="link" onClick={() => setStep('phone')}>
              ← Change number
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
