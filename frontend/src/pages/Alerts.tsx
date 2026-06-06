import { useState, useEffect } from 'react'
import client from '../api/client'

interface AlertRule {
  id: number
  name: string
  rule_type: string
  api_key: number | null
  api_key_name: string | null
  threshold_yuan: number
  auto_disable: boolean
  alert_channel: string
  webhook_url: string | null
  is_active: boolean
  last_triggered: string | null
  created_at: string
}

interface AlertLog {
  id: number
  rule: number
  rule_name: string
  trigger_cost: number
  threshold: number
  channel: string
  send_status: string
  created_at: string
}

interface ApiKeyOption {
  id: number
  name: string
  agent_name: string
}

export default function Alerts() {
  const [rules, setRules] = useState<AlertRule[]>([])
  const [logs, setLogs] = useState<AlertLog[]>([])
  const [apiKeys, setApiKeys] = useState<ApiKeyOption[]>([])
  const [showDialog, setShowDialog] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState({
    name: '',
    rule_type: 'monthly',
    api_key: null as number | null,
    threshold_yuan: 100,
    auto_disable: false,
    alert_channel: 'webhook',
    webhook_url: '',
  })
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'rules' | 'logs'>('rules')
  const [error, setError] = useState('')

  const fetchRules = () => {
    client.get('/alerts/rules/')
      .then((res) => { setRules(res.data?.data || []); setError('') })
      .catch(() => setError('加载规则失败'))
  }

  const fetchLogs = () => {
    client.get('/alerts/logs/')
      .then((res) => { setLogs(res.data?.data || []); setError('') })
      .catch(() => setError('加载日志失败'))
  }

  const fetchApiKeys = () => {
    client.get('/keys/')
      .then((res) => {
        setApiKeys((res.data?.data || []).map((k: any) => ({
          id: k.id,
          name: k.name,
          agent_name: k.agent_name || '',
        })))
      })
      .catch(() => {})
  }

  useEffect(() => { fetchRules(); fetchLogs(); fetchApiKeys() }, [])

  const handleSave = async () => {
    if (!form.name) return
    setLoading(true)
    try {
      const payload: any = {
        name: form.name,
        rule_type: form.rule_type,
        threshold_yuan: form.threshold_yuan,
        auto_disable: form.auto_disable,
        alert_channel: form.alert_channel,
        webhook_url: form.webhook_url,
      }
      if (form.api_key) payload.api_key = form.api_key

      if (editingId) {
        await client.put(`/alerts/rules/${editingId}/`, payload)
      } else {
        await client.post('/alerts/rules/', payload)
      }
      setShowDialog(false)
      setEditingId(null)
      resetForm()
      fetchRules()
    } catch (err: any) {
      setError(err.response?.data?.message || '保存失败')
    } finally { setLoading(false) }
  }

  const resetForm = () => {
    setForm({
      name: '', rule_type: 'monthly', api_key: null, threshold_yuan: 100,
      auto_disable: false, alert_channel: 'webhook', webhook_url: '',
    })
  }

  const handleEdit = (rule: AlertRule) => {
    setEditingId(rule.id)
    setForm({
      name: rule.name,
      rule_type: rule.rule_type,
      api_key: rule.api_key,
      threshold_yuan: Number(rule.threshold_yuan),
      auto_disable: rule.auto_disable,
      alert_channel: rule.alert_channel,
      webhook_url: rule.webhook_url || '',
    })
    setShowDialog(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除此规则？')) return
    try { await client.delete(`/alerts/rules/${id}/`); fetchRules() }
    catch { setError('删除失败') }
  }

  const handleToggle = async (rule: AlertRule) => {
    try { await client.put(`/alerts/rules/${rule.id}/`, { is_active: !rule.is_active }); fetchRules() }
    catch { setError('操作失败') }
  }

  const ruleTypeLabel = (type: string) => {
    if (type === 'daily') return '每日'
    if (type === 'monthly') return '每月'
    return '累计'
  }

  return (
    <div className="p-6 animate-fadeIn">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">告警设置</h1>
          <p className="page-subtitle mt-1">设置预算告警规则，支持用户级和单个 Key 级别</p>
        </div>
        <button onClick={() => { setShowDialog(true); setEditingId(null); resetForm() }}
          className="btn-primary text-sm">
          添加规则
        </button>
      </div>

      <div className="flex gap-1 mb-4 border-b border-gray-200 dark:border-gray-700">
        <button onClick={() => setActiveTab('rules')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${activeTab === 'rules' ? 'border-primary text-primary' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}`}>
          告警规则
        </button>
        <button onClick={() => setActiveTab('logs')}
          className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${activeTab === 'logs' ? 'border-primary text-primary' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'}`}>
          告警历史
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-center dark:bg-red-900/20 dark:border-red-800">
          <p className="text-red-500 dark:text-red-400 mb-2">{error}</p>
          <button onClick={() => { setError(''); fetchRules(); fetchLogs() }} className="btn-primary text-sm">重试</button>
        </div>
      )}

      {activeTab === 'rules' && (
        <div className="card">
          {rules.length === 0 && !error ? (
            <div className="empty-state">暂无告警规则</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="table-header">
                    <th className="px-4 py-3 font-medium">规则名称</th>
                    <th className="px-4 py-3 font-medium">类型</th>
                    <th className="px-4 py-3 font-medium">作用范围</th>
                    <th className="px-4 py-3 font-medium text-center">阈值</th>
                    <th className="px-4 py-3 font-medium text-center">自动禁用</th>
                    <th className="px-4 py-3 font-medium text-center">状态</th>
                    <th className="px-4 py-3 font-medium">上次触发</th>
                    <th className="px-4 py-3 font-medium text-center">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {rules.map((r) => (
                    <tr key={r.id} className="table-row">
                      <td className="px-4 py-2.5 font-medium text-center">{r.name}</td>
                      <td className="px-4 py-2.5 text-center">
                        <span className="badge badge-info">{ruleTypeLabel(r.rule_type)}</span>
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        {r.api_key_name ? (
                          <span className="badge badge-info">{r.api_key_name}</span>
                        ) : (
                          <span className="badge badge-warning">全部 Key</span>
                        )}
                      </td>
                      <td className="px-4 py-2.5 text-center font-mono">¥{Number(r.threshold_yuan).toFixed(2)}</td>
                      <td className="px-4 py-2.5 text-center">
                        {r.auto_disable ? (
                          <span className="badge badge-error">是</span>
                        ) : (
                          <span className="text-xs opacity-50">否</span>
                        )}
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <span className={`badge ${r.is_active ? 'badge-success' : 'badge-warning'}`}>
                          {r.is_active ? '✅ 启用' : '⏸ 禁用'}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-center text-xs">
                        {r.last_triggered ? new Date(r.last_triggered).toLocaleString('zh-CN') : '从未'}
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <button onClick={() => handleEdit(r)} className="text-primary hover:underline text-xs mr-3">编辑</button>
                        <button onClick={() => handleDelete(r.id)} className="text-red-600 hover:underline text-xs">删除</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab === 'logs' && (
        <div className="card">
          {logs.length === 0 ? (
            <div className="empty-state">暂无告警记录</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="table-header">
                    <th className="px-4 py-3 font-medium">时间</th>
                    <th className="px-4 py-3 font-medium">规则</th>
                    <th className="px-4 py-3 font-medium text-right">触发费用</th>
                    <th className="px-4 py-3 font-medium text-center">阈值</th>
                    <th className="px-4 py-3 font-medium text-center">通知方式</th>
                    <th className="px-4 py-3 font-medium text-center">状态</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id} className="table-row">
                      <td className="px-4 py-2.5 text-xs">{new Date(log.created_at).toLocaleString('zh-CN')}</td>
                      <td className="px-4 py-2.5">{log.rule_name}</td>
                      <td className="px-4 py-2.5 text-right font-mono">¥{Number(log.trigger_cost).toFixed(2)}</td>
                      <td className="px-4 py-2.5 text-right font-mono">¥{Number(log.threshold).toFixed(2)}</td>
                      <td className="px-4 py-2.5 text-center">
                        <span className="badge badge-warning">{log.channel === 'webhook' ? 'Webhook' : '邮件'}</span>
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <span className={`badge ${log.send_status === 'sent' ? 'badge-success' : 'badge-error'}`}>
                          {log.send_status === 'sent' ? '已发送' : '失败'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {showDialog && (
        <div className="dialog-overlay">
          <div className="dialog-content">
            <h2 className="text-lg font-bold mb-4">{editingId ? '编辑规则' : '添加规则'}</h2>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">规则名称</label>
              <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="input"
                placeholder="例如：客服 Bot 月度预算" />
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-1.5">规则类型</label>
                <select value={form.rule_type} onChange={(e) => setForm({ ...form, rule_type: e.target.value })}
                  className="input">
                  <option value="daily">每日</option>
                  <option value="monthly">每月</option>
                  <option value="total">累计</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1.5">告警阈值 (元)</label>
                <input type="number" step="0.01" value={form.threshold_yuan}
                  onChange={(e) => setForm({ ...form, threshold_yuan: Number(e.target.value) })}
                  className="input" />
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">作用范围</label>
              <select value={form.api_key || ''} onChange={(e) => setForm({ ...form, api_key: e.target.value ? Number(e.target.value) : null })}
                className="input">
                <option value="">全部 Key（用户级）</option>
                {apiKeys.map(k => (
                  <option key={k.id} value={k.id}>{k.name}{k.agent_name ? ` (${k.agent_name})` : ''}</option>
                ))}
              </select>
              <p className="text-xs opacity-50 mt-1">选择「全部 Key」检查所有调用的总费用，选择具体 Key 只检查该 Key 的费用</p>
            </div>

            <div className="mb-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={form.auto_disable}
                  onChange={(e) => setForm({ ...form, auto_disable: e.target.checked })}
                  className="rounded text-primary focus:ring-primary/20" />
                <span className="text-sm">超预算后自动禁用 Key</span>
              </label>
              <p className="text-xs opacity-50 mt-1 ml-5">仅对「单个 Key」级别的规则有效</p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium mb-1.5">通知方式</label>
              <select value={form.alert_channel} onChange={(e) => setForm({ ...form, alert_channel: e.target.value })}
                className="input">
                <option value="webhook">Webhook</option>
                <option value="email">邮件</option>
              </select>
            </div>

            {form.alert_channel === 'webhook' && (
              <div className="mb-4">
                <label className="block text-sm font-medium mb-1.5">Webhook URL</label>
                <input type="text" value={form.webhook_url}
                  onChange={(e) => setForm({ ...form, webhook_url: e.target.value })}
                  className="input"
                  placeholder="企微/钉钉 webhook 地址" />
              </div>
            )}

            <div className="flex gap-2">
              <button onClick={() => setShowDialog(false)} className="btn-secondary flex-1">取消</button>
              <button onClick={handleSave} disabled={loading} className="btn-primary flex-1 justify-center disabled:opacity-50">
                {loading ? '保存中...' : '保存'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
