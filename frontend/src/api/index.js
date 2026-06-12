import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

export const jdBillApi = {
  getBills: () => api.get('/jd-bills'),
  getBill: (id) => api.get(`/jd-bills/${id}`),
  createBill: (data) => api.post('/jd-bills', data),
  updateBill: (id, data) => api.put(`/jd-bills/${id}`, data),
  deleteBill: (id) => api.delete(`/jd-bills/${id}`),
  getItems: (billId) => api.get(`/jd-bills/${billId}/items`),
  createItem: (billId, data) => api.post(`/jd-bills/${billId}/items`, data),
  uploadItems: (billId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/jd-bills/${billId}/items/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  updateItem: (itemId, data) => api.put(`/jd-bills/items/${itemId}`, data),
  deleteItem: (itemId) => api.delete(`/jd-bills/items/${itemId}`)
}

export const erpOrderApi = {
  getOrders: (params) => api.get('/erp-orders', { params }),
  getOrder: (id) => api.get(`/erp-orders/${id}`),
  createOrder: (data) => api.post('/erp-orders', data),
  uploadOrders: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/erp-orders/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  updateOrder: (id, data) => api.put(`/erp-orders/${id}`, data),
  deleteOrder: (id) => api.delete(`/erp-orders/${id}`)
}

export const expressBillApi = {
  getBills: (params) => api.get('/express-bills', { params }),
  getBill: (id) => api.get(`/express-bills/${id}`),
  createBill: (data) => api.post('/express-bills', data),
  uploadBills: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/express-bills/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  updateBill: (id, data) => api.put(`/express-bills/${id}`, data),
  deleteBill: (id) => api.delete(`/express-bills/${id}`)
}

export const costApi = {
  getCosts: (params) => api.get('/costs', { params }),
  getCost: (id) => api.get(`/costs/${id}`),
  createCost: (data) => api.post('/costs', data),
  uploadCosts: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/costs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  syncCosts: (shopName) => api.post('/costs/sync', null, { params: { shop_name: shopName } }),
  updateCost: (id, data) => api.put(`/costs/${id}`, data),
  deleteCost: (id) => api.delete(`/costs/${id}`)
}

export const dashboardApi = {
  getProfit: (params) => api.get('/dashboard/profit', { params }),
  exportDetail: (params) => {
    window.open(`/api/dashboard/export?${new URLSearchParams(params).toString()}`)
  }
}

export default api
