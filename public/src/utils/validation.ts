import type { NewQuestionForm, ValidationResult } from '../types'

// Проверка валидности email адреса
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Проверка валидности 6-значного кода
export function isValidCode(code: string): boolean {
  const codeRegex = /^\d{6}$/
  return codeRegex.test(code)
}

// Проверка валидности UUID
export function isValidUUID(uuid: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  return uuidRegex.test(uuid)
}

// Валидация формы создания обращения
export function validateQuestionForm(form: NewQuestionForm): ValidationResult {
  const errors: string[] = []

  // Проверка имени
  if (!form.name || form.name.trim().length === 0) {
    errors.push('Имя обязательно для заполнения')
  }

  // Проверка фамилии
  if (!form.surname || form.surname.trim().length === 0) {
    errors.push('Фамилия обязательна для заполнения')
  }

  // Проверка email
  if (!form.email || !isValidEmail(form.email)) {
    errors.push('Введите корректный email адрес')
  }

  // Проверка адреса
  if (!form.address || form.address.trim().length === 0) {
    errors.push('Адрес обязателен для заполнения')
  }

  // Проверка сообщения
  if (!form.message || form.message.trim().length < 10) {
    errors.push('Сообщение должно содержать минимум 10 символов')
  }

  return {
    isValid: errors.length === 0,
    errors
  }
}
