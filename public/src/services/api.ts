import type { UserInfo, Question, NewQuestionForm, NewAnswerData, Answer, QuestionData } from '../types'

class APIService {
  private baseURL: string

  constructor() {
    this.baseURL = ''  // Прокси настроен в vite.credentials.ts
  }

  // Обработка ответа от API
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Ошибка сервера' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }
    return response.json()
  }

  // Auth endpoints
  async getAuthCode(email: string): Promise<string> {
    const formData = new URLSearchParams()
    formData.append('email', email)
    
    const response = await fetch(`${this.baseURL}/auth/get_auth_code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      credentials: 'include',
      body: formData
    })
    const data = await this.handleResponse<string>(response)
    return data
  }

  async login(email: string, code: string): Promise<{ access_token: string }> {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, auth_code: code })
    })
    return this.handleResponse<{ access_token: string }>(response)
  }

  async getUserInfo(): Promise<UserInfo> {
    const response = await fetch(`${this.baseURL}/auth/user_info`, {
      method: 'GET',
      credentials: 'include'
    })
    return this.handleResponse<UserInfo>(response)
  }

  async logout(): Promise<void> {
    const response = await fetch(`${this.baseURL}/auth/logout`, {
      method: 'GET',
      credentials: 'include'
    })
    await this.handleResponse<void>(response)
  }

  async refreshToken(): Promise<{ access_token: string }> {
    const response = await fetch(`${this.baseURL}/auth/refresh`, {
      method: 'POST',
      credentials: 'include'
    })
    return this.handleResponse<{ access_token: string }>(response)
  }

  // Questions endpoints
  async createQuestion(question: NewQuestionForm, files?: File[]): Promise<void> {
    const formData = new FormData()
    formData.append('question', JSON.stringify(question))
    if (files && files.length > 0) {
      files.forEach(file => formData.append('files', file))
    }
    const response = await fetch(`${this.baseURL}/questions/create_question`, {
      method: 'POST',
      credentials: 'include',
      body: formData
    })
    return this.handleResponse<void>(response)
  }

  async getAllQuestions(): Promise<Question[]> {
    const response = await fetch(`${this.baseURL}/handle_questions/all_questions`, {
      method: 'GET',
      credentials: 'include'
    })
    return this.handleResponse<Question[]>(response)
  }

  async answerQuestion(answer: NewAnswerData, files?: File[]): Promise<{ message: string }> {
    const formData = new FormData()
    formData.append('answer', JSON.stringify(answer))
    if (files && files.length > 0) {
      files.forEach(file => formData.append('files', file))
    }
    const response = await fetch(`${this.baseURL}/handle_questions/answer_question`, {
      method: 'POST',
      credentials: 'include',
      body: formData
    })
    return this.handleResponse<{ message: string }>(response)
  }

  async createExtraMessage(questionId: string, message: string, files?: File[]): Promise<{ message: string }> {
    const formData = new FormData()
    formData.append('question_id', questionId)
    formData.append('message', JSON.stringify({ question_id: questionId, message }))
    if (files && files.length > 0) {
      files.forEach(file => formData.append('files', file))
    }
    const response = await fetch(`${this.baseURL}/handle_questions/create_extra_message`, {
      method: 'POST',
      credentials: 'include',
      body: formData
    })
    return this.handleResponse<{ message: string }>(response)
  }

  async changeQuestionStatus(questionId: string, newStatus: string): Promise<{ message: string }> {
    const response = await fetch(`${this.baseURL}/handle_questions/change_question_status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ question_id: questionId, new_status: newStatus })
    })
    return this.handleResponse<{ message: string }>(response)
  }

  async getAllAnswers(): Promise<Answer[]> {
    const response = await fetch(`${this.baseURL}/handle_questions/answers_for_all_questions`, {
      method: 'GET',
      credentials: 'include'
    })
    return this.handleResponse<Answer[]>(response)
  }

  async getAnswersForQuestion(questionId: string): Promise<Answer[]> {
    const response = await fetch(`${this.baseURL}/handle_questions/answers_for_question/${questionId}`, {
      method: 'GET',
      credentials: 'include'
    })
    return this.handleResponse<Answer[]>(response)
  }

  async getQuestionData(questionId: string): Promise<QuestionData> {
    const response = await fetch(`${this.baseURL}/handle_questions/question_data/${questionId}`, {
      method: 'GET',
      credentials: 'include'
    })
    return this.handleResponse<QuestionData>(response)
  }

  async downloadAllFilesForQuestion(questionId: string): Promise<string[]> {
    const response = await fetch(`${this.baseURL}/files/download_all_files_for_question/${questionId}`, {
      method: 'PUT',
      credentials: 'include'
    })
    return this.handleResponse<string[]>(response)
  }

  async downloadAllFilesForAnswer(questionId: string): Promise<string[]> {
    const response = await fetch(`${this.baseURL}/files/download_all_files_for_answer/${questionId}`, {
      method: 'PUT',
      credentials: 'include'
    })
    return this.handleResponse<string[]>(response)
  }

  async downloadFileByName(fileName: string): Promise<string> {
    const response = await fetch(`${this.baseURL}/files/download_file_by_name`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ file_name: fileName })
    })
    return this.handleResponse<string>(response)
  }
}

export const apiService = new APIService()
