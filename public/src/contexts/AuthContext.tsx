import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import type { UserInfo } from '../types'
import { apiService } from '../services/api'

interface AuthContextType {
  user: UserInfo | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, code: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  const isAuthenticated = user !== null

  // Проверка аутентификации при загрузке
  const checkAuth = useCallback(async () => {
    try {
      setIsLoading(true)
      const userInfo = await apiService.getUserInfo()
      setUser(userInfo)
      
      // Перенаправление по роли только если не на странице входа
      const currentPath = window.location.pathname
      if (currentPath === '/') {
        if (userInfo.role === 'admin') {
          navigate('/admin', { replace: true })
        } else {
          navigate('/user', { replace: true })
        }
      }
    } catch (error) {
      setUser(null)
      // Не перенаправляем, если уже на странице входа
      const currentPath = window.location.pathname
      if (currentPath !== '/') {
        navigate('/', { replace: true })
      }
    } finally {
      setIsLoading(false)
    }
  }, [navigate])

  // Вход в систему
  const login = useCallback(async (email: string, code: string) => {
    try {
      await apiService.login(email, code)
      await checkAuth()
    } catch (error) {
      throw error
    }
  }, [checkAuth])

  // Выход из системы
  const logout = useCallback(async () => {
    try {
      await apiService.logout()
    } catch (error) {
      console.error('Ошибка при выходе:', error)
    } finally {
      setUser(null)
      navigate('/', { replace: true })
    }
  }, [navigate])

  // Проверка при монтировании
  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isLoading, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
