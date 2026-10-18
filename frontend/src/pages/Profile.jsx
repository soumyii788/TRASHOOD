import { useEffect, useState } from 'react'
import { getProfile, updateProfile, getAddresses, addAddress } from '../api/services'
import './Page.css'
import './Profile.css'

const LABEL_OPTIONS = [
  { value: 'HOME', icon: '🏠', hint: 'House / flat' },
  { value: 'OFFICE', icon: '🏢', hint: 'Workplace' },
  { value: 'OTHER', icon: '📍', hint: 'Anywhere else' },
]

const EMPTY_FORM = {
  label: 'HOME',
  address_line1: '',
  city: '',
  state: '',
  zip_code: '',
  lat: '',
  long: '',
  is_default: false,
}

function initials(first, last) {
  return `${(first || '')[0] || ''}${(last || '')[0] || ''}`.toUpperCase() || '?'
}

export default function Profile() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Profile form
  const [avatar, setAvatar] = useState('')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [savingProfile, setSavingProfile] = useState(false)
  const [profileMsg, setProfileMsg] = useState('')

  // Addresses
  const [addresses, setAddresses] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY_FORM)
  const [savingAddr, setSavingAddr] = useState(false)
  const [addrError, setAddrError] = useState('')
  const [addrMsg, setAddrMsg] = useState('')
  const [locating, setLocating] = useState(false)

  useEffect(() => {
    Promise.all([getProfile(), getAddresses()])
      .then(([profRes, addrRes]) => {
        const p = profRes.data
        setAvatar(p.avatar || '')
        setFirstName(p.first_name || '')
        setLastName(p.last_name || '')
        setAddresses(addrRes.data.results || addrRes.data || [])
      })
      .catch(() => setError('Failed to load your profile. Please refresh the page.'))
      .finally(() => setLoading(false))
  }, [])

  const setField = (name, value) => setForm((f) => ({ ...f, [name]: value }))

  const handleSaveProfile = async (e) => {
    e.preventDefault()
    setProfileMsg('')
    setSavingProfile(true)
    try {
      await updateProfile({ first_name: firstName, last_name: lastName })
      setProfileMsg('✅ Profile updated.')
    } catch (err) {
      const d = err?.response?.data
      setProfileMsg('❌ ' + (d?.detail || d?.first_name?.[0] || 'Could not save changes.'))
    } finally {
      setSavingProfile(false)
    }
  }

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      setAddrError('Geolocation is not supported by this browser.')
      return
    }
    setLocating(true)
    setAddrError('')
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setField('lat', pos.coords.latitude.toFixed(6))
        setField('long', pos.coords.longitude.toFixed(6))
        setLocating(false)
      },
      () => {
        setAddrError('Could not read your location. Enter lat/long manually.')
        setLocating(false)
      },
      { enableHighAccuracy: true, timeout: 10000 },
    )
  }

  const handleAddAddress = async (e) => {
    e.preventDefault()
    setAddrError('')
    if (form.lat === '' || form.long === '') {
      setAddrError('Location coordinates are required — use "Use my location" or type them in.')
      return
    }
    setSavingAddr(true)
    try {
      const { data } = await addAddress({
        ...form,
        lat: parseFloat(form.lat),
        long: parseFloat(form.long),
      })
      setAddresses((list) => [...list, data])
      setForm(EMPTY_FORM)
      setShowForm(false)
      setAddrMsg('✅ Address added. You can now pick it up when scheduling a pickup.')
    } catch (err) {
      const d = err?.response?.data
      const firstKey = d && typeof d === 'object' ? Object.keys(d)[0] : null
      setAddrError(
        firstKey ? `${firstKey}: ${Array.isArray(d[firstKey]) ? d[firstKey][0] : d[firstKey]}`
                 : (d?.detail || 'Could not add address.'),
      )
    } finally {
      setSavingAddr(false)
    }
  }

  if (loading) {
    return (
      <div className="page">
        <div className="state-box">
          <div className="spinner" />
          <span>Loading your profile…</span>
        </div>
      </div>
    )
  }

  return (
    <div className="page">
      <h2 className="page-heading">👤 Profile & Addresses</h2>
      <p className="page-subtitle">
        Manage your details and saved pickup locations. Address geolocation helps our
        collector reach you faster.
      </p>

      {error && <div className="error-banner">{error}</div>}

      <div className="profile-grid">
        {/* ── Personal details ── */}
        <section className="profile-card">
          <div className="profile-card-head">
            {avatar ? (
              <img className="profile-avatar" src={avatar} alt="" />
            ) : (
              <div className="profile-avatar placeholder">{initials(firstName, lastName)}</div>
            )}
            <div>
              <h3>{[firstName, lastName].filter(Boolean).join(' ') || 'Your name'}</h3>
              <p>Customer account</p>
            </div>
          </div>

          <form onSubmit={handleSaveProfile} className="profile-form">
            <div className="form-group">
              <label htmlFor="first_name">First name</label>
              <input
                id="first_name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="e.g. Priya"
                maxLength={50}
              />
            </div>
            <div className="form-group">
              <label htmlFor="last_name">Last name</label>
              <input
                id="last_name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="e.g. Sharma"
                maxLength={50}
              />
            </div>
            {profileMsg && <p className="profile-msg">{profileMsg}</p>}
            <button type="submit" className="profile-save-btn" disabled={savingProfile}>
              {savingProfile ? 'Saving…' : 'Save changes'}
            </button>
          </form>
        </section>

        {/* ── Address book ── */}
        <section className="profile-card">
          <div className="address-head">
            <div>
              <h3>📍 Saved addresses</h3>
              <p>{addresses.length} on file</p>
            </div>
            <button
              className="add-addr-btn"
              onClick={() => { setShowForm((s) => !s); setAddrMsg(''); setAddrError('') }}
            >
              {showForm ? 'Cancel' : '+ Add address'}
            </button>
          </div>

          {addrMsg && <p className="profile-msg">{addrMsg}</p>}

          {addresses.length === 0 && !showForm && (
            <div className="addr-empty">
              <span className="state-icon">🏠</span>
              <p>No saved addresses yet. Add one so you can schedule pickups.</p>
            </div>
          )}

          <div className="address-list">
            {addresses.map((a) => {
              const meta = LABEL_OPTIONS.find((l) => l.value === a.label) || LABEL_OPTIONS[2]
              return (
                <article className="address-item" key={a.id}>
                  <div className="address-label">
                    <span>{meta.icon} {a.label}</span>
                    {a.is_default && <span className="default-star">⭐ Default</span>}
                  </div>
                  <p className="address-line">{a.address_line1}</p>
                  <p className="address-region">{a.city}, {a.state} — {a.zip_code}</p>
                  <p className="address-coords">🌐 {a.lat}, {a.long}</p>
                </article>
              )
            })}
          </div>

          {showForm && (
            <form onSubmit={handleAddAddress} className="address-form">
              <div className="form-group">
                <label>Save as</label>
                <div className="label-picker">
                  {LABEL_OPTIONS.map((l) => (
                    <button
                      type="button"
                      key={l.value}
                      className={`label-chip${form.label === l.value ? ' active' : ''}`}
                      onClick={() => setField('label', l.value)}
                    >
                      <span>{l.icon}</span> {l.value}
                      <small>{l.hint}</small>
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="addr1">Address</label>
                <input
                  id="addr1"
                  placeholder="Flat / house no., street, area"
                  value={form.address_line1}
                  onChange={(e) => setField('address_line1', e.target.value)}
                  required
                  maxLength={255}
                />
              </div>

              <div className="addr-row">
                <div className="form-group">
                  <label htmlFor="city">City</label>
                  <input id="city" value={form.city} onChange={(e) => setField('city', e.target.value)} required maxLength={100} />
                </div>
                <div className="form-group">
                  <label htmlFor="state">State</label>
                  <input id="state" value={form.state} onChange={(e) => setField('state', e.target.value)} required maxLength={100} />
                </div>
                <div className="form-group zip">
                  <label htmlFor="zip">PIN code</label>
                  <input id="zip" inputMode="numeric" value={form.zip_code} onChange={(e) => setField('zip_code', e.target.value)} required maxLength={10} />
                </div>
              </div>

              <div className="form-group">
                <label>
                  Pickup coordinates <span className="label-note">(required — collectors navigate by these)</span>
                </label>
                <div className="addr-row coords-row">
                  <input
                    aria-label="Latitude"
                    placeholder="Latitude"
                    value={form.lat}
                    onChange={(e) => setField('lat', e.target.value)}
                    inputMode="decimal"
                  />
                  <input
                    aria-label="Longitude"
                    placeholder="Longitude"
                    value={form.long}
                    onChange={(e) => setField('long', e.target.value)}
                    inputMode="decimal"
                  />
                  <button type="button" className="geo-btn" onClick={useMyLocation} disabled={locating}>
                    {locating ? '⏳ Locating…' : '🎯 Use my location'}
                  </button>
                </div>
              </div>

              <label className="default-toggle">
                <input
                  type="checkbox"
                  checked={form.is_default}
                  onChange={(e) => setField('is_default', e.target.checked)}
                />
                Set as my default pickup address
              </label>

              {addrError && <div className="error-banner">{addrError}</div>}

              <button type="submit" className="profile-save-btn" disabled={savingAddr}>
                {savingAddr ? 'Saving…' : '✅ Save address'}
              </button>
            </form>
          )}
        </section>
      </div>
    </div>
  )
}
