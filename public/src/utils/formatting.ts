import type { QuestionStatus } from '../types'

// Конвертация даты и времени из UTC в локальный часовой пояс
function convertToLocalTime(dateString: string, timeString: string): Date {
  // Проверяем что параметры валидны
  if (!dateString || !timeString) {
    return new Date()
  }
  
  // Нормализуем время - убираем микросекунды если есть
  let normalizedTime = timeString
  if (timeString.includes('.')) {
    // Обрезаем микросекунды: "17:07:20.086197" -> "17:07:20"
    normalizedTime = timeString.split('.')[0]
  }
  
  // Добавляем секунды если их нет
  if (normalizedTime.split(':').length === 2) {
    normalizedTime = `${normalizedTime}:00`
  }
  
  // Создаем дату в формате ISO (UTC)
  const isoString = `${dateString}T${normalizedTime}Z`
  return new Date(isoString)
}

// Форматирование даты в формат ДД.ММ.ГГГГ с учетом часового пояса
export function formatDate(dateString: string, timeString?: string): string {
  // Проверка на undefined/null
  if (!dateString) {
    return 'Дата не указана'
  }
  
  if (timeString) {
    // Если есть время, конвертируем в локальный часовой пояс
    const localDate = convertToLocalTime(dateString, timeString)
    
    // Проверяем что дата валидна
    if (isNaN(localDate.getTime())) {
      // Если дата невалидна, форматируем без конвертации
      const parts = dateString.split('-')
      if (parts.length !== 3) return dateString
      const [year, month, day] = parts
      return `${day}.${month}.${year}`
    }
    
    const day = String(localDate.getDate()).padStart(2, '0')
    const month = String(localDate.getMonth() + 1).padStart(2, '0')
    const year = localDate.getFullYear()
    return `${day}.${month}.${year}`
  } else {
    // Если времени нет, просто форматируем дату
    const parts = dateString.split('-')
    if (parts.length !== 3) return dateString
    const [year, month, day] = parts
    return `${day}.${month}.${year}`
  }
}

// Форматирование времени в формат ЧЧ:ММ с учетом часового пояса
export function formatTime(dateString: string, timeString: string): string {
  // Проверка на undefined/null
  if (!dateString || !timeString) {
    return '00:00'
  }
  
  const localDate = convertToLocalTime(dateString, timeString)
  
  // Проверяем что дата валидна
  if (isNaN(localDate.getTime())) {
    // Если дата невалидна, форматируем без конвертации
    const parts = timeString.split(':')
    if (parts.length < 2) return timeString
    const [hours, minutes] = parts
    return `${hours}:${minutes}`
  }
  
  const hours = String(localDate.getHours()).padStart(2, '0')
  const minutes = String(localDate.getMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

// Форматирование полной даты и времени
export function formatDateTime(dateString: string, timeString: string): string {
  return `${formatDate(dateString, timeString)} ${formatTime(dateString, timeString)}`
}

// Получение русской метки для статуса обращения
export function getStatusLabel(status: QuestionStatus): string {
  const statusLabels: Record<QuestionStatus, string> = {
    active: 'Активно',
    answered: 'Отвечено',
    closed: 'Архив'
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

// Сортировка вопросов: active (новые→старые) → answered (новые→старые) → closed (новые→старые)
export function sortQuestions<T extends { status: QuestionStatus; date: string; time?: string }>(questions: T[]): T[] {
  const statusOrder: Record<QuestionStatus, number> = {
    active: 1,
    answered: 2,
    closed: 3
  }

  return [...questions].sort((a, b) => {
    // Сначала по статусу
    const statusDiff = statusOrder[a.status] - statusOrder[b.status]
    if (statusDiff !== 0) return statusDiff

    // Внутри статуса — по дате/времени (новые сверху)
    const timeA = a.time ? a.time.split('.')[0] : '00:00:00'
    const timeB = b.time ? b.time.split('.')[0] : '00:00:00'
    const dateA = new Date(`${a.date}T${timeA}Z`)
    const dateB = new Date(`${b.date}T${timeB}Z`)
    return dateB.getTime() - dateA.getTime()
  })
}
