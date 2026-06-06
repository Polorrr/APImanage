import { useState, useEffect } from 'react'
import client from '../api/client'

interface Provider {
  id: number
  name: string
  base_url: string
  model_prefix: string
  status: string
  health_status: string
  last_health_check: string | null
  created_at: string
}

export default function Providers() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [form, setForm] = useState({ name: '', base_url: '', api_key: '', model_prefix: '' })
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(false)
  const [error, setError] = useState('')
  const [pageError, setPageError] = useState('')

  const fetchProviders = () => {
    client.get('/providers/')
      .then((res) => { setProviders(res.data?.data || []); setPageError('') })
      .catch(() => setPageError('加载失败'))
  }

  useEffect(() => { fetchProviders() }, [])

  const handleCreate = async () => {
    if (!form.name || !form.base_url || !form.api_key) { setError('请填写所有必填字段'); return }
    setError(''); setLoading(true)
    try {
      await client.post('/providers/', form)
      setForm({ name: '', base_url: '', api_key: '', model_prefix: '' })
      setShowDialog(false)
      fetchProviders()
    } catch (err: any) { setError(err.response?.data?.message || '添加失败') }
    finally { setLoading(false) }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此供应商？')) return
    try { await client.delete(`/providers/${id}/`); fetchProviders() }
    catch { setPageError('删除失败') }
  }

  const handleHealthCheck = async () => {
    setChecking(true)
    try {
      await client.get('/providers/health/')
      // Backend saves health_status to DB; refetch to get updated data
      fetchProviders()
    } catch {
      setPageError('健康检查失败')
    } finally { setChecking(false) }
  }

  const getHealthBadge = (status: string) => {
    switch (status) {
      case 'healthy': return <span className="badge badge-success">✅ 正常</span>
      case 'unhealthy': return <span className="badge badge-error">❌ 异常</span>
      default: return <span className="badge badge-info">❓ 未检测</span>
    }
  }

  return (
    <div className="p-6 animate-fadeIn">
      <div className="flex items-center justify-between mb-6">
        <h1 className="page-title">供应商管理</h1>
        <div className="flex gap-2">
          <button onClick={handleHealthCheck} disabled={checking}
            className="btn-secondary text-sm disabled:opacity-50">
            {checking ? '检测中...' : '🔍 一键检测'}
          </button>
          <button onClick={() => { setShowDialog(true); setError('') }}
            className="btn-primary text-sm">
            添加供应商
          </button>
        </div>
      </div>

      {pageError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-center dark:bg-red-900/20 dark:border-red-800">
          <p className="text-red-500 dark:text-red-400 mb-2">{pageError}</p>
          <button onClick={() => { setPageError(''); fetchProviders() }} className="btn-primary text-sm">重试</button>
        </div>
      )}

      <div className="card">
        {providers.length === 0 && !pageError ? (
          <div className="empty-state">暂无供应商，点击右上角添加</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="table-header">
                <th className="px-4 py-3 font-medium">名称</th>
                <th className="px-4 py-3 font-medium">API 地址</th>
                <th className="px-4 py-3 font-medium">模型前缀</th>
                <th className="px-4 py-3 font-medium">健康状态</th>
                <th className="px-4 py-3 font-medium">状态</th>
                <th className="px-4 py-3 font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              {providers.map((p) => (
                <tr key={p.id} className="table-row">
                  <td className="px-4 py-2.5 font-medium text-center">{p.name}</td>
                  <td className="px-4 py-2.5 text-xs break-all text-center">{p.base_url}</td>
                  <td className="px-4 py-2.5 text-center">
                    {p.model_prefix ? (
                      <span className="badge badge-info">{p.model_prefix}</span>
                    ) : (
                      <span className="text-xs opacity-50">未设置</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-center">{getHealthBadge(p.health_status)}</td>
                  <td className="px-4 py-2.5 text-center">
                    <span className={`badge ${p.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                      {p.status === 'active' ? '正常' : '禁用'}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <button onClick={() => handleDelete(p.id)} className="text-red-600 hover:underline text-xs">删除</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showDialog && (
        <div className="dialog-overlay">
          <div className="dialog-content">
            <h2 className="text-lg font-bold mb-4">添加供应商</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">供应商名称</label>
              <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="input"
                placeholder="例如：小米 MiMo" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">API 地址</label>
              <input type="text" value={form.base_url} onChange={(e) => setForm({ ...form, base_url: e.target.value })}
                className="input"
                placeholder="https://token-plan-cn.xiaomimimo.com/v1" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">API Key</label>
              <input type="password" value={form.api_key} onChange={(e) => setForm({ ...form, api_key: e.target.value })}
                className="input"
                placeholder="tp-xxx 或 sk-xxx" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">模型前缀（可选）</label>
              <input type="text" value={form.model_prefix} onChange={(e) => setForm({ ...form, model_prefix: e.target.value })}
                className="input"
                placeholder="mimo-,deepseek-（逗号分隔）" />
            </div>
            {error && <div className="mb-4 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 px-3 py-2 rounded-lg">{error}</div>}
            <div className="flex gap-2">
              <button onClick={() => setShowDialog(false)} className="btn-secondary flex-1">取消</button>
              <button onClick={handleCreate} disabled={loading} className="btn-primary flex-1 disabled:opacity-50">
                {loading ? '添加中...' : '添加'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
