import { useState, useEffect } from 'react'
import client from '../api/client'

interface ApiKey {
  id: number
  name: string
  key: string
  key_prefix: string
  rate_limit_rpm: number
  is_active: boolean
  permissions: string
  agent_id: string
  agent_name: string
  allowed_models: string[]
  monthly_budget: number
  last_used_at: string | null
  created_at: string
  expires_at: string | null
}

export default function ApiKeys() {
  const [keys, setKeys] = useState<ApiKey[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [copiedId, setCopiedId] = useState<number | null>(null)
  const [form, setForm] = useState({
    name: '',
    rate_limit_rpm: 60,
    permissions: 'read',
    agent_id: '',
    agent_name: '',
    allowed_models: [] as string[],
    monthly_budget: 0,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchKeys = () => {
    client.get('/keys/')
      .then((res) => { setKeys(res.data?.data || []); setError('') })
      .catch(() => setError('加载失败'))
  }

  useEffect(() => { fetchKeys() }, [])

  const handleSave = async () => {
    if (!form.name) return
    setLoading(true)
    try {
      if (editingId) {
        await client.patch(`/keys/${editingId}/`, form)
      } else {
        await client.post('/keys/', form)
      }
      setShowDialog(false)
      setEditingId(null)
      resetForm()
      fetchKeys()
    } catch (err: any) {
      setError(err.response?.data?.message || '保存失败')
    } finally { setLoading(false) }
  }

  const resetForm = () => {
    setForm({
      name: '', rate_limit_rpm: 60, permissions: 'read',
      agent_id: '', agent_name: '', allowed_models: [], monthly_budget: 0,
    })
  }

  const handleEdit = (k: ApiKey) => {
    setEditingId(k.id)
    setForm({
      name: k.name,
      rate_limit_rpm: k.rate_limit_rpm,
      permissions: k.permissions,
      agent_id: k.agent_id || '',
      agent_name: k.agent_name || '',
      allowed_models: k.allowed_models || [],
      monthly_budget: Number(k.monthly_budget) || 0,
    })
    setShowDialog(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此 Key？')) return
    try { await client.delete(`/keys/${id}/`); fetchKeys() }
    catch { setError('删除失败') }
  }

  const handleToggle = async (k: ApiKey) => {
    try {
      await client.patch(`/keys/${k.id}/`, { is_active: !k.is_active })
      fetchKeys()
    } catch {
      setError('操作失败')
    }
  }

  const copyKey = (key: string, id: number) => {
    navigator.clipboard.writeText(key)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  return (
    <div className="p-6 animate-fadeIn">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">API Keys</h1>
          <p className="page-subtitle mt-1">管理你的平台 API Key，支持按 Agent 分配和模型白名单</p>
        </div>
        <button onClick={() => { setShowDialog(true); setEditingId(null); resetForm() }}
          className="btn-primary text-sm">
          创建 Key
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-center dark:bg-red-900/20 dark:border-red-800">
          <p className="text-red-500 dark:text-red-400 mb-2">{error}</p>
          <button onClick={() => { setError(''); fetchKeys() }} className="btn-primary text-sm">重试</button>
        </div>
      )}

      <div className="card">
        {keys.length === 0 && !error ? (
          <div className="empty-state">暂无 API Key</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="table-header">
                  <th className="px-4 py-3 font-medium">名称</th>
                  <th className="px-4 py-3 font-medium">Key</th>
                  <th className="px-4 py-3 font-medium">Agent</th>
                  <th className="px-4 py-3 font-medium text-center">限流</th>
                  <th className="px-4 py-3 font-medium text-center">模型数</th>
                  <th className="px-4 py-3 font-medium text-center">预算</th>
                  <th className="px-4 py-3 font-medium text-center">状态</th>
                  <th className="px-4 py-3 font-medium">最后使用</th>
                  <th className="px-4 py-3 font-medium text-center">操作</th>
                </tr>
              </thead>
              <tbody>
                {keys.map((k) => (
                  <tr key={k.id} className="table-row">
                    <td className="px-4 py-2.5 font-medium">{k.name}</td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        <code className="text-xs bg-gray-100 dark:bg-gray-800 dark:text-gray-300 px-2 py-1 rounded font-mono border border-gray-200 dark:border-gray-600">{k.key_prefix}...</code>
                        <button onClick={() => copyKey(k.key, k.id)} className="text-primary hover:text-primary-dark text-xs">
                          {copiedId === k.id ? '✅ 已复制' : '📋 复制'}
                        </button>
                      </div>
                    </td>
                    <td className="px-4 py-2.5">
                      {k.agent_name ? (
                        <span className="badge badge-info">{k.agent_name}</span>
                      ) : (
                        <span className="text-xs opacity-50">-</span>
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-center text-xs">{k.rate_limit_rpm} rpm</td>
                    <td className="px-4 py-2.5 text-center">
                      {k.allowed_models.length > 0 ? (
                        <span className="badge badge-info">{k.allowed_models.length}</span>
                      ) : (
                        <span className="text-xs opacity-50">全部</span>
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-center text-xs">
                      {Number(k.monthly_budget) > 0 ? `¥${Number(k.monthly_budget).toFixed(0)}` : '-'}
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      <button onClick={() => handleToggle(k)}
                        className={`badge cursor-pointer ${k.is_active ? 'badge-success' : 'badge-error'}`}>
                        {k.is_active ? '✅ 正常' : '❌ 禁用'}
                      </button>
                    </td>
                    <td className="px-4 py-2.5 text-xs">
                      {k.last_used_at ? new Date(k.last_used_at).toLocaleString('zh-CN') : '从未'}
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      <button onClick={() => handleEdit(k)} className="text-primary hover:underline text-xs mr-3">编辑</button>
                      <button onClick={() => handleDelete(k.id)} className="text-red-600 hover:underline text-xs">删除</button>
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
            <h2 className="text-lg font-bold mb-4">{editingId ? '编辑 Key' : '创建 Key'}</h2>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">名称</label>
              <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="input"
                placeholder="例如：客服 Bot Key" />
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1.5">Agent ID</label>
                <input type="text" value={form.agent_id} onChange={(e) => setForm({ ...form, agent_id: e.target.value })}
                  className="input"
                  placeholder="customer-service" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5">Agent 名称</label>
                <input type="text" value={form.agent_name} onChange={(e) => setForm({ ...form, agent_name: e.target.value })}
                  className="input"
                  placeholder="客服 Bot" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1.5">每分钟限流</label>
                <input type="number" value={form.rate_limit_rpm}
                  onChange={(e) => setForm({ ...form, rate_limit_rpm: Number(e.target.value) })}
                  className="input" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5">月度预算 (元)</label>
                <input type="number" step="0.01" value={form.monthly_budget}
                  onChange={(e) => setForm({ ...form, monthly_budget: Number(e.target.value) })}
                  className="input"
                  placeholder="0 = 不限制" />
              </div>
            </div>

            <div className="flex gap-2">
              <button onClick={() => setShowDialog(false)} className="btn-secondary flex-1">取消</button>
              <button onClick={handleSave} disabled={loading} className="btn-primary flex-1 disabled:opacity-50">
                {loading ? '保存中...' : '保存'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
