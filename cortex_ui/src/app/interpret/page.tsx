'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Loader2, Sparkles, Copy, Check, RotateCcw } from 'lucide-react'
import { ToneSelector } from '@/components/tone-selector'
import { interpretInput } from '@/lib/api'
import type { Tone, Style } from '@/types'

export default function InterpretPage() {
  const [input, setInput] = useState('')
  const [context, setContext] = useState('')
  const [tone, setTone] = useState<Tone>('insightful')
  const [style, setStyle] = useState<Style>('concise')
  const [interpretation, setInterpretation] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const handleClear = useCallback(() => {
    setInput('')
    setContext('')
    setInterpretation(null)
    setError(null)
    setTone('insightful')
    setStyle('concise')
  }, [])

  const handleCopy = useCallback(async () => {
    if (!interpretation) return
    await navigator.clipboard.writeText(interpretation)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [interpretation])

  const handleInterpret = useCallback(async () => {
    if (!input.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await interpretInput({
        input: input.trim(),
        tone,
        style,
        context: context.trim() || null,
      })
      setInterpretation(response.interpretation)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Interpretation failed')
    } finally {
      setIsLoading(false)
    }
  }, [input, tone, style, context])

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold">Input Interpreter</h1>
        <p className="mt-2 text-neutral-600 dark:text-neutral-400">
          Get thoughtful interpretations of your ideas, thoughts, and experiences
        </p>
      </motion.div>

      <div className="mt-8 space-y-6">
        {/* Tone & Style Selector */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl border border-neutral-200 p-6 dark:border-neutral-800"
        >
          <ToneSelector
            tone={tone}
            style={style}
            onToneChange={setTone}
            onStyleChange={setStyle}
          />
        </motion.div>

        {/* Input Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          <div>
            <label className="mb-2 block text-sm font-medium">
              What would you like to interpret?
            </label>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Enter your thought, idea, dream, or experience..."
              rows={4}
              className="w-full rounded-xl border border-neutral-300 bg-white px-4 py-3 text-sm outline-none transition-colors placeholder:text-neutral-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium">
              Context{' '}
              <span className="font-normal text-neutral-400">(optional)</span>
            </label>
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Add any relevant background or context..."
              rows={2}
              className="w-full rounded-xl border border-neutral-300 bg-white px-4 py-3 text-sm outline-none transition-colors placeholder:text-neutral-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleClear}
              disabled={isLoading}
              className="flex items-center justify-center gap-2 rounded-xl border border-neutral-300 px-4 py-3 font-medium transition-colors hover:bg-neutral-50 disabled:opacity-50 dark:border-neutral-700 dark:hover:bg-neutral-800"
            >
              <RotateCcw className="h-4 w-4" />
              Clear
            </button>
            <button
              onClick={handleInterpret}
              disabled={!input.trim() || isLoading}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-3 font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Interpreting...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  Interpret
                </>
              )}
            </button>
          </div>
        </motion.div>

        {/* Error */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-xl bg-red-50 px-4 py-3 text-red-600 dark:bg-red-950 dark:text-red-400"
          >
            {error}
          </motion.div>
        )}

        {/* Result */}
        {interpretation && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border border-neutral-200 p-6 dark:border-neutral-800"
          >
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-500" />
                <h3 className="font-semibold">Interpretation</h3>
              </div>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-neutral-500 transition-colors hover:bg-neutral-100 dark:hover:bg-neutral-800"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4 text-green-500" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <div className="prose prose-neutral dark:prose-invert max-w-none">
              <p className="whitespace-pre-wrap leading-relaxed">
                {interpretation}
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
