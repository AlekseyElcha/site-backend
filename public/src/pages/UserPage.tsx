import { useState, useEffect, useMemo, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { apiService } from '../services/api'
import { sortQuestions } from '../utils/formatting'
import type { Question, NewQuestionForm } from '../types'
import { QuestionCard } from '../components/QuestionCard'
import { QuestionDetails } from '../components/QuestionDetails'
import { QuestionForm } from '../components/QuestionForm'
import { Modal } from '../components/Modal'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorMessage } from '../components/ErrorMessage'
import { SuccessNotification } from '../components/SuccessNotification'
import './UserPage.css'

export function UserPage() {
  const { questionId } = useParams<{ questionId?: string }>()
  const { user, logout } = useAuth()
  const [questions, setQuestions] = useState<Question[]>([])
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [showArchived, setShowArchived] = useState(false)
  const [showAnswered, setShowAnswered] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)

  // Фильтруем вопросы по настройкам
  const filteredQuestions = useMemo(() => {
    return questions.filter(q => {
      // Фильтр архивных
      if (!showArchived && q.status === 'closed') return false
      // Фильтр отвеченных
      if (!showAnswered && q.status === 'answered') return false
      return true
    })
  }, [questions, showArchived, showAnswered])

  const loadQuestions = useCallback(async () => {
    const abortController = new AbortController()
    
    try {
      setIsLoading(true)
      setError(null)
      
      // Загружаем только список вопросов
      const allQuestions = await apiService.getAllQuestions()
      
      // Проверяем, не был ли запрос отменен
      if (abortController.signal.aborted) return
      
      // Фильтруем вопросы пользователя
      const userQuestions = allQuestions.filter(q => q.email === user?.sub)
      
      // Сортируем вопросы
      const sortedQuestions = sortQuestions(userQuestions)
      setQuestions(sortedQuestions)
    } catch (err) {
      if (abortController.signal.aborted) return
      setError(err instanceof Error ? err.message : 'Ошибка загрузки обращений')
    } finally {
      if (!abortController.signal.aborted) {
        setIsLoading(false)
      }
    }
    
    return () => abortController.abort()
  }, [user])

  const handleSearch = useCallback(async (query: string) => {
    if (!query.trim()) {
      // Если поиск пустой, загружаем все вопросы
      await loadQuestions()
      return
    }

    try {
      setIsSearching(true)
      setError(null)
      
      const results = await apiService.filterQuestions(query)
      
      // Фильтруем только валидные вопросы (с полем id) и для текущего пользователя
      const validResults = results.filter(q => q.id && q.email === user?.sub)
      
      // Сортируем результаты
      const sortedResults = sortQuestions(validResults)
      setQuestions(sortedResults)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка поиска')
    } finally {
      setIsSearching(false)
    }
  }, [user, loadQuestions])

  useEffect(() => {
    loadQuestions()
    
    // Обновляем данные каждые 30 секунд
    const interval = setInterval(() => {
      loadQuestions()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [loadQuestions])

  // Автоматически выбираем вопрос из URL
  useEffect(() => {
    if (questionId && questions.length > 0) {
      const question = questions.find(q => q.id === questionId)
      if (question) {
        loadQuestionDetails(question.id)
      }
    }
  }, [questionId, questions])

  // Загружаем полные данные по вопросу
  const loadQuestionDetails = useCallback(async (qId: string) => {
    try {
      const data = await apiService.getQuestionData(qId)
      // Объединяем данные в формат Question
      const fullQuestion: Question = {
        ...data.question,
        answers: data.answers,
        extra_messages: data.extra_messages
      }
      setSelectedQuestion(fullQuestion)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки деталей обращения')
    }
  }, [])

  const handleCreateQuestion = useCallback(async (form: NewQuestionForm, files: File[]) => {
    try {
      setIsSubmitting(true)
      setError(null)
      await apiService.createQuestion(form, files)
      setSuccessMessage('Обращение успешно создано!')
      await loadQuestions()
      setShowForm(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания обращения')
      throw err
    } finally {
      setIsSubmitting(false)
    }
  }, [loadQuestions])

  const handleToggleForm = useCallback(() => {
    setShowForm(prev => !prev)
  }, [])

  const handleCloseModal = useCallback(() => {
    setSelectedQuestion(null)
  }, [])

  const handleCloseError = useCallback(() => {
    setError(null)
  }, [])

  const handleCloseSuccess = useCallback(() => {
    setSuccessMessage(null)
  }, [])

  const handleMarkAsResolved = useCallback(async () => {
    if (!selectedQuestion) return
    
    try {
      setError(null)
      const response = await apiService.changeQuestionStatus(selectedQuestion.id, 'closed')
      
      if (response.message) {
        setSuccessMessage(response.message)
      }
      
      await loadQuestions()
      setSelectedQuestion(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка изменения статуса')
    }
  }, [selectedQuestion, loadQuestions])

  return (
    <div className="user-page">
      {successMessage && (
        <SuccessNotification 
          message={successMessage} 
          onClose={handleCloseSuccess} 
        />
      )}
      
      <header className="page-header">
        <h1>Мои обращения</h1>
        <div className="header-actions">
          <button onClick={handleToggleForm} className="new-button">
            {showForm ? 'Отменить' : 'Новое обращение'}
          </button>
          <button onClick={logout} className="logout-button">Выйти</button>
        </div>
      </header>

      {error && <ErrorMessage message={error} onClose={handleCloseError} />}

      {showForm && (
        <div className="form-section">
          <QuestionForm 
            onSubmit={handleCreateQuestion} 
            isLoading={isSubmitting}
            userEmail={user?.sub || ''}
          />
        </div>
      )}

      {!showForm && (
        <div className="page-content">
          <div className="filter-section">
            <div className="search-box">
              <input
                type="text"
                placeholder="Поиск по обращениям..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSearch(searchQuery)
                  }
                }}
                className="search-input"
              />
              <button 
                onClick={() => handleSearch(searchQuery)}
                disabled={isSearching}
                className="search-button"
              >
                {isSearching ? 'Поиск...' : 'Найти'}
              </button>
              {searchQuery && (
                <button 
                  onClick={() => {
                    setSearchQuery('')
                    loadQuestions()
                  }}
                  className="clear-search-button"
                >
                  Очистить
                </button>
              )}
            </div>
            <div className="user-filters">
              <label className="filter-toggle">
                <input
                  type="checkbox"
                  checked={showAnswered}
                  onChange={(e) => setShowAnswered(e.target.checked)}
                />
                <span>Показывать отвеченные</span>
              </label>
              <label className="filter-toggle">
                <input
                  type="checkbox"
                  checked={showArchived}
                  onChange={(e) => setShowArchived(e.target.checked)}
                />
                <span>Показывать архивные</span>
              </label>
            </div>
          </div>

          <div className="questions-grid">
            {isLoading ? (
              <LoadingSpinner />
            ) : filteredQuestions.length === 0 ? (
              <div className="empty-state">
                <p>Нет обращений для отображения</p>
                {questions.length > 0 && (
                  <p className="filter-hint">Попробуйте изменить настройки фильтров</p>
                )}
              </div>
            ) : (
              filteredQuestions.map((question) => (
                <QuestionCard
                  key={question.id}
                  question={question}
                  onClick={() => loadQuestionDetails(question.id)}
                  isSelected={selectedQuestion?.id === question.id}
                />
              ))
            )}
          </div>
        </div>
      )}

      <Modal isOpen={selectedQuestion !== null} onClose={handleCloseModal}>
        {selectedQuestion && (
          <>
            <QuestionDetails question={selectedQuestion} onRefresh={loadQuestions} />
            {selectedQuestion.status !== 'closed' && (
              <div className="user-actions">
                <button 
                  className="resolve-button"
                  onClick={handleMarkAsResolved}
                  type="button"
                >
                  Мой вопрос решен
                </button>
              </div>
            )}
          </>
        )}
      </Modal>
    </div>
  )
}
