import type {
  UploadResponse,
  AskRequest,
  AskResponse,
  InterpretRequest,
  InterpretResponse,
  HealthResponse,
  DocumentInfo,
  ChatSession,
  ChatSessionWithMessages,
  CreateSessionRequest,
  AddMessageRequest,
  ChatMessage,
  AskRequestWithSession,
} from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new ApiError(response.status, error.detail || 'Request failed')
  }
  return response.json()
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData,
  })

  return handleResponse<UploadResponse>(response)
}

export async function askQuestion(request: AskRequestWithSession): Promise<AskResponse> {
  const response = await fetch(`${API_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  return handleResponse<AskResponse>(response)
}

export async function interpretInput(request: InterpretRequest): Promise<InterpretResponse> {
  const response = await fetch(`${API_URL}/interpret`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  return handleResponse<InterpretResponse>(response)
}

export async function healthCheck(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/health`)
  return handleResponse<HealthResponse>(response)
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const response = await fetch(`${API_URL}/documents`)
  return handleResponse<DocumentInfo[]>(response)
}

export async function deleteDocument(docId: string): Promise<void> {
  const response = await fetch(`${API_URL}/documents/${docId}`, {
    method: 'DELETE',
  })
  await handleResponse(response)
}

// ==================== Chat Session API ====================

export async function getSessions(docId?: string): Promise<ChatSession[]> {
  const url = docId ? `${API_URL}/sessions?doc_id=${docId}` : `${API_URL}/sessions`
  const response = await fetch(url)
  return handleResponse<ChatSession[]>(response)
}

export async function createSession(request: CreateSessionRequest): Promise<ChatSession> {
  const response = await fetch(`${API_URL}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  return handleResponse<ChatSession>(response)
}

export async function getSession(sessionId: string): Promise<ChatSessionWithMessages> {
  const response = await fetch(`${API_URL}/sessions/${sessionId}`)
  return handleResponse<ChatSessionWithMessages>(response)
}

export async function updateSession(sessionId: string, title: string): Promise<ChatSession> {
  const response = await fetch(`${API_URL}/sessions/${sessionId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  })
  return handleResponse<ChatSession>(response)
}

export async function deleteSession(sessionId: string): Promise<void> {
  const response = await fetch(`${API_URL}/sessions/${sessionId}`, {
    method: 'DELETE',
  })
  await handleResponse(response)
}

export async function addMessage(sessionId: string, request: AddMessageRequest): Promise<ChatMessage> {
  const response = await fetch(`${API_URL}/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  return handleResponse<ChatMessage>(response)
}

export async function exportSession(sessionId: string, format: 'md' | 'pdf' = 'md'): Promise<Blob> {
  const response = await fetch(`${API_URL}/sessions/${sessionId}/export?format=${format}`)
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new ApiError(response.status, error.detail || 'Export failed')
  }
  return response.blob()
}

export { ApiError }
