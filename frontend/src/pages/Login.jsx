import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { sendOTP, verifyOTP, socialLogin } from '../api/services'
import logoFull from '../assets/trashhood-logo.png'
import heroBg from '../assets/hero.png'
import heroBottle from '../assets/hero-bottle.jpg'
import heroRecycle from '../assets/hero-recycle.jpg'
import recycleBag from '../assets/recycle-bag.jpg'
import './Login.css'

const TRASH_IMAGES = [
  { src: heroBottle,  label: '♻️ Bottles & Cans' },
  { src: heroRecycle, label: '📦 Paper & Cardboard' },
  { src: recycleBag,  label: '🛍️ Plastic Bags' },
  { src: heroBg,      label: '🌱 E-Waste & More' },
]

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''
const APPLE_CLIENT_ID = import.meta.env.VITE_APPLE_CLIENT_ID || ''

const GOOGLE_GSI_SRC = 'https://accounts.google.com/gsi/client'
const APPLE_JS_SRC = 'https://appleid.cdn-apple.com/appleauth/static/jsapi/appleid/1/en_US/appleid.auth.js'

function loadScript(src) {
  return new Promise((resolve, reject) => {
    const existing = document.querySelector(`script[src="${src}"]`)
    if (existing) {
      if (existing.complete || existing.dataset.loaded) {
        resolve()
      } else {
        existing.addEventListener('load', resolve, { once: true })
        existing.addEventListener('error', reject, { once: true })
      }
      return
    }
    const script = document.createElement('script')
    script.src = src
    script.async = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load ' + src))
    document.head.appendChild(script)
  })
}

async function signInWithGoogle(credentialResponse, setSocialLoading) {
  setSocialLoading(true)
  try {
    const { data } = await socialLogin('google', credentialResponse.credential)
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    window.location.href = '/'
  } catch {
    alert('Google sign-in failed. Please try again.')
    setSocialLoading(false)
  }
}

async function signInWithApple(event, setSocialLoading) {
  try {
    const idToken = event.detail?.authorization?.id_token
    if (!idToken) {
      setSocialLoading(false)
      return
    }
    const { data } = await socialLogin('apple', idToken)
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    window.location.href = '/'
  } catch {
    alert('Apple sign-in failed. Please try again.')
    setSocialLoading(false)
  }
}

