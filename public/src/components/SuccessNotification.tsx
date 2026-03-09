import { useEffect } from 'react'
import './SuccessNotification.css'

interface SuccessNotificationProps {
  message: string
  onClose: () => void
  duration?: number
}

export function SuccessNotification({ message, onClose, duration = 3000 }: SuccessNotificationProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose()
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, onClose])

  return (
    <div className="success-notification">
      <span className="success-icon">✓</span>
      <span className="success-text">{message}</span>
      <button className="success-close" onClick={onClose} aria-label="Закрыть">
        ×
      </button>
    </div>
  )
}
