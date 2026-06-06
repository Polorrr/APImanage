import { useState, useEffect, useCallback } from 'react'

interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
  duration: number
}

let toastId = 0
let addToastFn: ((toast: Omit<Toast, 'id'>) => void) | null = null

export function showToast(message: string, type: 'success' | 'error' | 'info' = 'success', duration: number = 3000) {
  if (addToastFn) {
    addToastFn({ message, type, duration })
  }
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = ++toastId
    setToasts(prev => [...prev, { ...toast, id }])
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, toast.duration)
  }, [])

  useEffect(() => {
    addToastFn = addToast
    return () => { addToastFn = null }
  }, [addToast])

  const removeToast = (id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-3">
      {toasts.map(toast => (
        <div
          key={toast.id}
          className="relative overflow-hidden rounded-xl shadow-2xl min-w-[280px] max-w-[360px] animate-slideInRight"
          style={{
            background: toast.type === 'success' ? '#065f46' : toast.type === 'error' ? '#991b1b' : '#1e3a5f',
            border: `1px solid ${toast.type === 'success' ? '#10b981' : toast.type === 'error' ? '#ef4444' : '#3b82f6'}`,
          }}
        >
          {/* 内容 */}
          <div className="flex items-center gap-3 px-4 py-3">
            <span className="text-lg flex-shrink-0">
              {toast.type === 'success' ? '✅' : toast.type === 'error' ? '❌' : 'ℹ️'}
            </span>
            <span className="text-white text-sm flex-1">{toast.message}</span>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-white/50 hover:text-white text-lg flex-shrink-0"
            >
              ×
            </button>
          </div>

          {/* 加载条 */}
          <div className="h-[3px] w-full bg-black/20">
            <div
              className="h-full rounded-full"
              style={{
                background: toast.type === 'success' ? '#34d399' : toast.type === 'error' ? '#f87171' : '#60a5fa',
                animation: `shrink ${toast.duration}ms linear forwards`,
              }}
            />
          </div>
        </div>
      ))}

      <style>{`
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(100px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
        .animate-slideInRight {
          animation: slideInRight 0.3s ease;
        }
      `}</style>
    </div>
  )
}
