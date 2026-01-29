'use client'

import { cn } from '@/lib/utils'
import type { Tone, Style } from '@/types'

interface ToneSelectorProps {
  tone: Tone
  style: Style
  onToneChange: (tone: Tone) => void
  onStyleChange: (style: Style) => void
}

const TONES: { value: Tone; label: string; description: string }[] = [
  { value: 'insightful', label: 'Insightful', description: 'Deep, thoughtful analysis' },
  { value: 'supportive', label: 'Supportive', description: 'Warm and encouraging' },
  { value: 'analytical', label: 'Analytical', description: 'Logical and objective' },
  { value: 'creative', label: 'Creative', description: 'Imaginative exploration' },
  { value: 'direct', label: 'Direct', description: 'Concise and straightforward' },
]

const STYLES: { value: Style; label: string }[] = [
  { value: 'concise', label: 'Concise' },
  { value: 'detailed', label: 'Detailed' },
  { value: 'bullet_points', label: 'Bullet Points' },
  { value: 'narrative', label: 'Narrative' },
]

export function ToneSelector({
  tone,
  style,
  onToneChange,
  onStyleChange,
}: ToneSelectorProps) {
  return (
    <div className="space-y-4">
      <div>
        <label className="mb-2 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Tone
        </label>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
          {TONES.map((t) => (
            <button
              key={t.value}
              onClick={() => onToneChange(t.value)}
              className={cn(
                'rounded-lg border px-3 py-2 text-left text-sm transition-colors',
                tone === t.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                  : 'border-neutral-200 hover:border-neutral-300 dark:border-neutral-700 dark:hover:border-neutral-600'
              )}
            >
              <div className="font-medium">{t.label}</div>
              <div className="text-xs opacity-70">{t.description}</div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Style
        </label>
        <div className="flex flex-wrap gap-2">
          {STYLES.map((s) => (
            <button
              key={s.value}
              onClick={() => onStyleChange(s.value)}
              className={cn(
                'rounded-full border px-4 py-1.5 text-sm transition-colors',
                style === s.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                  : 'border-neutral-200 hover:border-neutral-300 dark:border-neutral-700 dark:hover:border-neutral-600'
              )}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
