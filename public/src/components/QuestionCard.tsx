import { memo } from 'react'
import type { Question } from '../types'
import { formatDate, formatTime, getStatusLabel, getStatusColor } from '../utils/formatting'
import './QuestionCard.css'

interface QuestionCardProps {
  question: Question
  onClick: () => void
  isSelected?: boolean
}

export const QuestionCard = memo(function QuestionCard({ question, onClick, isSelected }: QuestionCardProps) {
  return (
    <article 
      className={`question-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
      aria-label={`Обращение от ${question.name} ${question.surname}, статус: ${getStatusLabel(question.status)}`}
    >
      <div className="question-card-header">
        <h3 className="question-card-title">
          {question.name} {question.surname}
        </h3>
        <span 
          className="question-card-status"
          style={{ backgroundColor: getStatusColor(question.status) }}
          role="status"
          aria-label={`Статус: ${getStatusLabel(question.status)}`}
        >
          {getStatusLabel(question.status)}
        </span>
      </div>
      
      <div className="question-card-info">
        <p className="question-card-email">{question.email}</p>
        <time className="question-card-date" dateTime={`${question.date}T${question.time}`}>
          {formatDate(question.date, question.time)} {formatTime(question.date, question.time)}
        </time>
      </div>
      
      <p className="question-card-message">
        {question.message.length > 100 
          ? `${question.message.substring(0, 100)}...` 
          : question.message}
      </p>
      
      {question.answers && question.answers.length > 0 && (
        <p className="question-card-answers" aria-label={`Количество ответов: ${question.answers.length}`}>
          Ответов: {question.answers.length}
        </p>
      )}
    </article>
  )
})
