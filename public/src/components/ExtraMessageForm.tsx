import { useState, useRef, FormEvent } from 'react'
import { apiService } from '../services/api'
import { ErrorMessage } from './ErrorMessage'
import { SuccessNotification } from './SuccessNotification'
import './ExtraMessageForm.css'

interface ExtraMessageFormProps {
  questionId: string
  onSuccess: () => void
}

export function ExtraMessageForm({ questionId, onSuccess }: ExtraMessageFormProps) {
  const [message, setMessage] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showSuccess, setShowSuccess] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    
    // Валидация
    if (message.trim().length < 10) {
      setError('Сообщение должно содержать минимум 10 символов')
      return
    }
    
    setIsSubmitting(true)
    setError(null)
    
    try {
      await apiService.createExtraMessage(questionId, message, files)
      setMessage('')
      setFiles([])
      setShowSuccess(true)
      onSuccess()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка при отправке сообщения')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = Array.from(e.target.files || [])
    setFiles(prev => [...prev, ...newFiles])
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="extra-message-form-container">
      {showSuccess && (
        <SuccessNotification
          message="Дополнительное сообщение успешно отправлено"
          onClose={() => setShowSuccess(false)}
        />
      )}
      
      <form className="extra-message-form" onSubmit={handleSubmit}>
        <h3>Добавить дополнительное сообщение</h3>
        
        {error && <ErrorMessage message={error} onClose={() => setError(null)} />}
        
        <div className="form-group">
          <textarea
            value={message}
            onChange={(e) => {
              setMessage(e.target.value)
              if (error && e.target.value.trim().length >= 10) {
                setError(null)
              }
            }}
            placeholder="Введите сообщение (минимум 10 символов)"
            rows={4}
            className={error ? 'error' : ''}
            disabled={isSubmitting}
          />
        </div>

        <div className="form-group">
          <label className="file-label">Прикрепить файлы (необязательно)</label>
          <input
            type="file"
            multiple
            ref={fileInputRef}
            onChange={handleFileChange}
            className="file-input"
            disabled={isSubmitting}
          />
          {files.length > 0 && (
            <ul className="file-list">
              {files.map((f, i) => (
                <li key={i}>
                  {f.name}
                  <button
                    type="button"
                    className="remove-file-btn"
                    onClick={() => removeFile(i)}
                    aria-label="Удалить файл"
                    disabled={isSubmitting}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={message.trim().length < 10 || isSubmitting}
        >
          {isSubmitting ? 'Отправка...' : 'Отправить сообщение'}
        </button>
      </form>
    </div>
  )
}
