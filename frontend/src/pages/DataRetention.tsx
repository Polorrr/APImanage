import { useState, useEffect } from 'react'
import client from '../api/client'

interface RetentionPolicy {
  id: number
  name: string
  retention_days: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export default function DataRetention() {
  const [policies, setPolicies] = useState<RetentionPolicy[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showDialog, setShowDialog] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState({
    name: '',
    retention_days: 30,
    is_active: true,
  })

  const fetchPolicies = () => {
    setLoading(true)
    client.get('/alerts/retention/')
      .then((res) => {
        setPolicies(res.data?.data || [])
        setError('')
      })
      .catch((err: any) => {
        setError(err.response?.data?.message || '加载失败')
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchPolicies()
  }, [])

  const handleSave = () => {
    if (!form.name) {
      setError('请输入策略名称')
      return
    }

    const request = editingId
      ? client.patch(`/alerts/retention/${editingId}/`, form)
      : client.post('/alerts/retention/', form)

    request
      .then(() => {
        setShowDialog(false)
        setEditingId(null)
        setForm({ name: '', retention_days: 30, is_active: true })
        fetchPolicies()
      })
      .catch((err: any) => {
        setError(err.response?.data?.message || '保存失败')
      })
  }

  const handleEdit = (policy: RetentionPolicy) => {
    setEditingId(policy.id)
    setForm({
      name: policy.name,
      retention_days: policy.retention_days,
      is_active: policy.is_active,
    })
    setShowDialog(true)
  }

  const handleDelete = (id: number) => {
    if (!confirm('确定删除此策略？')) return

    client.delete(`/alerts/retention/${id}/`)
      .then(() => fetchPolicies())
      .catch((err: any) => {
        setError(err.response?.data?.message || '删除失败')
      })
  }

  const handleToggle = (policy: RetentionPolicy) => {
    client.patch(`/alerts/retention/${policy.id}/`, { is_active: !policy.is_active })
      .then(() => fetchPolicies())
      .catch((err: any) => {
        setError(err.response?.data?.message || '操作失败')
      })
  }

  return (
    <div className="animate-fadeIn">
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">数据保留策略</h1>
          <p className="page-subtitle">设置日志保留时间，自动清理过期数据</p>
        </div>
        <button onClick={() => { setEditingId(null); setForm({ name: '', retention_days: 30, is_active: true }); setShowDialog(true) }} className="btn-primary">
          添加策略
        </button>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4 text-center">
          <p className="text-red-500 dark:text-red-400 mb-2">{error}</p>
          <button onClick={() => setError('')} className="btn-primary">确定</button>
        </div>
      )}

      {/* 策略列表 */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="table-header text-left">
                <th className="px-4 py-3 font-medium">策略名称</th>
                <th className="px-4 py-3 font-medium">保留天数</th>
                <th className="px-4 py-3 font-medium">状态</th>
                <th className="px-4 py-3 font-medium">创建时间</th>
                <th className="px-4 py-3 font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400 dark:text-gray-500">加载中...</td></tr>
              ) : policies.length === 0 ? (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400 dark:text-gray-500">暂无保留策略</td></tr>
              ) : (
                policies.map((policy) => (
                  <tr key={policy.id} className="table-row">
                    <td className="px-4 py-2.5 font-medium">{policy.name}</td>
                    <td className="px-4 py-2.5">{policy.retention_days} 天</td>
                    <td className="px-4 py-2.5">
                      <button onClick={() => handleToggle(policy)} className={`badge cursor-pointer ${policy.is_active ? 'badge-success' : 'badge-warning'}`}>
                        {policy.is_active ? '✅ 启用' : '⏸ 禁用'}
                      </button>
                    </td>
                    <td className="px-4 py-2.5 text-xs">
                      {new Date(policy.created_at).toLocaleString('zh-CN')}
                    </td>
                    <td className="px-4 py-2.5">
                      <button onClick={() => handleEdit(policy)} className="text-primary hover:underline text-xs mr-3">编辑</button>
                      <button onClick={() => handleDelete(policy.id)} className="text-red-600 hover:underline text-xs">删除</button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 添加/编辑对话框 */}
      {showDialog && (
        <div className="dialog-overlay" onClick={() => setShowDialog(false)}>
          <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
            <h2 className="text-lg font-bold mb-4">{editingId ? '编辑策略' : '添加策略'}</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">策略名称</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="input"
                  placeholder="例如：默认保留策略"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">保留天数</label>
                <input
                  type="number"
                  value={form.retention_days}
                  onChange={(e) => setForm({ ...form, retention_days: parseInt(e.target.value) || 30 })}
                  className="input"
                  min="1"
                  max="365"
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">超过此天数的日志将被自动删除</p>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                  className="w-4 h-4 text-primary rounded"
                />
                <label htmlFor="is_active" className="text-sm font-medium">启用策略</label>
              </div>
            </div>

            <div className="flex gap-2 mt-6">
              <button onClick={() => setShowDialog(false)} className="btn-secondary flex-1">取消</button>
              <button onClick={handleSave} className="btn-primary flex-1 justify-center">保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
