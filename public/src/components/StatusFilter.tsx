import type { QuestionStatus } from '../types'
import { getStatusLabel } from '../utils/formatting'
import './StatusFilter.css'

interface StatusFilterProps {
  selectedStatus: QuestionStatus | 'all'
  onStatusChange: (status: QuestionStatus | 'all') => void
}

export function StatusFilter({ selectedStatus, onStatusChange }: StatusFilterProps) {
  const statuses: Array<QuestionStatus | 'all'> = ['all', 'active', 'answered', 'closed']

  return (
    <div className="status-filter" role="group" aria-label="Фильтр по статусу">
      {statuses.map((status) => (
        <button
          key={status}
          className={`filter-button ${selectedStatus === status ? 'active' : ''}`}
          onClick={() => onStatusChange(status)}
          aria-pressed={selectedStatus === status}
          type="button"
        >
          {status === 'all' ? 'Все' : getStatusLabel(status)}
        </button>
      ))}
    </div>
  )
}
