export interface BaseProps {
  className?: string
}

// API Types
export interface UploadResponse {
  doc_id: string
  filename: string
  chunks_created: number
}

export interface AskRequest {
  question: string
  doc_id: string
}

export interface AskResponse {
  answer: string
  source_pages: number[]
}

export type Tone = 'insightful' | 'supportive' | 'analytical' | 'creative' | 'direct'
export type Style = 'concise' | 'detailed' | 'bullet_points' | 'narrative'

export interface InterpretRequest {
  input: string
  tone?: Tone
  style?: Style
  context?: string | null
}

export interface InterpretResponse {
  interpretation: string
  tone: string
  style: string
}

export interface HealthResponse {
  status: string
}

export interface DocumentInfo {
  doc_id: string
  filename: string
  chunks: number
}

// Document state
export interface Document {
  id: string
  filename: string
  chunks: number
  uploadedAt: Date
}

// Chat types
export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sourcePages?: number[]
}
