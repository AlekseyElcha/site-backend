import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { apiService } from '../services/api'
import { sortQuestions } from '../utils/formatting'
import type { Question, NewQuestionForm } from '../types'
import { QuestionCard } from '../components/QuestionCard'
import { QuestionDetails } from '../components/QuestionDetails'
import { QuestionForm } from '../components/QuestionForm'
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

  const loadQuestions = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Загружаем вопросы и ответы параллельно
      const [allQuestions, allAnswers] = await Promise.all([
        apiService.getAllQuestions(),
        apiService.getAllAnswers()
      ])
      
      // Фильтруем вопросы пользователя
      const userQuestions = allQuestions.filter(q => q.email === user?.sub)
      
      // Объединяем вопросы с их ответами
      const questionsWithAnswers = userQuestions.map(question => ({
        ...question,
        answers: allAnswers.filter(answer => answer.question_id === question.id)
      }))
      
      // Сортируем вопросы
      const sortedQuestions = sortQuestions(questionsWithAnswers)
      setQuestions(sortedQuestions)
      
      // Обновляем выбранное обращение, если оно было выбрано
      if (selectedQuestion) {
        const updated = questionsWithAnswers.find(q => q.id === selectedQuestion.id)
        if (updated) {
          setSelectedQuestion(updated)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки обращений')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadQuestions()
    
    // Обновляем данные каждые 30 секунд
    const interval = setInterval(() => {
      loadQuestions()
    }, 30000)
    
    return () => clearInterval(interval)
  }, [user])

  // Автоматически выбираем вопрос из URL
  useEffect(() => {
    if (questionId && questions.length > 0) {
      const question = questions.find(q => q.id === questionId)
      if (question) {
        setSelectedQuestion(question)
      }
    }
  }, [questionId, questions])

  const handleCreateQuestion = async (form: NewQuestionForm, files: File[]) => {
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
  }

  return (
    <div className="user-page">
      {successMessage && (
        <SuccessNotification 
          message={successMessage} 
          onClose={() => setSuccessMessage(null)} 
        />
      )}
      
      <header className="page-header">
        <h1>Мои обращения</h1>
        <div className="header-actions">
          <button onClick={() => setShowForm(!showForm)} className="new-button">
            {showForm ? 'Отменить' : 'Новое обращение'}
          </button>
          <button onClick={logout} className="logout-button">Выйти</button>
        </div>
      </header>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}

      {showForm && (
        <div className="form-section">
          <QuestionForm 
            onSubmit={handleCreateQuestion} 
            isLoading={isSubmitting}
            userEmail={user?.sub || ''}
          />
        </div>
      )}

      <div className="page-content">
        <aside className="sidebar">
          {isLoading ? (
            <LoadingSpinner />
          ) : questions.length === 0 && !showForm ? (
            <div className="empty-state">
              <p>У вас пока нет обращений</p>
              <button onClick={() => setShowForm(true)} className="new-button">
                Создать первое обращение
              </button>
            </div>
          ) : questions.length === 0 && showForm ? (
            <div className="empty-state">
              <p>У вас пока нет обращений</p>
            </div>
          ) : (
            <div className="questions-list">
              {questions.map((question) => (
                <QuestionCard
                  key={question.id}
                  question={question}
                  onClick={() => setSelectedQuestion(question)}
                  isSelected={selectedQuestion?.id === question.id}
                />
              ))}
            </div>
          )}
        </aside>

        <main className="main-content">
          {selectedQuestion ? (
            <QuestionDetails question={selectedQuestion} />
          ) : (
            <div className="empty-state">
              <p>Выберите обращение для просмотра деталей</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
