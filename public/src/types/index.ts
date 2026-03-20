// Информация о пользователе из JWT токена
export interface UserInfo {
  sub: string        // email пользователя
  role: 'user' | 'admin'
  iat: number        // issued at (timestamp)
  exp: number        // expiration (timestamp)
}

// Статусы обращений
export type QuestionStatus = 'active' | 'answered' | 'closed'

// Роли пользователей
export type UserRole = 'user' | 'admin'

// Ответ на обращение
export interface Answer {
  id: string
  date: string       // формат: YYYY-MM-DD
  time: string       // формат: HH:MM:SS
  message: string
  question_id: string
  files: string[]    // имена файлов
}

// Обращение пользователя
export interface Question {
  id: string
  date: string       // формат: YYYY-MM-DD
  time: string       // формат: HH:MM:SS
  name: string
  surname: string
  email: string
  address: string
  message: string
  status: QuestionStatus
  answers: Answer[]
  files: string[]    // имена файлов
}

// Форма создания нового обращения
export interface NewQuestionForm {
  name: string
  surname: string
  email: string
  address: string
  message: string
}

// Данные для создания ответа
export interface NewAnswerData {
  message: string
  question_id: string
}

// Результат валидации формы
export interface ValidationResult {
  isValid: boolean
  errors: string[]
}
