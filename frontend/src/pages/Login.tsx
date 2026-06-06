import { useState, useEffect, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import client from '../api/client'

export default function Login() {
  const navigate = useNavigate()
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const mouseRef = useRef({ x: 0, y: 0 })
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationId: number
    let width = window.innerWidth
    let height = window.innerHeight

    canvas.width = width
    canvas.height = height

    // 粒子类
    class Particle {
      x: number
      y: number
      vx: number
      vy: number
      radius: number
      color: string

      constructor() {
        this.x = Math.random() * width
        this.y = Math.random() * height
        this.vx = (Math.random() - 0.5) * 0.5
        this.vy = (Math.random() - 0.5) * 0.5
        this.radius = Math.random() * 3 + 1
        this.color = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'][Math.floor(Math.random() * 5)]
      }

      update() {
        const dx = mouseRef.current.x - this.x
        const dy = mouseRef.current.y - this.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        const maxDist = 150

        if (dist < maxDist) {
          const force = (maxDist - dist) / maxDist
          this.vx += dx * force * 0.002
          this.vy += dy * force * 0.002
        }

        this.vx *= 0.98
        this.vy *= 0.98
        this.vx += (Math.random() - 0.5) * 0.1
        this.vy += (Math.random() - 0.5) * 0.1

        this.x += this.vx
        this.y += this.vy

        if (this.x < 0 || this.x > width) this.vx *= -1
        if (this.y < 0 || this.y > height) this.vy *= -1
        this.x = Math.max(0, Math.min(width, this.x))
        this.y = Math.max(0, Math.min(height, this.y))
      }

      draw() {
        ctx!.beginPath()
        ctx!.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
        ctx!.fillStyle = this.color
        ctx!.globalAlpha = 0.6
        ctx!.fill()

        ctx!.beginPath()
        ctx!.arc(this.x, this.y, this.radius * 3, 0, Math.PI * 2)
        const gradient = ctx!.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.radius * 3)
        gradient.addColorStop(0, this.color + '40')
        gradient.addColorStop(1, 'transparent')
        ctx!.fillStyle = gradient
        ctx!.globalAlpha = 0.3
        ctx!.fill()
        ctx!.globalAlpha = 1
      }
    }

    const particles: Particle[] = Array.from({ length: 50 }, () => new Particle())

    function drawLines() {
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < 120) {
            ctx!.beginPath()
            ctx!.moveTo(particles[i].x, particles[i].y)
            ctx!.lineTo(particles[j].x, particles[j].y)
            ctx!.strokeStyle = `rgba(102, 126, 234, ${0.2 * (1 - dist / 120)})`
            ctx!.lineWidth = 0.5
            ctx!.stroke()
          }
        }

        const dx = mouseRef.current.x - particles[i].x
        const dy = mouseRef.current.y - particles[i].y
        const dist = Math.sqrt(dx * dx + dy * dy)

        if (dist < 200) {
          ctx!.beginPath()
          ctx!.moveTo(particles[i].x, particles[i].y)
          ctx!.lineTo(mouseRef.current.x, mouseRef.current.y)
          ctx!.strokeStyle = `rgba(118, 75, 162, ${0.4 * (1 - dist / 200)})`
          ctx!.lineWidth = 0.8
          ctx!.stroke()
        }
      }
    }

    function drawMouseGlow() {
      const gradient = ctx!.createRadialGradient(
        mouseRef.current.x, mouseRef.current.y, 0,
        mouseRef.current.x, mouseRef.current.y, 100
      )
      gradient.addColorStop(0, 'rgba(102, 126, 234, 0.15)')
      gradient.addColorStop(1, 'transparent')
      ctx!.fillStyle = gradient
      ctx!.fillRect(0, 0, width, height)
    }

    function animate() {
      ctx!.clearRect(0, 0, width, height)
      drawMouseGlow()
      drawLines()
      particles.forEach(p => {
        p.update()
        p.draw()
      })
      animationId = requestAnimationFrame(animate)
    }

    animate()

    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY }
    }

    const handleResize = () => {
      width = window.innerWidth
      height = window.innerHeight
      canvas.width = width
      canvas.height = height
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('resize', handleResize)

    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const res = await client.post('/auth/login/', { email, password })
      const data = res.data?.data
      if (data?.access) {
        localStorage.setItem('access_token', data.access)
        localStorage.setItem('refresh_token', data.refresh)
        navigate('/')
      }
    } catch (err: any) {
      setError(err.response?.data?.message || '登录失败，请检查邮箱和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center"
      style={{ background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)' }}
    >
      <canvas ref={canvasRef} className="absolute inset-0 z-0" />

      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full opacity-20 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #667eea 0%, transparent 70%)' }}
      />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full opacity-20 blur-3xl pointer-events-none"
        style={{ background: 'radial-gradient(circle, #764ba2 0%, transparent 70%)' }}
      />

      <div className="relative z-10 w-full max-w-md mx-4 animate-float-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4 shadow-2xl"
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              animation: 'pulse-glow 2s ease-in-out infinite',
            }}
          >
            <span className="text-3xl font-bold text-white">AI</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">AI 成本管理平台</h1>
          <p className="text-gray-400 text-sm">智能管理你的每一笔 AI 开销</p>
        </div>

        <div className="backdrop-blur-xl rounded-3xl p-8 shadow-2xl"
          style={{
            background: 'rgba(255, 255, 255, 0.08)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            boxShadow: '0 25px 50px rgba(0, 0, 0, 0.3)',
          }}
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-500/20 border border-red-500/30 rounded-xl p-3 text-center animate-shake">
                <p className="text-red-300 text-sm">{error}</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">邮箱</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all"
                style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                }}
                placeholder="请输入邮箱"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">密码</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all pr-12"
                  style={{
                    background: 'rgba(255, 255, 255, 0.08)',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                  }}
                  placeholder="请输入密码"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl text-white font-semibold text-lg transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 10px 40px rgba(102, 126, 234, 0.4)',
              }}
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  登录中...
                </span>
              ) : '登录'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <span className="text-gray-400 text-sm">还没有账号? </span>
            <Link to="/register" className="text-purple-400 hover:text-purple-300 text-sm font-medium transition-colors">
              立即注册
            </Link>
          </div>
        </div>

        <div className="text-center mt-8 text-gray-500 text-xs">
          <p>Powered by AIManage © 2026</p>
        </div>
      </div>

      <style>{`
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 30px rgba(102, 126, 234, 0.5); }
          50% { box-shadow: 0 0 60px rgba(118, 75, 162, 0.8); }
        }
        @keyframes float-in {
          from { opacity: 0; transform: translateY(30px) scale(0.95); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
        .animate-float-in { animation: float-in 0.8s ease-out; }
        .animate-shake { animation: shake 0.3s ease-in-out; }
      `}</style>
    </div>
  )
}
