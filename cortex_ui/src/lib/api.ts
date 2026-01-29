import type {
  UploadResponse,
  AskRequest,
  AskResponse,
  InterpretRequest,
  InterpretResponse,
  HealthResponse,
  DocumentInfo,
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

export async function askQuestion(request: AskRequest): Promise<AskResponse> {
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

export { ApiError }
