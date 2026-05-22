import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { apiService } from '../services/api'
import { isValidEmail, isValidCode } from '../utils/validation'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorMessage } from '../components/ErrorMessage'
import './LoginPage.css'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [step, setStep] = useState<'email' | 'code'>('email')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { login } = useAuth()

  const handleGetCode = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isValidEmail(email)) {
      setError('Введите корректный email адрес')
      return
    }

    try {
      setIsLoading(true)
      setError(null)
      await apiService.getAuthCode(email)
      setStep('code')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при отправке кода')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!isValidCode(code)) {
      setError('Код должен содержать 6 цифр')
      return
    }

    try {
      setIsLoading(true)
      setError(null)
      await login(email, code)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка аутентификации')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">

        <h1>Для входа на сайт введите адрес своей электронной почты</h1>
        
        {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
        
        {step === 'email' ? (
          <form onSubmit={handleGetCode}>
            <div className="form-group">
              <label htmlFor="email">Email адрес</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="example@email.com"
                disabled={isLoading}
                autoFocus
              />
            </div>
            
            <button type="submit" className="submit-button" disabled={isLoading}>
              {isLoading ? <LoadingSpinner /> : 'Отправить код'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="email-display">Email адрес</label>
              <input
                id="email-display"
                type="email"
                value={email}
                disabled
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="code">Код подтверждения</label>
              <input
                id="code"
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                placeholder="000000"
                maxLength={6}
                disabled={isLoading}
                autoFocus
              />
              <p className="help-text">Введите 6-значный код из email</p>
            </div>
            
            <button type="submit" className="submit-button" disabled={isLoading}>
              {isLoading ? <LoadingSpinner /> : 'Войти'}
            </button>
            
            <button 
              type="button" 
              className="secondary-button"
              onClick={() => { setStep('email'); setCode(''); setError(null); }}
              disabled={isLoading}
            >
              Отправить код повторно
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
