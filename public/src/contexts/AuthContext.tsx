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
  const [isCheckingAuth, setIsCheckingAuth] = useState(false)
  const navigate = useNavigate()

  const isAuthenticated = user !== null

  // Проверка аутентификации при загрузке
  const checkAuth = useCallback(async () => {
    // Предотвращаем параллельные вызовы
    if (isCheckingAuth) {
      console.log('checkAuth уже выполняется, пропускаем...')
      return
    }
    
    try {
      setIsCheckingAuth(true)
      setIsLoading(true)
      
      console.log('Проверяем аутентификацию...')
      
      // Пробуем получить информацию о пользователе с retry
      let userInfo: UserInfo | null = null
      let lastError: Error | null = null
      
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          userInfo = await apiService.getUserInfo()
          console.log('Получена информация о пользователе:', userInfo)
          break // Успешно получили данные
        } catch (error) {
          lastError = error as Error
          console.error(`Попытка ${attempt + 1}/3 получить user_info не удалась:`, error)
          
          // Если это 401/403 - не пытаемся повторно
          if (error instanceof Error && (error.message.includes('401') || error.message.includes('403'))) {
            break
          }
          
          // Ждем перед следующей попыткой
          if (attempt < 2) {
            await new Promise(resolve => setTimeout(resolve, 1000))
          }
        }
      }
      
      if (!userInfo) {
        throw lastError || new Error('Не удалось получить информацию о пользователе')
      }
      
      setUser(userInfo)
      
      // Перенаправление по роли только если не на странице входа
      const currentPath = window.location.pathname
      if (currentPath === '/') {
        console.log('Перенаправляем пользователя по роли:', userInfo.role)
        if (userInfo.role === 'admin') {
          navigate('/admin', { replace: true })
        } else {
          navigate('/user', { replace: true })
        }
      }
    } catch (error) {
      console.error('Ошибка аутентификации:', error)
      setUser(null)
      // Не перенаправляем, если уже на странице входа
      const currentPath = window.location.pathname
      if (currentPath !== '/') {
        navigate('/', { replace: true })
      }
    } finally {
      setIsLoading(false)
      setIsCheckingAuth(false)
    }
  }, [navigate, isCheckingAuth])

  // Вход в систему
  const login = useCallback(async (email: string, code: string) => {
    try {
      console.log('Начинаем вход...')
      await apiService.login(email, code)
      console.log('Логин успешен, проверяем аутентификацию...')
      await checkAuth()
      console.log('Аутентификация проверена')
    } catch (error) {
      console.error('Ошибка входа:', error)
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

  // Автоматическое обновление токена каждые 10 минут
  useEffect(() => {
    if (!isAuthenticated) return

    const refreshInterval = setInterval(async () => {
      try {
        await apiService.refreshToken()
        // Обновляем информацию о пользователе после refresh
        const userInfo = await apiService.getUserInfo()
        setUser(userInfo)
      } catch (error) {
        console.error('Ошибка обновления токена:', error)
        // Если refresh не удался — разлогиниваем
        await logout()
      }
    }, 10 * 60 * 1000) // 10 минут

    return () => clearInterval(refreshInterval)
  }, [isAuthenticated, logout])

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
