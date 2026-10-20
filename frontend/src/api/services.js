import api from './axios'
import axios from 'axios'

// Auth
export const sendOTP = (phone_number, role = 'CUSTOMER') =>
  api.post('/auth/send-otp/', { phone_number, role })

export const verifyOTP = (phone_number, otp_code) =>
  api.post('/auth/verify-otp/', { phone_number, otp_code })

export const getMe = () => api.get('/auth/me/')
export const refreshToken = (refresh) => api.post('/auth/token/refresh/', { refresh })

// Customer
export const getProfile = () => api.get('/customers/profile/')
export const updateProfile = (data) => api.put('/customers/profile/', data)
export const getAddresses = () => api.get('/customers/addresses/')
export const addAddress = (data) => api.post('/customers/addresses/', data)
export const updateAddress = (id, data) => api.patch(`/customers/addresses/${id}/`, data)
export const deleteAddress = (id) => api.delete(`/customers/addresses/${id}/`)

// Catalog – authenticated (post-login)
export const getCategories = () => api.get('/catalog/categories/')
export const getCategory = (id) => api.get(`/catalog/categories/${id}/`)

// Catalog – public price list (no auth required)
export const getPublicCategories = () =>
  axios.get('/api/v1/catalog/public-categories/')

// Pickups
export const requestPickup = (data) => api.post('/pickups/request/', data)
export const getPickupHistory = (status) =>
  api.get('/pickups/history/', { params: status ? { status } : {} })
export const getActivePickups = () => api.get('/pickups/active/')
export const getPickup = (id) => api.get(`/pickups/${id}/`)
export const cancelPickup = (id, reason = '') =>
  api.post(`/pickups/${id}/cancel/`, { reason })

// Collector
export const getCollectorProfile = () => api.get('/collectors/profile/')
export const updateCollectorProfile = (data) => api.patch('/collectors/profile/', data)
export const setCollectorAvailability = (is_available) =>
  api.post('/collectors/availability/', { is_available })
export const getNearbyJobs = (params) => api.get('/collectors/jobs/nearby/', { params })
export const getAssignedJobs = () => api.get('/collectors/jobs/assigned/')
export const acceptJob = (id) => api.post(`/collectors/jobs/${id}/accept/`)
export const updateJobStatus = (id, payload = {}) =>
  api.patch(`/collectors/jobs/${id}/status/`, payload)
export const weighJob = (id, items) => api.post(`/collectors/jobs/${id}/weigh/`, { items })
export const completeJob = (id) => api.post(`/collectors/jobs/${id}/complete/`)
export const updateLocation = (lat, long) => api.post('/collectors/location/', { lat, long })

// Wallet
export const getBalance = () => api.get('/wallet/balance/')
export const getTransactions = (params) => api.get('/wallet/transactions/', { params })
export const requestWithdraw = (amount) => api.post('/wallet/withdraw/', { amount })
