import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import client from '../api/client'
import { showToast } from '../components/Toast'

interface Settings {
  log_retention_days: number
  updated_at: string
}

export default function Settings() {
  const navigate = useNavigate()
  const [settings, setSettings] = useState<Settings | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const fetchSettings = () => {
    setLoading(true)
    client.get('/settings/')
      .then((res) => {
        setSettings(res.data?.data || null)
      })
      .catch((err: any) => {
        showToast(err.response?.data?.message || '加载失败', 'error')
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchSettings()
  }, [])

  const handleSave = () => {
    if (!settings) return

    setSaving(true)
    client.patch('/settings/', { log_retention_days: settings.log_retention_days })
      .then((res) => {
        setSettings(res.data?.data || settings)
        showToast('保存成功', 'success')
      })
      .catch((err: any) => {
        showToast(err.response?.data?.message || '保存失败', 'error')
      })
      .finally(() => setSaving(false))
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  return (
    <div className="animate-fadeIn">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="page-title">设置</h1>
        <p className="page-subtitle">管理你的账户和系统设置</p>
      </div>

      {/* 数据保留设置 */}
      <div className="card p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">📦 数据保留</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          设置调用日志的保留时间，超过此时间的日志将被自动删除
        </p>

        {loading ? (
          <div className="loading">
            <div className="loading-spinner" />
            <span>加载中...</span>
          </div>
        ) : settings ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">日志保留天数</label>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  value={settings.log_retention_days}
                  onChange={(e) => setSettings({ ...settings, log_retention_days: parseInt(e.target.value) || 30 })}
                  className="input"
                  style={{ width: '120px' }}
                  min="1"
                  max="999"
                />
                <span className="text-gray-500 dark:text-gray-400">天</span>
              </div>
              <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                当前设置：保留最近 {settings.log_retention_days} 天的调用日志
              </p>
            </div>

            <button onClick={handleSave} disabled={saving} className="btn-primary">
              {saving ? '保存中...' : '保存设置'}
            </button>
          </div>
        ) : null}
      </div>

      {/* 账户操作 */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">👤 账户</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
          管理你的账户操作
        </p>

        <button onClick={handleLogout} className="btn-secondary text-red-600 border-red-300 hover:bg-red-50 dark:text-red-400 dark:border-red-700 dark:hover:bg-red-900/20">
          🚪 退出登录
        </button>
      </div>
    </div>
  )
}
