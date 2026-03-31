import { useState, useEffect, useMemo, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { apiService } from '../services/api'
import { sortQuestions } from '../utils/formatting'
import type { Question, QuestionStatus } from '../types'
import { QuestionCard } from '../components/QuestionCard'
import { QuestionDetails } from '../components/QuestionDetails'
import { AnswerForm } from '../components/AnswerForm'
import { StatusFilter } from '../components/StatusFilter'
import { Modal } from '../components/Modal'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorMessage } from '../components/ErrorMessage'
import { SuccessNotification } from '../components/SuccessNotification'
import './AdminPage.css'

export function AdminPage() {
  const { questionId } = useParams<{ questionId?: string }>()
  const { logout } = useAuth()
  const [questions, setQuestions] = useState<Question[]>([])
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null)
  const [selectedStatus, setSelectedStatus] = useState<QuestionStatus | 'all'>('all')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Мемоизируем отфильтрованные вопросы
  const filteredQuestions = useMemo(() => {
    if (selectedStatus === 'all') {
      return questions
    }
    return questions.filter(q => q.status === selectedStatus)
  }, [questions, selectedStatus])

  const loadQuestions = useCallback(async () => {
    const abortController = new AbortController()
    
    try {
      setIsLoading(true)
      setError(null)
      
      // Загружаем вопросы и ответы параллельно
      const [allQuestions, allAnswers] = await Promise.all([
        apiService.getAllQuestions(),
        apiService.getAllAnswers()
      ])
      
      // Проверяем, не был ли запрос отменен
      if (abortController.signal.aborted) return
      
      // Объединяем вопросы с их ответами
      const questionsWithAnswers = allQuestions.map(question => ({
        ...question,
        answers: allAnswers.filter(answer => answer.question_id === question.id)
      }))
      
      // Сортируем вопросы
      const sortedQuestions = sortQuestions(questionsWithAnswers)
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
  }, [])

  useEffect(() => {
    loadQuestions()
  }, [loadQuestions])

  // Автоматически выбираем вопрос из URL
  useEffect(() => {
    if (questionId && questions.length > 0) {
      const question = questions.find(q => q.id === questionId)
      if (question) {
        setSelectedQuestion(question)
      }
    }
  }, [questionId, questions])

  // Обновляем выбранное обращение при изменении списка вопросов
  useEffect(() => {
    if (selectedQuestion && questions.length > 0) {
      const updated = questions.find(q => q.id === selectedQuestion.id)
      if (updated) {
        setSelectedQuestion(updated)
      }
    }
  }, [questions])

  const handleAnswerSubmit = useCallback(async (message: string, files: File[]) => {
    if (!selectedQuestion) return

    try {
      setIsSubmitting(true)
      setError(null)
      const response = await apiService.answerQuestion({
        message,
        question_id: selectedQuestion.id
      }, files)
      
      // Показываем сообщение с бэкенда
      if (response.message) {
        setSuccessMessage(response.message)
      }
      
      // Перезагружаем список обращений
      await loadQuestions()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка отправки ответа')
      throw err
    } finally {
      setIsSubmitting(false)
    }
  }, [selectedQuestion, loadQuestions])

  const handleStatusChange = useCallback(async (newStatus: QuestionStatus) => {
    if (!selectedQuestion) return
    
    try {
      setError(null)
      const response = await apiService.changeQuestionStatus(selectedQuestion.id, newStatus)
      
      // Показываем сообщение с бэкенда
      if (response.message) {
        setSuccessMessage(response.message)
      }
      
      // Перезагружаем список обращений
      await loadQuestions()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка изменения статуса')
    }
  }, [selectedQuestion, loadQuestions])

  const handleCloseModal = useCallback(() => {
    setSelectedQuestion(null)
  }, [])

  const handleCloseError = useCallback(() => {
    setError(null)
  }, [])

  const handleCloseSuccess = useCallback(() => {
    setSuccessMessage(null)
  }, [])

  return (
    <div className="admin-page">
      {successMessage && (
        <SuccessNotification 
          message={successMessage} 
          onClose={handleCloseSuccess} 
        />
      )}
      
      <header className="page-header">
        <h1>Панель администратора</h1>
        <button onClick={logout} className="logout-button">Выйти</button>
      </header>

      {error && <ErrorMessage message={error} onClose={handleCloseError} />}

      <div className="page-content">
        <div className="filter-section">
          <StatusFilter 
            selectedStatus={selectedStatus} 
            onStatusChange={setSelectedStatus} 
          />
        </div>

        <div className="questions-grid">
          {isLoading ? (
            <LoadingSpinner />
          ) : filteredQuestions.length === 0 ? (
            <div className="empty-state">
              <p>Обращений с таким статусом не найдено</p>
            </div>
          ) : (
            filteredQuestions.map((question) => (
              <QuestionCard
                key={question.id}
                question={question}
                onClick={() => setSelectedQuestion(question)}
                isSelected={selectedQuestion?.id === question.id}
              />
            ))
          )}
        </div>
      </div>

      <Modal isOpen={selectedQuestion !== null} onClose={handleCloseModal}>
        {selectedQuestion && (
          <>
            <QuestionDetails question={selectedQuestion} onRefresh={loadQuestions} />
            
            <div className="admin-actions">
              <div className="status-change">
                <label>Изменить статус:</label>
                <select 
                  value={selectedQuestion.status}
                  onChange={(e) => handleStatusChange(e.target.value as QuestionStatus)}
                >
                  <option value="active">Активно</option>
                  <option value="answered">Отвечено</option>
                  <option value="closed">Архив</option>
                </select>
              </div>
              
              <AnswerForm 
                onSubmit={handleAnswerSubmit} 
                isLoading={isSubmitting} 
              />
            </div>
          </>
        )}
      </Modal>
    </div>
  )
}
