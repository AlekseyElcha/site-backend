import type { QuestionStatus } from '../types'

// Форматирование даты в формат ДД.ММ.ГГГГ
export function formatDate(dateString: string): string {
  const [year, month, day] = dateString.split('-')
  return `${day}.${month}.${year}`
}

// Форматирование времени в формат ЧЧ:ММ
export function formatTime(timeString: string): string {
  const [hours, minutes] = timeString.split(':')
  return `${hours}:${minutes}`
}

// Получение русской метки для статуса обращения
export function getStatusLabel(status: QuestionStatus): string {
  const statusLabels: Record<QuestionStatus, string> = {
    active: 'Активно',
    answered: 'Отвечено',
    closed: 'Закрыто'
  }
  return statusLabels[status] || status
}

// Получение цвета для статуса
export function getStatusColor(status: QuestionStatus): string {
  const statusColors: Record<QuestionStatus, string> = {
    active: '#ea580c',    // warning
    answered: '#16a34a',  // success
    closed: '#6b7280'     // secondary
  }
  return statusColors[status] || '#6b7280'
}
