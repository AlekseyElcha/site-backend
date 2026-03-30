import { useState } from 'react'
import JSZip from 'jszip'
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

  const downloadFile = async (url: string, fileName: string) => {
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const blobUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
    } catch {
      // Если fetch не работает (CORS), открываем в новой вкладке
      window.open(url, '_blank')
    }
  }

  const handleDownloadAll = async () => {
    try {
      setIsDownloading(true)
      // Используем разные эндпоинты в зависимости от типа файлов
      const urls = isAnswer 
        ? await apiService.downloadAllFilesForAnswer(questionId)
        : await apiService.downloadAllFilesForQuestion(questionId)
      
      // Создаём ZIP-архив
      const zip = new JSZip()
      
      // Загружаем все файлы и добавляем в архив
      for (let i = 0; i < urls.length; i++) {
        try {
          const response = await fetch(urls[i])
          const blob = await response.blob()
          const fileName = files[i] || `file-${i}`
          zip.file(fileName, blob)
        } catch (error) {
          console.error(`Ошибка загрузки файла ${files[i]}:`, error)
        }
      }
      
      // Генерируем ZIP и скачиваем
      const zipBlob = await zip.generateAsync({ type: 'blob' })
      const zipUrl = window.URL.createObjectURL(zipBlob)
      const link = document.createElement('a')
      link.href = zipUrl
      link.download = `files-${questionId}.zip`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(zipUrl)
    } catch {
      // silent
    } finally {
      setIsDownloading(false)
    }
  }

  const handleDownloadFile = async (fileName: string) => {
    try {
      const url = await apiService.downloadFileByName(fileName)
      await downloadFile(url, fileName)
    } catch {
      // silent
    }
  }

  // Показываем оригинальное имя: убираем суффикс _uuid.расширение
  const displayName = (fileName: string) => {
    // Формат: originalname_uuid.ext
    // UUID имеет формат xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    const uuidPattern = /_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.[^.]+$/i
    return fileName.replace(uuidPattern, '')
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
