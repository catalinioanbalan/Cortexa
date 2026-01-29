export function Footer() {
  return (
    <footer className="border-t border-neutral-200 dark:border-neutral-800">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
        <p className="text-sm text-neutral-500">
          Cortexa &copy; {new Date().getFullYear()}
        </p>
        <p className="text-sm text-neutral-400">
          AI-powered interpretation
        </p>
      </div>
    </footer>
  )
}
