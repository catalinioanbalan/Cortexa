'use client'

import { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Trash2, RefreshCw } from 'lucide-react'
import { FileUpload } from '@/components/file-upload'
import { ChatMessage } from '@/components/chat-message'
import { ChatInput } from '@/components/chat-input'
import { DocumentCard } from '@/components/document-card'
import { uploadDocument, askQuestion, listDocuments, deleteDocument } from '@/lib/api'
import type { Document, Message } from '@/types'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

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

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

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
  }, [])

  const handleAsk = useCallback(async (question: string) => {
    if (!selectedDoc) return

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
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sourcePages: response.source_pages,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get answer')
    }
  }, [selectedDoc])

  const handleDeleteDoc = useCallback(async (docId: string) => {
    try {
      await deleteDocument(docId)
      setDocuments((prev) => prev.filter((d) => d.id !== docId))
      if (selectedDoc?.id === docId) {
        setSelectedDoc(null)
        setMessages([])
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
                        setSelectedDoc(doc)
                        setMessages([])
                      }}
                      onDelete={() => handleDeleteDoc(doc.id)}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
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
                  </p>
                </div>
                {messages.length > 0 && (
                  <button
                    onClick={() => setMessages([])}
                    className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-neutral-500 transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  >
                    <Trash2 className="h-4 w-4" />
                    Clear Chat
                  </button>
                )}
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
