import { useState, useEffect } from 'react'
import client from '../api/client'

interface ModelRouting {
  id: number
  model_name: string
  provider: number
  provider_name: string
  priority: number
  max_tokens: number
  is_active: boolean
  created_at: string
}

interface Provider {
  id: number
  name: string
}

export default function ModelRoutingPage() {
  const [routings, setRoutings] = useState<ModelRouting[]>([])
  const [providers, setProviders] = useState<Provider[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [form, setForm] = useState({ model_name: '', provider: 0, priority: 1, max_tokens: 0 })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchRoutings = () => {
    client.get('/routing/')
      .then((res) => { setRoutings(res.data?.data || []); setError('') })
      .catch(() => setError('加载失败'))
  }

  const fetchProviders = () => {
    client.get('/providers/')
      .then((res) => setProviders((res.data?.data || []).map((p: any) => ({ id: p.id, name: p.name }))))
      .catch(() => {})
  }

  useEffect(() => { fetchRoutings(); fetchProviders() }, [])

  const handleCreate = async () => {
    if (!form.model_name || !form.provider) { setError('请填写模型名和选择供应商'); return }
    setLoading(true)
    try {
      await client.post('/routing/', form)
      setForm({ model_name: '', provider: 0, priority: 1, max_tokens: 0 })
      setShowDialog(false)
      fetchRoutings()
    } catch { setError('创建失败') }
    finally { setLoading(false) }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定删除此路由？')) return
    try { await client.delete(`/routing/${id}/`); fetchRoutings() }
    catch { setError('删除失败') }
  }

  const handleToggle = async (id: number, is_active: boolean) => {
    try { await client.put(`/routing/${id}/`, { is_active: !is_active }); fetchRoutings() }
    catch { setError('更新失败') }
  }

  const getPriorityBadge = (priority: number) => {
    switch (priority) {
      case 1: return <span className="badge badge-success">P1 最高</span>
      case 2: return <span className="badge badge-info">P2 备用</span>
      case 3: return <span className="badge badge-warning">P3 备用</span>
      default: return <span className="badge badge-warning">P{priority}</span>
    }
  }

  const commonMaxTokens: Record<string, number> = {
    'mimo-v2.5-pro': 16384,
    'mimo-v2.5': 16384,
    'mimo-v2-pro': 16384,
    'mimo-v2-omni': 16384,
    'mimo-v2-flash': 16384,
  }

  return (
    <div className="p-6 animate-fadeIn">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">模型路由</h1>
          <p className="page-subtitle mt-1">管理模型到供应商的映射，同名模型可配置多个供应商（按优先级选择）</p>
        </div>
        <button onClick={() => { setShowDialog(true); setError('') }}
          className="btn-primary text-sm">
          添加路由
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-center dark:bg-red-900/20 dark:border-red-800">
          <p className="text-red-500 dark:text-red-400 mb-2">{error}</p>
          <button onClick={() => { setError(''); fetchRoutings() }} className="btn-primary text-sm">重试</button>
        </div>
      )}

      <div className="card">
        {routings.length === 0 && !error ? (
          <div className="empty-state">
            暂无路由配置<br/>
            <span className="text-xs">添加供应商后使用「自动检测」会自动创建路由</span>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="table-header">
                  <th className="px-4 py-3 font-medium">模型名</th>
                  <th className="px-4 py-3 font-medium">路由到供应商</th>
                  <th className="px-4 py-3 font-medium text-center">优先级</th>
                  <th className="px-4 py-3 font-medium text-right">Max Tokens</th>
                  <th className="px-4 py-3 font-medium text-center">状态</th>
                  <th className="px-4 py-3 font-medium text-center">操作</th>
                </tr>
              </thead>
              <tbody>
                {routings.map((r) => (
                  <tr key={r.id} className="table-row">
                    <td className="px-4 py-2.5 font-mono text-xs text-center">{r.model_name}</td>
                    <td className="px-4 py-2.5 text-center">
                      <span className="badge badge-info">{r.provider_name}</span>
                    </td>
                    <td className="px-4 py-2.5 text-center">{getPriorityBadge(r.priority)}</td>
                    <td className="px-4 py-2.5 text-center">
                      {r.max_tokens > 0 ? (
                        <span className="text-xs font-mono">{r.max_tokens.toLocaleString()}</span>
                      ) : (
                        <span className="text-xs opacity-50">不限制</span>
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      <button onClick={() => handleToggle(r.id, r.is_active)}
                        className={`badge cursor-pointer ${r.is_active ? 'badge-success' : 'badge-warning'}`}>
                        {r.is_active ? '✅ 启用' : '⏸ 禁用'}
                      </button>
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      <button onClick={() => handleDelete(r.id)} className="text-red-600 hover:underline text-xs">删除</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showDialog && (
        <div className="dialog-overlay">
          <div className="dialog-content">
            <h2 className="text-lg font-bold mb-4">添加模型路由</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">模型名</label>
              <input type="text" value={form.model_name} onChange={(e) => {
                const name = e.target.value
                setForm({ ...form, model_name: name, max_tokens: commonMaxTokens[name] || 0 })
              }}
                className="input"
                placeholder="例如：mimo-v2.5-pro 或 deepseek-ai/DeepSeek-V4-Flash" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">路由到供应商</label>
              <select value={form.provider} onChange={(e) => setForm({ ...form, provider: Number(e.target.value) })}
                className="input">
                <option value={0}>请选择供应商</option>
                {providers.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1.5">优先级</label>
                <select value={form.priority} onChange={(e) => setForm({ ...form, priority: Number(e.target.value) })}
                  className="input">
                  <option value={1}>P1 - 最高（优先使用）</option>
                  <option value={2}>P2 - 备用（P1 挂了自动切换）</option>
                  <option value={3}>P3 - 备用（P1 和 P2 都挂了才用）</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5">Max Tokens</label>
                <input type="number" value={form.max_tokens} onChange={(e) => setForm({ ...form, max_tokens: Number(e.target.value) })}
                  className="input"
                  placeholder="0 = 不限制" />
                <p className="text-xs opacity-50 mt-1">超过此限制的请求会自动截断</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => setShowDialog(false)} className="btn-secondary flex-1">取消</button>
              <button onClick={handleCreate} disabled={loading} className="btn-primary flex-1 disabled:opacity-50">
                {loading ? '创建中...' : '创建'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
