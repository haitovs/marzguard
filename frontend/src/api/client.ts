const API_BASE = '/api/v1'

function getToken(): string | null {
  return localStorage.getItem('marzguard_token')
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    localStorage.removeItem('marzguard_token')
    window.location.href = '/login'
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }

  return res.json()
}

export const api = {
  // Auth
  login: async (username: string, password: string) => {
    const res = await fetch(`${API_BASE}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username, password, grant_type: 'password' }),
    })
    if (!res.ok) throw new Error('Login failed')
    return res.json()
  },

  // Dashboard
  getSummary: () => request<any>('/dashboard/summary'),
  getLive: () => request<any>('/dashboard/live'),

  // Users
  getAdmins: () => request<any>('/users/admins'),
  getUsers: (page = 1, search = '', admin = '') => {
    const params = new URLSearchParams({ page: String(page), page_size: '50' })
    if (search) params.set('search', search)
    if (admin) params.set('admin', admin)
    return request<any>(`/users?${params}`)
  },
  getUser: (username: string) => request<any>(`/users/${username}`),
  updateUser: (username: string, data: any) =>
    request<any>(`/users/${username}`, { method: 'PUT', body: JSON.stringify(data) }),
  disableUser: (username: string) =>
    request<any>(`/users/${username}/disable`, { method: 'POST' }),
  enableUser: (username: string) =>
    request<any>(`/users/${username}/enable`, { method: 'POST' }),
  syncUsers: () => request<any>('/users/sync', { method: 'POST' }),

  // Policies
  getPolicies: () => request<any[]>('/policies'),
  createPolicy: (data: any) =>
    request<any>('/policies', { method: 'POST', body: JSON.stringify(data) }),
  updatePolicy: (id: number, data: any) =>
    request<any>(`/policies/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deletePolicy: (id: number) =>
    request<any>(`/policies/${id}`, { method: 'DELETE' }),
  batchAssignPolicy: (data: any) =>
    request<any>('/policies/batch-assign', { method: 'POST', body: JSON.stringify(data) }),

  // Settings
  getSettings: () => request<any>('/settings'),
  updateSettings: (data: any) =>
    request<any>('/settings', { method: 'PUT', body: JSON.stringify(data) }),

  // Logs
  getLogs: (page = 1, eventType = '', username = '') => {
    const params = new URLSearchParams({ page: String(page), page_size: '50' })
    if (eventType) params.set('event_type', eventType)
    if (username) params.set('username', username)
    return request<any>(`/logs?${params}`)
  },
}
