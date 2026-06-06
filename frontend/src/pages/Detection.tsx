import { useState } from 'react'
import client from '../api/client'

interface TrialResult {
  model: string
  status: string
  input_tokens: number | null
  output_tokens: number | null
  total_tokens: number | null
  latency_ms: number | null
  has_usage: boolean
  error?: string
}

interface DetectResult {
  api_connected: boolean
  models_found: string[]
  token_mode: string
  matched_prices: {
    model: string
    input_price: number | null
    input_price_cached: number | null
    output_price: number | null
    status: string
  }[]
  provider_created?: boolean
  routing_created?: number
  provider_id?: number
  provider_name?: string
}

export default function Detection() {
  const [url, setUrl] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(false)
  const [trialLoading, setTrialLoading] = useState(false)
  const [result, setResult] = useState<DetectResult | null>(null)
  const [trialResults, setTrialResults] = useState<TrialResult[]>([])
  const [error, setError] = useState('')
  const [prices, setPrices] = useState<{model: string; input_price: number | null; input_price_cached: number | null; output_price: number | null; status: string}[]>([])
  const [saving, setSaving] = useState(false)

  const handleDetect = async () => {
    if (!url || !apiKey) { setError('请填写 API 地址和 Key'); return }
    setError(''); setLoading(true); setResult(null); setTrialResults([])
    try {
      const res = await client.post('/detect/', {
        base_url: url,
        api_key: apiKey,
        name: name || undefined,
      })
      const data = res.data?.data
      setResult(data)
      setPrices(data?.matched_prices || [])
    } catch (err: any) {
      setError(err.response?.data?.message || '检测失败')
    } finally { setLoading(false) }
  }

  const handleTrial = async () => {
    if (!url || !apiKey) { setError('请填写 API 地址和 Key'); return }
    setError(''); setTrialLoading(true); setTrialResults([])
    try {
      const res = await client.post('/pricing/trial/', { base_url: url, api_key: apiKey })
      const data = res.data?.data
      setTrialResults(data?.results || [])
    } catch (err: any) {
      setError(err.response?.data?.message || '试算失败')
    } finally { setTrialLoading(false) }
  }

  const handlePriceChange = (index: number, field: string, value: string) => {
    const updated = [...prices]
    updated[index] = { ...updated[index], [field]: value === '' ? null : Number(value) }
    setPrices(updated)
  }

  const handleSave = async () => {
    setSaving(true)
    let saved = 0
    for (const p of prices) {
      if (p.input_price && p.output_price && p.input_price > 0 && p.output_price > 0) {
        try {
          await client.post('/pricing/', {
            model_keyword: p.model,
            input_price: p.input_price,
            input_price_cached: p.input_price_cached || 0,
            output_price: p.output_price,
          })
          saved++
        } catch {}
      }
    }
    setSaving(false)
    alert(`已保存 ${saved} 个模型价格`)
  }

  return (
    <div className="p-6 animate-fadeIn">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">API 自动检测</h1>
          <p className="page-subtitle mt-1">填写 API 地址和 Key，自动创建供应商、发现模型、配置路由和匹配价格</p>
        </div>
      </div>

      {/* 输入区域 */}
      <div className="card p-5 mb-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1.5">供应商名称</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)}
              className="input text-sm"
              placeholder="自动识别" />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium mb-1.5">API 地址</label>
            <input type="text" value={url} onChange={(e) => setUrl(e.target.value)}
              className="input text-sm"
              placeholder="https://token-plan-cn.xiaomimimo.com/v1" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1.5">API Key</label>
            <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)}
              className="input text-sm"
              placeholder="tp-xxx 或 sk-xxx" />
          </div>
        </div>

        {error && <div className="mb-4 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 px-3 py-2 rounded-lg">{error}</div>}

        <div className="flex gap-3">
          <button onClick={handleDetect} disabled={loading}
            className="btn-primary text-sm disabled:opacity-50">
            {loading ? '检测中...' : '🔍 一键检测'}
          </button>
          <button onClick={handleTrial} disabled={trialLoading}
            className="btn-secondary text-sm disabled:opacity-50">
            {trialLoading ? '试算中...' : '💰 试算价格'}
          </button>
        </div>
      </div>

      {/* 检测结果 */}
      {result && (
        <div className="card p-5 mb-4">
          <h3 className="text-sm font-medium mb-3">检测结果</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
              <div className="text-lg">{result.api_connected ? '✅' : '❌'}</div>
              <div className="text-xs mt-1 opacity-70">API 连接</div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-primary">{result.models_found?.length || 0}</div>
              <div className="text-xs mt-1 opacity-70">发现模型</div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
              <div className="text-lg">{result.token_mode === 'provider' ? '✅' : '⚠️'}</div>
              <div className="text-xs mt-1 opacity-70">{result.token_mode === 'provider' ? '精确模式' : '估算模式'}</div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-green-600">{result.routing_created || 0}</div>
              <div className="text-xs mt-1 opacity-70">路由创建</div>
            </div>
          </div>

          {result.provider_created && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4 text-sm text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400">
              ✅ 已自动创建供应商「{result.provider_name}」，并配置了 {result.routing_created} 条模型路由
            </div>
          )}

          {result.models_found?.length > 0 && (
            <div className="mb-4">
              <h4 className="text-xs font-medium mb-2 uppercase opacity-70">发现的模型</h4>
              <div className="flex flex-wrap gap-2">
                {result.models_found.map(m => (
                  <span key={m} className="badge badge-info">{m}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 价格配置 */}
      {prices.length > 0 && (
        <div className="card p-5 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium">价格配置</h3>
            <span className="text-xs opacity-50">已匹配的价格来自内置数据库，未匹配的请手动填写</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="table-header">
                  <th className="px-4 py-2.5 font-medium">模型</th>
                  <th className="px-4 py-2.5 font-medium text-right">缓存命中 (元/千token)</th>
                  <th className="px-4 py-2.5 font-medium text-right">未命中 (元/千token)</th>
                  <th className="px-4 py-2.5 font-medium text-right">输出 (元/千token)</th>
                  <th className="px-4 py-2.5 font-medium text-center">状态</th>
                </tr>
              </thead>
              <tbody>
                {prices.map((p, i) => (
                  <tr key={p.model} className="table-row">
                    <td className="px-4 py-2.5 font-mono text-xs">{p.model}</td>
                    <td className="px-4 py-2.5 text-right">
                      {p.status === 'matched' ? (
                        <span className="text-green-700 dark:text-green-400 font-medium text-xs">¥{p.input_price_cached || 0}</span>
                      ) : (
                        <input type="number" step="0.001" value={p.input_price_cached ?? ''}
                          onChange={(e) => handlePriceChange(i, 'input_price_cached', e.target.value)}
                          className="input w-24 px-2 py-1 text-xs text-right" />
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      {p.status === 'matched' ? (
                        <span className="text-green-700 dark:text-green-400 font-medium text-xs">¥{p.input_price}</span>
                      ) : (
                        <input type="number" step="0.01" value={p.input_price ?? ''}
                          onChange={(e) => handlePriceChange(i, 'input_price', e.target.value)}
                          className="input w-24 px-2 py-1 text-xs text-right" />
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      {p.status === 'matched' ? (
                        <span className="text-green-700 dark:text-green-400 font-medium text-xs">¥{p.output_price}</span>
                      ) : (
                        <input type="number" step="0.01" value={p.output_price ?? ''}
                          onChange={(e) => handlePriceChange(i, 'output_price', e.target.value)}
                          className="input w-24 px-2 py-1 text-xs text-right" />
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      <span className={`badge ${p.status === 'matched' ? 'badge-success' : 'badge-warning'}`}>
                        {p.status === 'matched' ? '✅ 已匹配' : '⚠️ 手动'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4">
            <button onClick={handleSave} disabled={saving}
              className="btn-primary text-sm disabled:opacity-50">
              {saving ? '保存中...' : '确认保存价格'}
            </button>
          </div>
        </div>
      )}

      {/* 试算结果 */}
      {trialResults.length > 0 && (
        <div className="card p-5">
          <h3 className="text-sm font-medium mb-3">试算结果</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="table-header">
                  <th className="px-4 py-2.5 font-medium">模型</th>
                  <th className="px-4 py-2.5 font-medium text-right">输入 Token</th>
                  <th className="px-4 py-2.5 font-medium text-right">输出 Token</th>
                  <th className="px-4 py-2.5 font-medium text-right">延迟</th>
                  <th className="px-4 py-2.5 font-medium text-center">状态</th>
                </tr>
              </thead>
              <tbody>
                {trialResults.map((r) => (
                  <tr key={r.model} className="table-row">
                    <td className="px-4 py-2.5 font-mono text-xs">{r.model}</td>
                    <td className="px-4 py-2.5 text-right">{r.input_tokens ?? '-'}</td>
                    <td className="px-4 py-2.5 text-right">{r.output_tokens ?? '-'}</td>
                    <td className="px-4 py-2.5 text-right">{r.latency_ms ? `${r.latency_ms}ms` : '-'}</td>
                    <td className="px-4 py-2.5 text-center">
                      {r.status === 'ok' ? (
                        <span className="badge badge-success">✅ 正常</span>
                      ) : r.status === 'no_usage' ? (
                        <span className="badge badge-warning">⚠️ 无 usage</span>
                      ) : (
                        <span className="badge badge-error">❌ {r.error}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-xs text-blue-700 dark:text-blue-400">
            💡 去中转站后台查看这次调用的扣费金额，然后计算单价：输入单价 = 扣费中输入部分 ÷ 输入 Token × 1000
          </div>
        </div>
      )}
    </div>
  )
}
