import type { Question } from '../types'
import { formatDate, formatTime, getStatusLabel, getStatusColor } from '../utils/formatting'
import { FileList } from './FileList'
import { ExtraMessageForm } from './ExtraMessageForm'
import './QuestionDetails.css'

interface QuestionDetailsProps {
  question: Question
  onRefresh: () => void
}

export function QuestionDetails({ question, onRefresh }: QuestionDetailsProps) {
  return (
    <article className="question-details" aria-labelledby="modal-title">
      <div className="question-details-header">
        <h2 id="modal-title" className="question-details-title">Детали обращения</h2>
        <span 
          className="question-details-status"
          style={{ backgroundColor: getStatusColor(question.status) }}
          role="status"
          aria-label={`Статус: ${getStatusLabel(question.status)}`}
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
            {question.time ? `${formatDate(question.date, question.time)} ${formatTime(question.date, question.time)}` : formatDate(question.date, '')}
          </span>
        </div>
      </div>

      <section className="question-details-message">
        <h3 className="message-title">Сообщение:</h3>
        <p className="message-text">{question.message}</p>
        <FileList files={question.files} questionId={question.id} isAnswer={false} />
      </section>

      {question.comment && (
        <section className="question-system-comment">
          <h3 className="comment-title">Системный комментарий:</h3>
          <p className="comment-text">{question.comment}</p>
        </section>
      )}

      <section className="question-details-answers" aria-label="Ответы на обращение">
        <h3 className="answers-title">
          Ответы: {question.answers && question.answers.length > 0 && `(${question.answers.length})`}
        </h3>
        
        {!question.answers || question.answers.length === 0 ? (
          <p className="no-answers">Ответов пока нет</p>
        ) : (
          <div className="answers-list">
            {question.answers.map((answer) => (
              <article key={answer.id} className="answer-item">
                <div className="answer-header">
                  <time className="answer-date" dateTime={`${answer.date}T${answer.time}`}>
                    {formatDate(answer.date, answer.time)} {formatTime(answer.date, answer.time)}
                  </time>
                </div>
                <p className="answer-message">{answer.message}</p>
                {answer.files && answer.files.length > 0 && (
                  <FileList files={answer.files} questionId={answer.question_id} isAnswer={true} />
                )}
              </article>
            ))}
          </div>
        )}
      </section>

      {question.extra_messages && question.extra_messages.length > 0 && (
        <section className="question-extra-messages" aria-label="Дополнительные сообщения">
          <h3 className="extra-messages-title">
            Дополнительные сообщения: ({question.extra_messages.length})
          </h3>
          <div className="extra-messages-list">
            {question.extra_messages.map((msg) => (
              <article key={msg.id} className="extra-message-item">
                <div className="extra-message-header">
                  <time className="extra-message-date" dateTime={`${msg.date}T${msg.time}`}>
                    {formatDate(msg.date, msg.time)} {formatTime(msg.date, msg.time)}
                  </time>
                </div>
                <p className="extra-message-text">{msg.message}</p>
                {msg.files && msg.files.length > 0 && (
                  <FileList files={msg.files} questionId={msg.question_id} isAnswer={false} />
                )}
              </article>
            ))}
          </div>
        </section>
      )}

      <ExtraMessageForm questionId={question.id} onSuccess={onRefresh} />
    </article>
  )
}
