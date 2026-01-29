'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageSquare, Trash2, Plus, Download, FileText, FileIcon } from 'lucide-react'
import type { ChatSession } from '@/types'

interface SessionListProps {
  sessions: ChatSession[]
  selectedSessionId?: string | null
  onSelect: (session: ChatSession) => void
  onDelete: (sessionId: string) => void
  onCreate: () => void
  onExport: (sessionId: string, format: 'md' | 'pdf') => void
  isLoading?: boolean
}

export function SessionList({
  sessions,
  selectedSessionId,
  onSelect,
  onDelete,
  onCreate,
  onExport,
  isLoading = false,
}: SessionListProps) {
  const [exportMenuId, setExportMenuId] = useState<string | null>(null)

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-neutral-500">Chat Sessions</h3>
        <button
          onClick={onCreate}
          className="flex items-center gap-1 rounded-lg px-2 py-1 text-sm text-blue-600 transition-colors hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-950"
        >
          <Plus className="h-3.5 w-3.5" />
          New
        </button>
      </div>

      {isLoading ? (
        <div className="py-4 text-center text-sm text-neutral-400">
          Loading sessions...
        </div>
      ) : sessions.length === 0 ? (
        <div className="py-4 text-center text-sm text-neutral-400">
          No chat history yet
        </div>
      ) : (
        <AnimatePresence>
          {sessions.map((session) => (
            <motion.div
              key={session.id}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`group relative rounded-lg border p-3 transition-colors cursor-pointer ${
                selectedSessionId === session.id
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/30'
                  : 'border-neutral-200 hover:border-neutral-300 dark:border-neutral-800 dark:hover:border-neutral-700'
              }`}
              onClick={() => onSelect(session)}
            >
              <div className="flex items-start gap-2">
                <MessageSquare className="mt-0.5 h-4 w-4 flex-shrink-0 text-neutral-400" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{session.title}</p>
                  <p className="text-xs text-neutral-400">{formatDate(session.updated_at)}</p>
                </div>
              </div>

              {/* Action buttons - visible on hover or when selected */}
              <div className={`absolute right-2 top-2 flex gap-1 ${
                selectedSessionId === session.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
              } transition-opacity`}>
                {/* Export dropdown */}
                <div className="relative">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setExportMenuId(exportMenuId === session.id ? null : session.id)
                    }}
                    className="rounded p-1 text-neutral-400 hover:bg-neutral-200 hover:text-neutral-600 dark:hover:bg-neutral-700"
                    title="Export"
                  >
                    <Download className="h-3.5 w-3.5" />
                  </button>
                  {exportMenuId === session.id && (
                    <div className="absolute right-0 top-full z-10 mt-1 rounded-lg border border-neutral-200 bg-white py-1 shadow-lg dark:border-neutral-700 dark:bg-neutral-800">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onExport(session.id, 'md')
                          setExportMenuId(null)
                        }}
                        className="flex w-full items-center gap-2 px-3 py-1.5 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-700"
                      >
                        <FileText className="h-3.5 w-3.5" />
                        Markdown
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onExport(session.id, 'pdf')
                          setExportMenuId(null)
                        }}
                        className="flex w-full items-center gap-2 px-3 py-1.5 text-sm hover:bg-neutral-100 dark:hover:bg-neutral-700"
                      >
                        <FileIcon className="h-3.5 w-3.5" />
                        PDF
                      </button>
                    </div>
                  )}
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete(session.id)
                  }}
                  className="rounded p-1 text-neutral-400 hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-950"
                  title="Delete"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      )}
    </div>
  )
}
