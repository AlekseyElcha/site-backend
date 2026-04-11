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
  files: string[] | null    // имена файлов (может быть null)
}

// Дополнительное сообщение к обращению
export interface ExtraMessage {
  id: string
  date: string       // формат: YYYY-MM-DD
  time: string       // формат: HH:MM:SS
  message: string
  question_id: string
  files: string[] | null    // имена файлов (может быть null)
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
  comment?: string   // системный комментарий (опционально)
  extra_messages?: ExtraMessage[]  // дополнительные сообщения (опционально)
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

// Данные для создания дополнительного сообщения
export interface NewExtraMessageData {
  question_id: string
  message: string
}

// Полные данные по вопросу (новый эндпоинт)
export interface QuestionData {
  question: Omit<Question, 'answers' | 'extra_messages'>
  answers: Answer[]
  extra_messages: ExtraMessage[]
}

// Результат валидации формы
export interface ValidationResult {
  isValid: boolean
  errors: string[]
}
