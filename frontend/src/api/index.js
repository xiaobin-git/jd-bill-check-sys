import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

const buildQueryString = (params = {}) => {
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value)
    }
  })
  return searchParams.toString()
}

export const jdBillApi = {
  getBills: (params) => api.get('/jd-bills', { params }),
  getShopNames: () => api.get('/jd-bills/shops'),
  getBill: (id) => api.get(`/jd-bills/${id}`),
  createBill: (data) => api.post('/jd-bills', data),
  updateBill: (id, data) => api.put(`/jd-bills/${id}`, data),
  deleteBill: (id) => api.delete(`/jd-bills/${id}`),
  getItems: (billId, params) => api.get(`/jd-bills/${billId}/items`, { params }),
  getItemFilterOptions: (billId) => api.get(`/jd-bills/${billId}/item-filter-options`),
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
  getCarriers: () => api.get('/express-bills/carriers'),
  getFieldMappings: () => api.get('/express-bills/field-mappings'),
  updateFieldMappings: (mappings) => api.put('/express-bills/field-mappings', { mappings }),
  getBill: (id) => api.get(`/express-bills/${id}`),
  createBill: (data) => api.post('/express-bills', data),
  importBills: ({ carrier, file, fieldMapping }) => {
    const formData = new FormData()
    formData.append('carrier', carrier)
    formData.append('file', file)
    if (fieldMapping) {
      formData.append('field_mapping', JSON.stringify(fieldMapping))
    }
    return api.post('/express-bills/import', formData, {
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
  exportCosts: (params) => {
    window.open(`/api/costs/export?${buildQueryString(params)}`)
  },
  downloadTemplate: () => {
    window.open('/api/costs/template')
  },
  updateCost: (id, data) => api.put(`/costs/${id}`, data),
  deleteCost: (id) => api.delete(`/costs/${id}`)
}

export const dashboardApi = {
  getProfit: (params) => api.get('/dashboard/profit', { params }),
  exportDetail: (params) => {
    window.open(`/api/dashboard/export?${buildQueryString(params)}`)
  }
}

export default api
