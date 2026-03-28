import { useState, useEffect, useRef } from 'react'
import type { NewQuestionForm } from '../types'
import { validateQuestionForm, isValidEmail } from '../utils/validation'
import './QuestionForm.css'

interface QuestionFormProps {
  onSubmit: (form: NewQuestionForm, files: File[]) => Promise<void>
  isLoading: boolean
  userEmail: string
}

export function QuestionForm({ onSubmit, isLoading, userEmail }: QuestionFormProps) {
  const [form, setForm] = useState<NewQuestionForm>({
    name: '',
    surname: '',
    email: userEmail,
    address: '',
    message: ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [files, setFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Обновляем email при изменении userEmail
  useEffect(() => {
    setForm(prev => ({ ...prev, email: userEmail }))
  }, [userEmail])

  const validateField = (name: keyof NewQuestionForm, value: string) => {
    let error = ''
    
    if (name === 'name' && !value.trim()) error = 'Имя обязательно'
    if (name === 'surname' && !value.trim()) error = 'Фамилия обязательна'
    if (name === 'email' && !isValidEmail(value)) error = 'Некорректный email'
    if (name === 'address' && !value.trim()) error = 'Адрес обязателен'
    if (name === 'message' && value.trim().length < 10) error = 'Минимум 10 символов'
    
    setErrors(prev => ({ ...prev, [name]: error }))
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setForm(prev => ({ ...prev, [name]: value }))
    if (touched[name]) {
      validateField(name as keyof NewQuestionForm, value)
    }
  }

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setTouched(prev => ({ ...prev, [name]: true }))
    validateField(name as keyof NewQuestionForm, value)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const validation = validateQuestionForm(form)
    if (!validation.isValid) {
      const errorMap: Record<string, string> = {}
      validation.errors.forEach(err => {
        if (err.includes('Имя')) errorMap.name = err
        if (err.includes('Фамилия')) errorMap.surname = err
        if (err.includes('email')) errorMap.email = err
        if (err.includes('Адрес')) errorMap.address = err
        if (err.includes('Сообщение')) errorMap.message = err
      })
      setErrors(errorMap)
      return
    }
    
    await onSubmit(form, files)
    setForm({ name: '', surname: '', email: userEmail, address: '', message: '' })
    setErrors({})
    setTouched({})
    setFiles([])
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = Array.from(e.target.files || [])
    setFiles(prev => [...prev, ...newFiles])
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const isFormValid = validateQuestionForm(form).isValid

  return (
    <form className="question-form" onSubmit={handleSubmit}>
      <h3>Новое обращение</h3>
      
      <div className="form-group">
        <input
          type="text"
          name="name"
          value={form.name}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Имя"
          className={errors.name && touched.name ? 'error' : ''}
        />
        {errors.name && touched.name && <span className="error-text">{errors.name}</span>}
      </div>

      <div className="form-group">
        <input
          type="text"
          name="surname"
          value={form.surname}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Фамилия"
          className={errors.surname && touched.surname ? 'error' : ''}
        />
        {errors.surname && touched.surname && <span className="error-text">{errors.surname}</span>}
      </div>

      <div className="form-group">
        <input
          type="email"
          name="email"
          value={form.email}
          placeholder="Email"
          disabled
          className="disabled"
        />
      </div>

      <div className="form-group">
        <input
          type="text"
          name="address"
          value={form.address}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Адрес"
          className={errors.address && touched.address ? 'error' : ''}
        />
        {errors.address && touched.address && <span className="error-text">{errors.address}</span>}
      </div>

      <div className="form-group">
        <textarea
          name="message"
          value={form.message}
          onChange={handleChange}
          onBlur={handleBlur}
          placeholder="Сообщение (минимум 10 символов)"
          rows={4}
          className={errors.message && touched.message ? 'error' : ''}
        />
        {errors.message && touched.message && <span className="error-text">{errors.message}</span>}
      </div>

      <div className="form-group">
        <label className="file-label">Прикрепить файлы (необязательно)</label>
        <input
          type="file"
          multiple
          ref={fileInputRef}
          onChange={handleFileChange}
          className="file-input"
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
        disabled={!isFormValid || isLoading}
      >
        {isLoading ? 'Отправка...' : 'Отправить обращение'}
      </button>
    </form>
  )
}
