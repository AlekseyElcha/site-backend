import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { apiService } from '../services/api'
import { sortQuestions } from '../utils/formatting'
import type { Question, QuestionStatus } from '../types'
import { QuestionCard } from '../components/QuestionCard'
import { QuestionDetails } from '../components/QuestionDetails'
import { AnswerForm } from '../components/AnswerForm'
import { StatusFilter } from '../components/StatusFilter'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorMessage } from '../components/ErrorMessage'
import { SuccessNotification } from '../components/SuccessNotification'
import './AdminPage.css'

export function AdminPage() {
  const { questionId } = useParams<{ questionId?: string }>()
  const { logout } = useAuth()
  const [questions, setQuestions] = useState<Question[]>([])
  const [filteredQuestions, setFilteredQuestions] = useState<Question[]>([])
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null)
  const [selectedStatus, setSelectedStatus] = useState<QuestionStatus | 'all'>('all')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const loadQuestions = async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Загружаем вопросы и ответы параллельно
      const [allQuestions, allAnswers] = await Promise.all([
        apiService.getAllQuestions(),
        apiService.getAllAnswers()
      ])
      
      // Объединяем вопросы с их ответами
      const questionsWithAnswers = allQuestions.map(question => ({
        ...question,
        answers: allAnswers.filter(answer => answer.question_id === question.id)
      }))
      
      // Сортируем вопросы
      const sortedQuestions = sortQuestions(questionsWithAnswers)
      setQuestions(sortedQuestions)
      filterQuestions(sortedQuestions, selectedStatus)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки обращений')
    } finally {
      setIsLoading(false)
    }
  }

  const filterQuestions = (allQuestions: Question[], status: QuestionStatus | 'all') => {
    if (status === 'all') {
      setFilteredQuestions(allQuestions)
    } else {
      setFilteredQuestions(allQuestions.filter(q => q.status === status))
    }
  }

  useEffect(() => {
    loadQuestions()
  }, [])

  useEffect(() => {
    filterQuestions(questions, selectedStatus)
  }, [selectedStatus, questions])

  // Автоматически выбираем вопрос из URL
  useEffect(() => {
    if (questionId && questions.length > 0) {
      const question = questions.find(q => q.id === questionId)
      if (question) {
        setSelectedQuestion(question)
      }
    }
  }, [questionId, questions])

  const handleAnswerSubmit = async (message: string, files: File[]) => {
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
      // Обновляем выбранное обращение из нового списка
      const updated = questions.find(q => q.id === selectedQuestion.id)
      if (updated) {
        setSelectedQuestion(updated)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка отправки ответа')
      throw err
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleStatusChange = async (newStatus: QuestionStatus) => {
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
      // Обновляем выбранное обращение из нового списка
      const updated = questions.find(q => q.id === selectedQuestion.id)
      if (updated) {
        setSelectedQuestion(updated)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка изменения статуса')
    }
  }

  return (
    <div className="admin-page">
      {successMessage && (
        <SuccessNotification 
          message={successMessage} 
          onClose={() => setSuccessMessage(null)} 
        />
      )}
      
      <header className="page-header">
        <h1>Панель администратора</h1>
        <button onClick={logout} className="logout-button">Выйти</button>
      </header>

      {error && <ErrorMessage message={error} onClose={() => setError(null)} />}

      <div className="page-content">
        <aside className="sidebar">
          <StatusFilter 
            selectedStatus={selectedStatus} 
            onStatusChange={setSelectedStatus} 
          />
          
          {isLoading ? (
            <LoadingSpinner />
          ) : filteredQuestions.length === 0 ? (
            <div className="empty-state">
              <p>Обращений с таким статусом не найдено</p>
            </div>
          ) : (
            <div className="questions-list">
              {filteredQuestions.map((question) => (
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
            <>
              <QuestionDetails question={selectedQuestion} />
              
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
          ) : (
            <div className="empty-state">
              <p>Выберите обращение для просмотра и ответа</p>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
