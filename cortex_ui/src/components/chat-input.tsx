'use client'

import { useState } from 'react'
import { Send, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ChatInputProps {
  onSend: (message: string) => Promise<void>
  placeholder?: string
  disabled?: boolean
}

export function ChatInput({
  onSend,
  placeholder = 'Type your message...',
  disabled,
}: ChatInputProps) {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading || disabled) return

    const message = input.trim()
    setInput('')
    setIsLoading(true)

    try {
      await onSend(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={placeholder}
        disabled={disabled || isLoading}
        className={cn(
          'flex-1 rounded-xl border border-neutral-300 bg-white px-4 py-3 text-sm outline-none transition-colors',
          'placeholder:text-neutral-400',
          'focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20',
          'dark:border-neutral-700 dark:bg-neutral-900 dark:text-white',
          'disabled:opacity-50'
        )}
      />
      <button
        type="submit"
        disabled={!input.trim() || isLoading || disabled}
        className={cn(
          'flex items-center justify-center rounded-xl bg-blue-600 px-4 text-white transition-colors',
          'hover:bg-blue-700',
          'disabled:opacity-50 disabled:hover:bg-blue-600'
        )}
      >
        {isLoading ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <Send className="h-5 w-5" />
        )}
      </button>
    </form>
  )
}
