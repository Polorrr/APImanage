import { useState, useEffect } from 'react'
import client from '../api/client'

interface Pricing {
  id: number
  model_keyword: string
  provider_name: string | null
  input_price: number | string
  input_price_cached: number | string
  output_price: number | string
  currency: string
  is_builtin: boolean
  created_at: string
}

interface PricingForm {
  model_keyword: string
  provider_name?: string
  input_price: number
  input_price_cached: number
  output_price: number
}

export default function Pricing() {
  const [pricing, setPricing] = useState<Pricing[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState<PricingForm>({ model_keyword: '', input_price: 0, input_price_cached: 0, output_price: 0 })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchPricing = () => {
    client.get('/pricing/')
      .then((res) => { setPricing(res.data?.data || []); setError('') })
      .catch(() => setError('加载失败'))
  }

  useEffect(() => { fetchPricing() }, [])

  const handleSave = async () => {
    if (!form.model_keyword) return
    setLoading(true)
    try {
      if (editingId) {
        await client.put(`/pricing/${editingId}/`, form)
      } else {
        await client.post('/pricing/', form)
      }
      setShowDialog(false)
      setEditingId(null)
      setForm({ model_keyword: '', input_price: 0, input_price_cached: 0, output_price: 0 })
      fetchPricing()
    } catch {
      setError('保存失败')
    } finally { setLoading(false) }
  }

  const handleEdit = (item: Pricing) => {
    setEditingId(item.id)
    setForm({
      model_keyword: item.model_keyword,
      input_price: Number(item.input_price),
      input_price_cached: Number(item.input_price_cached || 0),
      output_price: Number(item.output_price),
      provider_name: item.provider_name || undefined,
    })
    setShowDialog(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此价格配置？')) return
    try {
      await client.delete(`/pricing/${id}/`)
      fetchPricing()
    } catch { setError('删除失败') }
  }

  return (
    <div className="p-6 animate-fadeIn">
      <div className="flex items-center justify-between mb-6">
        <h1 className="page-title">价格配置</h1>
        <button onClick={() => { setShowDialog(true); setEditingId(null); setForm({ model_keyword: '', input_price: 0, input_price_cached: 0, output_price: 0 }) }}
          className="btn-primary text-sm">
          添加价格
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-center dark:bg-red-900/20 dark:border-red-800">
          <p className="text-red-500 dark:text-red-400 mb-2">{error}</p>
          <button onClick={() => { setError(''); fetchPricing() }} className="btn-primary text-sm">重试</button>
        </div>
      )}

      <div className="card">
        {pricing.length === 0 && !error ? (
          <div className="empty-state">暂无价格配置</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="table-header">
                  <th className="px-4 py-3 font-medium">模型</th>
                  <th className="px-4 py-3 font-medium text-right">缓存命中 (元/千token)</th>
                  <th className="px-4 py-3 font-medium text-right">未命中 (元/千token)</th>
                  <th className="px-4 py-3 font-medium text-right">输出 (元/千token)</th>
                  <th className="px-4 py-3 font-medium text-center">类型</th>
                  <th className="px-4 py-3 font-medium text-center">操作</th>
                </tr>
              </thead>
              <tbody>
                {pricing.map((p) => (
                  <tr key={p.id} className="table-row">
                    <td className="px-4 py-2.5 font-mono text-xs">{p.model_keyword}</td>
                    <td className="px-4 py-2.5 text-right">¥{Number(p.input_price_cached || 0).toFixed(3)}</td>
                    <td className="px-4 py-2.5 text-right">¥{Number(p.input_price).toFixed(2)}</td>
                    <td className="px-4 py-2.5 text-right">¥{Number(p.output_price).toFixed(2)}</td>
                    <td className="px-4 py-2.5 text-center">
                      <span className={`badge ${p.is_builtin ? 'badge-info' : 'badge-success'}`}>
                        {p.is_builtin ? '内置' : '自定义'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      <button onClick={() => handleEdit(p)} className="text-primary hover:underline text-xs mr-3">编辑</button>
                      {!p.is_builtin && (
                        <button onClick={() => handleDelete(p.id)} className="text-red-600 hover:underline text-xs">删除</button>
                      )}
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
            <h2 className="text-lg font-bold mb-4">{editingId ? '编辑价格' : '添加价格'}</h2>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">模型关键词</label>
              <input type="text" value={form.model_keyword} onChange={(e) => setForm({ ...form, model_keyword: e.target.value })}
                className="input"
                placeholder="例如：mimo-v2.5-pro" />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">供应商（可选）</label>
              <input type="text" value={form.provider_name || ''} onChange={(e) => setForm({ ...form, provider_name: e.target.value || undefined })}
                className="input"
                placeholder="留空表示通用" />
            </div>
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1.5">缓存命中价</label>
                <input type="number" step="0.001" value={form.input_price_cached} onChange={(e) => setForm({ ...form, input_price_cached: Number(e.target.value) })}
                  className="input" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5">未命中价</label>
                <input type="number" step="0.01" value={form.input_price} onChange={(e) => setForm({ ...form, input_price: Number(e.target.value) })}
                  className="input" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5">输出价</label>
                <input type="number" step="0.01" value={form.output_price} onChange={(e) => setForm({ ...form, output_price: Number(e.target.value) })}
                  className="input" />
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