export default function Login() {
  const navigate = useNavigate()
  const [phone, setPhone] = useState('')
  const [otp, setOtp] = useState('')
  const [step, setStep] = useState('phone')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [socialLoading, setSocialLoading] = useState(false)
  const otpBoxRef = useRef(null)

  const handleSendOTP = async (e) => {
    e.preventDefault()
    setError('')
    if (phone.replace(/\D/g, '').length !== 10) {
      setError('Enter a valid 10-digit phone number')
      return
    }
    setLoading(true)
    try {
      await sendOTP(phone)
      setStep('otp')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send OTP. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = async (e) => {
    e.preventDefault()
    setError('')
    if (otp.length !== 6) {
      setError('Enter the 6-digit OTP')
      return
    }
    setLoading(true)
    try {
      await verifyOTP(phone, otp)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid or expired OTP.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (step === 'otp') otpBoxRef.current?.focus()
  }, [step])

  useEffect(() => {
    let cancelled = false

    async function initGoogle() {
      if (!GOOGLE_CLIENT_ID) return
      try {
        await loadScript(GOOGLE_GSI_SRC)
      } catch {
        return
      }
      if (cancelled || !window.google?.accounts?.id) return
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: (credentialResponse) => signInWithGoogle(credentialResponse, setSocialLoading),
      })
      const slot = document.getElementById('google-btn')
      if (slot) {
        slot.innerHTML = ''
        window.google.accounts.id.renderButton(slot, {
          theme: 'outline',
          size: 'large',
          width: 320,
        })
      }
    }

    async function initApple() {
      if (!APPLE_CLIENT_ID) return
      try {
        await loadScript(APPLE_JS_SRC)
      } catch {
        return
      }
      if (cancelled || !window.AppleID) return
      window.AppleID.auth.init({
        clientId: APPLE_CLIENT_ID,
        scope: 'name email',
        redirectURI: window.location.origin,
        usePopup: true,
      })
    }

    initGoogle()
    initApple()

    function onAppleResponse(e) {
      if (e.detail?.authorization) {
        signInWithApple(e, setSocialLoading)
      } else {
        setSocialLoading(false)
      }
    }
    window.addEventListener('AppleIDSignInOnSuccess', onAppleResponse)
    return () => {
      cancelled = true
      window.removeEventListener('AppleIDSignInOnSuccess', onAppleResponse)
    }
  }, [])

  return (
    <div className="login-wrap">
      <div className="login-hero">
        <div className="login-hero-content">
          <img src={logoFull} alt="Trashhood" className="login-logo" />
          <h1>Turn your scrap into <em>rewards</em></h1>
          <p>Schedule doorstep pickups, earn instant wallet credits, and track every kilo you recycle.</p>

          {/* ── Scrollable image gallery with zoom-on-touch ── */}
          <div className="hero-gallery-wrap">
            <div className="hero-gallery">
              {TRASH_IMAGES.map((img, i) => (
                <div className="hero-gallery-item" key={i}>
                  <img src={img.src} alt={img.label} draggable={false} />
                  <span className="hero-gallery-label">{img.label}</span>
                </div>
              ))}
            </div>
          </div>

          <ul className="login-bullets">
            <li>✓ Free doorstep pickup</li>
            <li>✓ Instant wallet credit</li>
            <li>✓ Transparent rates</li>
          </ul>
        </div>
      </div>

      <div className="login-form-side">
        <div className="login-card">
          {step === 'phone' ? (
            <form onSubmit={handleSendOTP} noValidate>
              <h2>Welcome back 👋</h2>
              <p className="login-sub">Sign in or create an account in seconds</p>

              <label className="field-label" htmlFor="phone">Phone number</label>
              <input
                id="phone"
                type="tel"
                inputMode="numeric"
                autoComplete="tel-national"
                placeholder="10-digit phone number"
                value={phone}
                maxLength={11}
                onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
              />

              {error && <p className="login-error">{error}</p>}

              <button className="btn-primary" type="submit" disabled={loading}>
                {loading ? 'Sending OTP…' : 'Get OTP'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOTP} noValidate>
              <h2>Enter OTP</h2>
              <p className="login-sub">
                Sent to <strong>{phone}</strong>{' '}
                <button type="button" className="link-btn" onClick={() => { setStep('phone'); setError('') }}>
                  Change
                </button>
              </p>

              <label className="field-label" htmlFor="otp">6-digit code</label>
              <input
                id="otp"
                ref={otpBoxRef}
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                placeholder="••••••"
                value={otp}
                maxLength={6}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
              />

              {error && <p className="login-error">{error}</p>}

              <button className="btn-primary" type="submit" disabled={loading}>
                {loading ? 'Verifying…' : 'Verify & Continue'}
              </button>
            </form>
          )}

          <div className="divider"><span>or continue with</span></div>

          <div className="social-row">
            <div id="google-btn" className="social-slot">
              {!GOOGLE_CLIENT_ID && (
                <button
                  type="button"
                  className="social-btn social-btn--google"
                  onClick={() => alert('Google sign-in needs VITE_GOOGLE_CLIENT_ID in frontend/.env')}
                >
                  <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z" />
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z" />
                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z" />
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z" />
                  </svg>
                  Continue with Google
                </button>
              )}
            </div>
          </div>

          <div className="social-row">
            <div id="apple-btn" className="social-slot">
              <button
                type="button"
                className="social-btn social-btn--apple"
                disabled={socialLoading}
                onClick={() => {
                  if (window.AppleID) {
                    setSocialLoading(true)
                    window.AppleID.auth
                      .signIn({ responseMode: 'fragment' })
                      .catch(() => setSocialLoading(false))
                  } else {
                    alert('Apple sign-in needs VITE_APPLE_CLIENT_ID in frontend/.env')
                  }
                }}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M16.365 1.43c0 1.14-.493 2.27-1.177 3.08-.744.9-1.99 1.57-2.987 1.57-.12 0-.23-.02-.3-.03-.01-.06-.04-.22-.04-.39 0-1.15.572-2.27 1.206-2.98.804-.94 2.142-1.64 3.248-1.68.03.13.05.28.05.43zm4.565 16.31c-.03.07-.463 1.58-1.518 3.12-.945 1.34-1.94 2.71-3.43 2.71-1.517 0-1.9-.88-3.63-.88-1.698 0-2.302.91-3.67.91-1.377 0-2.332-1.26-3.428-2.8-1.287-1.82-2.323-4.61-2.587-7.37-.134-1.47.3-2.95 1.174-4.01.87-1.06 2.14-1.71 3.405-1.71 1.302 0 2.126.87 3.21.87 1.05 0 1.694-.87 3.19-.87 1.132 0 2.33.62 3.184 1.69-2.8 1.53-2.344 5.53.035 6.75z" />
                </svg>
                {socialLoading ? 'Signing in…' : 'Continue with Apple'}
              </button>
            </div>
          </div>

          <p className="login-terms">
            By continuing you agree to our <a href="#">Terms</a> & <a href="#">Privacy Policy</a>.
          </p>
        </div>
      </div>
    </div>
  )
}