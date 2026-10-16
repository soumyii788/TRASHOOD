import api from './axios'

// Auth
export const sendOTP = (phone_number, role = 'CUSTOMER') =>
  api.post('/auth/send-otp/', { phone_number, role })

export const verifyOTP = (phone_number, otp_code) =>
  api.post('/auth/verify-otp/', { phone_number, otp_code })

// Customer
export const getProfile = () => api.get('/customers/profile/')
export const updateProfile = (data) => api.put('/customers/profile/', data)
export const getAddresses = () => api.get('/customers/addresses/')
export const addAddress = (data) => api.post('/customers/addresses/', data)

// Catalog
export const getCategories = () => api.get('/catalog/categories/')

// Pickups
export const requestPickup = (data) => api.post('/pickups/request/', data)
export const getPickupHistory = () => api.get('/pickups/history/')

// Collector
export const getNearbyJobs = () => api.get('/collectors/jobs/nearby/')
export const acceptJob = (id) => api.post(`/collectors/jobs/${id}/accept/`)
export const updateJobStatus = (id) => api.patch(`/collectors/jobs/${id}/status/`)
export const updateLocation = (lat, long) => api.post('/collectors/location/', { lat, long })

// Wallet
export const getBalance = () => api.get('/wallet/balance/')
export const getTransactions = () => api.get('/wallet/transactions/')
