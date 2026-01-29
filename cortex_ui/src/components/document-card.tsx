import { FileText, Trash2 } from 'lucide-react'
import type { Document } from '@/types'

interface DocumentCardProps {
  document: Document
  isSelected: boolean
  onSelect: () => void
  onDelete?: () => void
}

export function DocumentCard({
  document,
  isSelected,
  onSelect,
  onDelete,
}: DocumentCardProps) {
  return (
    <div
      onClick={onSelect}
      className={`group relative cursor-pointer rounded-xl border p-4 transition-all ${
        isSelected
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/30'
          : 'border-neutral-200 hover:border-neutral-300 dark:border-neutral-800 dark:hover:border-neutral-700'
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/50">
          <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
        </div>
        <div className="flex-1 overflow-hidden">
          <p className="truncate font-medium">{document.filename}</p>
          <p className="text-sm text-neutral-500">
            {document.chunks} chunks
          </p>
        </div>
        {onDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete()
            }}
            className="rounded-lg p-1.5 opacity-0 transition-opacity hover:bg-red-100 group-hover:opacity-100 dark:hover:bg-red-900/30"
          >
            <Trash2 className="h-4 w-4 text-red-500" />
          </button>
        )}
      </div>
    </div>
  )
}
