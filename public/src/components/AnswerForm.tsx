import { useState, useRef } from 'react'
import './AnswerForm.css'

interface AnswerFormProps {
  onSubmit: (message: string, files: File[]) => Promise<void>
  isLoading: boolean
}

export function AnswerForm({ onSubmit, isLoading }: AnswerFormProps) {
  const [message, setMessage] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [error, setError] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (message.trim().length < 10) {
      setError('Ответ должен содержать минимум 10 символов')
      return
    }
    
    setError('')
    await onSubmit(message, files)
    setMessage('')
    setFiles([])
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <form className="answer-form" onSubmit={handleSubmit}>
      <h3>Ответить на обращение</h3>
      
      <div className="form-group">
        <textarea
          value={message}
          onChange={(e) => {
            setMessage(e.target.value)
            if (error && e.target.value.trim().length >= 10) {
              setError('')
            }
          }}
          placeholder="Введите ответ (минимум 10 символов)"
          rows={5}
          className={error ? 'error' : ''}
        />
        {error && <span className="error-text">{error}</span>}
      </div>

      <div className="form-group">
        <label className="file-label">Прикрепить файлы (необязательно)</label>
        <input
          type="file"
          multiple
          ref={fileInputRef}
          onChange={(e) => setFiles(Array.from(e.target.files || []))}
          className="file-input"
        />
        {files.length > 0 && (
          <ul className="file-list">
            {files.map((f, i) => (
              <li key={i}>{f.name}</li>
            ))}
          </ul>
        )}
      </div>

      <button 
        type="submit" 
        className="submit-button"
        disabled={message.trim().length < 10 || isLoading}
      >
        {isLoading ? 'Отправка...' : 'Отправить ответ'}
      </button>
    </form>
  )
}
