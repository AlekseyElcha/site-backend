import { useState } from 'react'
import { apiService } from '../services/api'
import './FileList.css'

interface FileListProps {
  files: string[]
  questionId: string
  isAnswer?: boolean  // true если это файлы из ответа, false если из вопроса
}

export function FileList({ files, questionId, isAnswer = false }: FileListProps) {
  const [isDownloading, setIsDownloading] = useState(false)

  if (!files || files.length === 0) return null

  const handleDownloadAll = async () => {
    try {
      setIsDownloading(true)
      
      // Используем разные эндпоинты в зависимости от типа файлов
      const urls = isAnswer 
        ? await apiService.downloadAllFilesForAnswer(questionId)
        : await apiService.downloadAllFilesForQuestion(questionId)
      
      if (!urls || urls.length === 0) {
        alert('Нет файлов для скачивания')
        return
      }
      
      // Скачиваем файлы по очереди, открывая в новых вкладках
      for (let i = 0; i < urls.length; i++) {
        // Небольшая задержка между открытием вкладок
        if (i > 0) {
          await new Promise(resolve => setTimeout(resolve, 300))
        }
        window.open(urls[i], '_blank')
      }
    } catch (error) {
      console.error('Ошибка загрузки файлов:', error)
      alert(`Ошибка: ${error instanceof Error ? error.message : 'Неизвестная ошибка'}`)
    } finally {
      setIsDownloading(false)
    }
  }

  const handleDownloadFile = async (fileName: string) => {
    try {
      const url = await apiService.downloadFileByName(fileName)
      // Открываем URL в новой вкладке - браузер сам скачает файл
      window.open(url, '_blank')
    } catch (error) {
      console.error('Ошибка скачивания файла:', error)
      alert(`Ошибка скачивания: ${error instanceof Error ? error.message : 'Неизвестная ошибка'}`)
    }
  }

  // Показываем оригинальное имя: убираем суффикс _uuid.расширение или _uuid_answer.расширение
  const displayName = (fileName: string) => {
    // Формат для вопросов: originalname_uuid.ext
    // Формат для ответов: originalname_uuid_answer.ext
    // UUID имеет формат xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    
    // Сначала пробуем формат с _answer
    const answerPattern = /_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_answer\.[^.]+$/i
    if (answerPattern.test(fileName)) {
      return fileName.replace(answerPattern, (match) => {
        // Извлекаем расширение из match
        const ext = match.substring(match.lastIndexOf('.'))
        return ext
      })
    }
    
    // Если не _answer, то обычный формат
    const questionPattern = /_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[^.]+$/i
    return fileName.replace(questionPattern, (match) => {
      const ext = match.substring(match.lastIndexOf('.'))
      return ext
    })
  }

  return (
    <div className="file-list-section">
      <div className="file-list-header">
        <span className="file-list-title">Файлы ({files.length})</span>
        <button
          className="download-all-btn"
          onClick={handleDownloadAll}
          disabled={isDownloading}
        >
          {isDownloading ? 'Загрузка...' : 'Скачать все'}
        </button>
      </div>
      <ul className="file-list-items">
        {files.map((fileName, i) => (
          <li key={i}>
            <button
              className="file-link"
              onClick={() => handleDownloadFile(fileName)}
            >
              📎 {displayName(fileName)}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
