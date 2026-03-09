import type { Question } from '../types'
import { formatDate, formatTime, getStatusLabel, getStatusColor } from '../utils/formatting'
import './QuestionDetails.css'

interface QuestionDetailsProps {
  question: Question
}

export function QuestionDetails({ question }: QuestionDetailsProps) {
  return (
    <div className="question-details">
      <div className="question-details-header">
        <h2 className="question-details-title">Детали обращения</h2>
        <span 
          className="question-details-status"
          style={{ backgroundColor: getStatusColor(question.status) }}
        >
          {getStatusLabel(question.status)}
        </span>
      </div>

      <div className="question-details-info">
        <div className="info-row">
          <span className="info-label">Имя:</span>
          <span className="info-value">{question.name}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Фамилия:</span>
          <span className="info-value">{question.surname}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Email:</span>
          <span className="info-value">{question.email}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Адрес:</span>
          <span className="info-value">{question.address}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Дата:</span>
          <span className="info-value">
            {formatDate(question.date)} {formatTime(question.time)}
          </span>
        </div>
      </div>

      <div className="question-details-message">
        <h3 className="message-title">Сообщение:</h3>
        <p className="message-text">{question.message}</p>
      </div>

      <div className="question-details-answers">
        <h3 className="answers-title">
          Ответы {question.answers && question.answers.length > 0 && `(${question.answers.length})`}
        </h3>
        
        {!question.answers || question.answers.length === 0 ? (
          <p className="no-answers">Ответов пока нет</p>
        ) : (
          <div className="answers-list">
            {question.answers.map((answer) => (
              <div key={answer.id} className="answer-item">
                <div className="answer-header">
                  <span className="answer-date">
                    {formatDate(answer.date)} {formatTime(answer.time)}
                  </span>
                </div>
                <p className="answer-message">{answer.message}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
