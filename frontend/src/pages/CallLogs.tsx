import { useState, useEffect } from 'react'
import { getCallLogs, CallLog, CallLogParams } from '../api/stats'

export default function CallLogs() {
  const [logs, setLogs] = useState<CallLog[]>([])
  const [count, setCount] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [model, setModel] = useState('')
  const [agentId, setAgentId] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchLogs = (p: number = 1) => {
    setLoading(true)
    setError('')
    const params: CallLogParams = { page: p, page_size: pageSize }
    if (model) params.model = model
    if (agentId) params.agent_id = agentId
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    getCallLogs(params)
      .then((res) => {
        const data = res.data?.data
        if (data) {
          setLogs(data.results || [])
          setCount(data.count || 0)
          setPage(p)
        }
      })
      .catch((err: any) => {
        setError(err.response?.data?.message || '加载失败，请稍后重试')
      })
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchLogs(1)
  }, [])

  const handleSearch = () => {
    fetchLogs(1)
  }

  const totalPages = Math.ceil(count / pageSize)

  return (
    <div className="animate-fadeIn">
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="page-title">调用日志</h1>
        <p className="page-subtitle">查看所有 API 调用记录</p>
      </div>

      {/* 筛选栏 */}
      <div className="card p-4 mb-4">
        <div className="flex items-center gap-3 flex-wrap">
          <input
            type="text"
            placeholder="模型名称"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="input"
            style={{ width: 'auto', minWidth: '120px' }}
          />
          <input
            type="text"
            placeholder="Agent ID"
            value={agentId}
            onChange={(e) => setAgentId(e.target.value)}
            className="input"
            style={{ width: 'auto', minWidth: '120px' }}
          />
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="input"
            style={{ width: 'auto' }}
          />
          <span className="text-gray-400">-</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="input"
            style={{ width: 'auto' }}
          />
          <button onClick={handleSearch} className="btn-primary">
            搜索
          </button>
          <button
            onClick={() => { setModel(''); setAgentId(''); setStartDate(''); setEndDate(''); fetchLogs(1) }}
            className="btn-secondary"
          >
            重置
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4 text-center">
          <p className="text-red-500 dark:text-red-400 mb-2">{error}</p>
          <button onClick={() => fetchLogs(1)} className="btn-primary">
            重试
          </button>
        </div>
      )}

      {/* 表格 */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="table-header text-left">
                <th className="px-4 py-3 font-medium">时间</th>
                <th className="px-4 py-3 font-medium">模型</th>
                <th className="px-4 py-3 font-medium">Agent</th>
                <th className="px-4 py-3 font-medium">输入 Token</th>
                <th className="px-4 py-3 font-medium">输出 Token</th>
                <th className="px-4 py-3 font-medium">费用</th>
                <th className="px-4 py-3 font-medium">延迟</th>
                <th className="px-4 py-3 font-medium">数据来源</th>
                <th className="px-4 py-3 font-medium">状态</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={9} className="px-4 py-8 text-center text-gray-400 dark:text-gray-500">加载中...</td></tr>
              ) : logs.length === 0 ? (
                <tr><td colSpan={9} className="px-4 py-8 text-center text-gray-400 dark:text-gray-500">暂无调用记录</td></tr>
              ) : (
                logs.map((log, index) => (
                  <tr key={log.id} className="table-row">
                    <td className="px-4 py-2.5">{new Date(log.created_at).toLocaleString('zh-CN')}</td>
                    <td className="px-4 py-2.5 font-medium">{log.model}</td>
                    <td className="px-4 py-2.5">{log.agent_id || '-'}</td>
                    <td className="px-4 py-2.5">{log.input_tokens_reported ?? log.input_tokens_estimated ?? 0}</td>
                    <td className="px-4 py-2.5">{log.output_tokens_reported ?? log.output_tokens_estimated ?? 0}</td>
                    <td className="px-4 py-2.5">¥{Number(log.cost_yuan || 0).toFixed(4)}</td>
                    <td className="px-4 py-2.5">{log.latency_ms ?? '-'}{log.latency_ms ? 'ms' : ''}</td>
                    <td className="px-4 py-2.5">
                      <span className={`badge ${
                        log.data_source === 'provider' ? 'badge-success' :
                        log.data_source === 'blocked' ? 'badge-error' :
                        'badge-warning'
                      }`}>
                        {log.data_source === 'provider' ? '精确' : log.data_source === 'blocked' ? '拦截' : '估算'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5">
                      {log.data_source === 'blocked' ? (
                        <span className="badge badge-warning">拦截</span>
                      ) : log.is_error ? (
                        <span className="badge badge-error">失败</span>
                      ) : (
                        <span className="badge badge-success">成功</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* 分页 */}
        {count > 0 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 dark:border-gray-700">
            <span className="text-sm text-gray-500 dark:text-gray-400">共 {count} 条</span>
            {totalPages > 1 && (
              <div className="flex items-center gap-1">
                <button
                  disabled={page <= 1}
                  onClick={() => fetchLogs(page - 1)}
                  className="px-3 py-1 text-sm border border-gray-200 dark:border-gray-600 rounded-lg disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  上一页
                </button>
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const start = Math.max(1, Math.min(page - 2, totalPages - 4))
                  const p = start + i
                  if (p > totalPages) return null
                  return (
                    <button
                      key={p}
                      onClick={() => fetchLogs(p)}
                      className={`px-3 py-1 text-sm border rounded-lg ${
                        p === page
                          ? 'bg-primary text-white border-primary'
                          : 'border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      {p}
                    </button>
                  )
                })}
                <button
                  disabled={page >= totalPages}
                  onClick={() => fetchLogs(page + 1)}
                  className="px-3 py-1 text-sm border border-gray-200 dark:border-gray-600 rounded-lg disabled:opacity-50 hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  下一页
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
