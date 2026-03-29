import React, { createContext, useContext, useState, useCallback } from 'react'
import { api } from '../api/client'

interface AuthContextType {
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>(null!)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem('marzguard_token')
  )

  const login = useCallback(async (username: string, password: string) => {
    const data = await api.login(username, password)
    localStorage.setItem('marzguard_token', data.access_token)
    setToken(data.access_token)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('marzguard_token')
    setToken(null)
  }, [])

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
