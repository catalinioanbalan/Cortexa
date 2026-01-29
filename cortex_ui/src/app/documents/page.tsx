'use client'

import { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Trash2, RefreshCw } from 'lucide-react'
import { FileUpload } from '@/components/file-upload'
import { ChatMessage } from '@/components/chat-message'
import { ChatInput } from '@/components/chat-input'
import { DocumentCard } from '@/components/document-card'
import { SessionList } from '@/components/session-list'
import {
  uploadDocument,
  askQuestion,
  listDocuments,
  deleteDocument,
  getSessions,
  createSession,
  getSession,
  deleteSession,
  exportSession,
} from '@/lib/api'
import type { Document, Message, ChatSession } from '@/types'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Session state
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [isLoadingSessions, setIsLoadingSessions] = useState(false)

  const fetchDocuments = useCallback(async () => {
    try {
      setIsLoading(true)
      const docs = await listDocuments()
      setDocuments(docs.map(d => ({
        id: d.doc_id,
        filename: d.filename,
        chunks: d.chunks,
        uploadedAt: new Date(),
      })))
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Fetch sessions for a document and auto-load the most recent one
  const fetchSessions = useCallback(async (docId: string, autoLoadRecent = true) => {
    try {
      setIsLoadingSessions(true)
      const docSessions = await getSessions(docId)
      setSessions(docSessions)
      
      // Auto-load the most recent session if exists
      if (autoLoadRecent && docSessions.length > 0) {
        const mostRecent = docSessions[0] // Sessions are sorted by updated_at DESC
        const sessionWithMessages = await getSession(mostRecent.id)
        setCurrentSessionId(mostRecent.id)
        setMessages(sessionWithMessages.messages.map(m => ({
          id: m.id,
          role: m.role,
          content: m.content,
          citations: m.citations,
        })))
      }
    } catch (err) {
      console.error('Failed to fetch sessions:', err)
      setSessions([])
    } finally {
      setIsLoadingSessions(false)
    }
  }, [])

  // Load session messages
  const loadSession = useCallback(async (session: ChatSession) => {
    try {
      const sessionWithMessages = await getSession(session.id)
      setCurrentSessionId(session.id)
      setMessages(sessionWithMessages.messages.map(m => ({
        id: m.id,
        role: m.role,
        content: m.content,
        citations: m.citations,
      })))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load session')
    }
  }, [])

  // Create a new session
  const handleCreateSession = useCallback(async () => {
    if (!selectedDoc) return
    try {
      const session = await createSession({
        doc_id: selectedDoc.id,
        title: `Chat with ${selectedDoc.filename}`,
      })
      setSessions(prev => [session, ...prev])
      setCurrentSessionId(session.id)
      setMessages([])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create session')
    }
  }, [selectedDoc])

  // Delete a session
  const handleDeleteSession = useCallback(async (sessionId: string) => {
    try {
      await deleteSession(sessionId)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      if (currentSessionId === sessionId) {
        setCurrentSessionId(null)
        setMessages([])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete session')
    }
  }, [currentSessionId])

  // Export a session
  const handleExportSession = useCallback(async (sessionId: string, format: 'md' | 'pdf') => {
    try {
      const blob = await exportSession(sessionId, format)
      const session = sessions.find(s => s.id === sessionId)
      const filename = `${session?.title || 'chat'}.${format}`
      
      // Create download link
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export session')
    }
  }, [sessions])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  // Fetch sessions when document is selected
  useEffect(() => {
    if (selectedDoc) {
      fetchSessions(selectedDoc.id)
    } else {
      setSessions([])
      setCurrentSessionId(null)
    }
  }, [selectedDoc, fetchSessions])

  const handleUpload = useCallback(async (file: File) => {
    setError(null)
    const response = await uploadDocument(file)
    const newDoc: Document = {
      id: response.doc_id,
      filename: response.filename,
      chunks: response.chunks_created,
      uploadedAt: new Date(),
    }
    setDocuments((prev) => [...prev, newDoc])
    setSelectedDoc(newDoc)
    setMessages([])
    setCurrentSessionId(null)
    setSessions([])
  }, [])

  const handleAsk = useCallback(async (question: string) => {
    if (!selectedDoc) return

    // Auto-create session if none exists
    let sessionId = currentSessionId
    if (!sessionId) {
      try {
        const session = await createSession({
          doc_id: selectedDoc.id,
          title: question.slice(0, 50) + (question.length > 50 ? '...' : ''),
        })
        sessionId = session.id
        setCurrentSessionId(session.id)
        setSessions(prev => [session, ...prev])
      } catch (err) {
        console.error('Failed to create session:', err)
        // Continue without session persistence
      }
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      const response = await askQuestion({
        question,
        doc_id: selectedDoc.id,
        session_id: sessionId || undefined,
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get answer')
    }
  }, [selectedDoc, currentSessionId])

  const handleDeleteDoc = useCallback(async (docId: string) => {
    try {
      await deleteDocument(docId)
      setDocuments((prev) => prev.filter((d) => d.id !== docId))
      if (selectedDoc?.id === docId) {
        setSelectedDoc(null)
        setMessages([])
        setSessions([])
        setCurrentSessionId(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete document')
    }
  }, [selectedDoc])

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold">Document Q&A</h1>
        <p className="mt-2 text-neutral-600 dark:text-neutral-400">
          Upload documents and ask questions about their content
        </p>
      </motion.div>

      <div className="mt-8 grid gap-8 lg:grid-cols-[300px_1fr]">
        {/* Sidebar */}
        <div className="space-y-6">
          <FileUpload onUpload={handleUpload} />

          {(documents.length > 0 || isLoading) && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-neutral-500">
                  Your Documents
                </h3>
                <button
                  onClick={fetchDocuments}
                  disabled={isLoading}
                  className="rounded-lg p-1.5 text-neutral-400 transition-colors hover:bg-neutral-100 hover:text-neutral-600 dark:hover:bg-neutral-800"
                  title="Refresh"
                >
                  <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>
              <AnimatePresence>
                {documents.map((doc) => (
                  <motion.div
                    key={doc.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <DocumentCard
                      document={doc}
                      isSelected={selectedDoc?.id === doc.id}
                      onSelect={() => {
                        if (selectedDoc?.id !== doc.id) {
                          setSelectedDoc(doc)
                          // Don't clear messages here - fetchSessions will auto-load
                        }
                      }}
                      onDelete={() => handleDeleteDoc(doc.id)}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}

          {/* Session List */}
          {selectedDoc && (
            <SessionList
              sessions={sessions}
              selectedSessionId={currentSessionId}
              onSelect={loadSession}
              onDelete={handleDeleteSession}
              onCreate={handleCreateSession}
              onExport={handleExportSession}
              isLoading={isLoadingSessions}
            />
          )}
        </div>

        {/* Chat Area */}
        <div className="flex flex-col rounded-2xl border border-neutral-200 dark:border-neutral-800">
          {selectedDoc ? (
            <>
              <div className="flex items-center justify-between border-b border-neutral-200 px-4 py-3 dark:border-neutral-800">
                <div>
                  <p className="font-medium">{selectedDoc.filename}</p>
                  <p className="text-sm text-neutral-500">
                    {selectedDoc.chunks} chunks indexed
                    {currentSessionId && ' • Session active'}
                  </p>
                </div>
                <button
                    onClick={() => {
                      setMessages([])
                      setCurrentSessionId(null)
                    }}
                    className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-neutral-500 transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  >
                    <Trash2 className="h-4 w-4" />
                    New Chat
                  </button>
              </div>

              <div className="flex-1 space-y-4 overflow-y-auto p-4" style={{ minHeight: '400px' }}>
                {messages.length === 0 ? (
                  <div className="flex h-full items-center justify-center text-neutral-400">
                    <p>Ask a question about this document</p>
                  </div>
                ) : (
                  messages.map((msg) => (
                    <ChatMessage key={msg.id} message={msg} />
                  ))
                )}
              </div>

              {error && (
                <div className="mx-4 mb-2 rounded-lg bg-red-50 px-4 py-2 text-sm text-red-600 dark:bg-red-950 dark:text-red-400">
                  {error}
                </div>
              )}

              <div className="border-t border-neutral-200 p-4 dark:border-neutral-800">
                <ChatInput
                  onSend={handleAsk}
                  placeholder="Ask a question about this document..."
                />
              </div>
            </>
          ) : (
            <div className="flex h-96 items-center justify-center text-neutral-400">
              <p>Upload or select a document to start asking questions</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
