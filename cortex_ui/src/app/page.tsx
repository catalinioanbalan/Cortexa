'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { FileText, Sparkles, ArrowRight } from 'lucide-react'

const features = [
  {
    icon: FileText,
    title: 'Document Q&A',
    description: 'Upload documents and ask questions. Get accurate answers with source references.',
    href: '/documents',
    color: 'blue',
  },
  {
    icon: Sparkles,
    title: 'Input Interpreter',
    description: 'Get thoughtful interpretations of your ideas, thoughts, and experiences.',
    href: '/interpret',
    color: 'purple',
  },
]

export default function Home() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-16">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
          Welcome to{' '}
          <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Cortexa
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-neutral-600 dark:text-neutral-400">
          Your AI-powered interpretation assistant. Understand documents, explore ideas,
          and gain insights with the power of advanced language models.
        </p>
      </motion.div>

      <div className="mt-16 grid gap-6 md:grid-cols-2">
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 * (index + 1) }}
          >
            <Link
              href={feature.href}
              className="group block rounded-2xl border border-neutral-200 p-6 transition-all hover:border-neutral-300 hover:shadow-lg dark:border-neutral-800 dark:hover:border-neutral-700"
            >
              <div
                className={`mb-4 inline-flex rounded-xl p-3 ${
                  feature.color === 'blue'
                    ? 'bg-blue-100 text-blue-600 dark:bg-blue-950 dark:text-blue-400'
                    : 'bg-purple-100 text-purple-600 dark:bg-purple-950 dark:text-purple-400'
                }`}
              >
                <feature.icon className="h-6 w-6" />
              </div>
              <h2 className="mb-2 text-xl font-semibold">{feature.title}</h2>
              <p className="mb-4 text-neutral-600 dark:text-neutral-400">
                {feature.description}
              </p>
              <span className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 dark:text-blue-400">
                Get started
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </span>
            </Link>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
