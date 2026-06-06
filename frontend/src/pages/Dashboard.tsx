import { useState, useEffect } from 'react'
import StatsCard from '../components/StatsCard'
import CostChart from '../components/CostChart'
import ModelPieChart from '../components/ModelPieChart'
import AgentBarChart from '../components/AgentBarChart'
import {
  getOverview,
  getDaily,
  getByModel,
  getByAgent,
  getCallLogs,
  OverviewData,
  DailyData,
  ModelData,
  AgentData,
  CallLog,
} from '../api/stats'

export default function Dashboard() {
  const [overview, setOverview] = useState<OverviewData | null>(null)
  const [daily, setDaily] = useState<DailyData[]>([])
  const [models, setModels] = useState<ModelData[]>([])
  const [agents, setAgents] = useState<AgentData[]>([])
  const [calls, setCalls] = useState<CallLog[]>([])
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchData = () => {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate

    setLoading(true)
    Promise.all([
      getOverview(),
      getDaily(params),
      getByModel(),
      getByAgent(),
      getCallLogs({ page: 1, page_size: 10 }),
    ]).then(([ov, d, m, a, cl]) => {
      setOverview(ov.data.data)
      setDaily(d.data.data)
      setModels(m.data.data)
      setAgents(a.data.data)
      setCalls(cl.data.data?.results || [])
      setError('')
    }).catch((err: any) => {
      setError(err.response?.data?.message || '加载失败，请稍后重试')
    }).finally(() => {
      setLoading(false)
    })
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleFilter = () => {
    fetchData()
  }

  return (
    <div className="animate-fadeIn">
      {/* 页面标题 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="page-title">数据概览</h1>
          <p className="page-subtitle">查看你的 LLM API 使用情况和成本分析</p>
        </div>
        <div className="flex items-center gap-3">
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="input"
            style={{ width: 'auto' }}
          />
          <span className="text-gray-400">至</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="input"
            style={{ width: 'auto' }}
          />
          <button onClick={handleFilter} className="btn-primary">
            查询
          </button>
        </div>
      </div>

      {error ? (
        <div className="card p-8 text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button onClick={fetchData} className="btn-primary">
            重试
          </button>
        </div>
      ) : loading ? (
        <div className="loading">
          <div className="loading-spinner" />
          <span>加载中...</span>
        </div>
      ) : (
        <>
          {/* 统计卡片 */}
          {overview && (
            <div className="grid grid-cols-4 gap-5 mb-6">
              <StatsCard
                title="总消耗"
                value={`¥${overview.total_cost.toFixed(2)}`}
                icon="💰"
                iconBg="bg-blue-100 dark:bg-blue-900"
                change={overview.cost_change}
              />
              <StatsCard
                title="总调用"
                value={overview.total_calls.toLocaleString()}
                icon="📈"
                iconBg="bg-green-100 dark:bg-green-900"
                change={overview.calls_change}
              />
              <StatsCard
                title="平均延迟"
                value={overview.avg_latency}
                suffix="ms"
                icon="⚡"
                iconBg="bg-yellow-100 dark:bg-yellow-900"
                change={overview.latency_change}
              />
              <StatsCard
                title="活跃 Key"
                value={overview.active_keys}
                icon="🔑"
                iconBg="bg-purple-100 dark:bg-purple-900"
              />
            </div>
          )}

          {/* 图表区域 */}
          <div className="grid grid-cols-2 gap-5 mb-6">
            <CostChart data={daily} />
            <ModelPieChart data={models} />
          </div>

          {/* Agent 消耗 */}
          <div className="mb-6">
            <AgentBarChart data={agents} />
          </div>

          {/* 最近调用 */}
          <div className="card">
            <div className="flex items-center justify-between p-5 border-b border-gray-100 dark:border-gray-700">
              <h3 className="font-semibold">最近调用</h3>
              <span className="text-sm text-gray-500 dark:text-gray-400">最近 10 条</span>
            </div>
            {calls.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📋</div>
                <div className="empty-state-text">暂无调用记录</div>
                <div className="empty-state-hint">开始使用 API 后，调用记录会显示在这里</div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="table-header text-left">
                      <th className="px-5 py-3 font-medium">时间</th>
                      <th className="px-5 py-3 font-medium">模型</th>
                      <th className="px-5 py-3 font-medium">Agent</th>
                      <th className="px-5 py-3 font-medium">Token</th>
                      <th className="px-5 py-3 font-medium">费用</th>
                      <th className="px-5 py-3 font-medium">延迟</th>
                      <th className="px-5 py-3 font-medium">状态</th>
                    </tr>
                  </thead>
                  <tbody>
                    {calls.map((call) => (
                      <tr key={call.id} className="table-row">
                        <td className="px-5 py-3.5">
                          {new Date(call.created_at).toLocaleString('zh-CN')}
                        </td>
                        <td className="px-5 py-3.5">
                          <span className="badge badge-info">{call.model}</span>
                        </td>
                        <td className="px-5 py-3.5">
                          {call.agent_id || '-'}
                        </td>
                        <td className="px-5 py-3.5">
                          {(call.input_tokens_reported || 0) + (call.output_tokens_reported || 0)}
                        </td>
                        <td className="px-5 py-3.5 font-medium">
                          ¥{Number(call.cost_yuan || 0).toFixed(4)}
                        </td>
                        <td className="px-5 py-3.5">
                          {call.latency_ms || '-'}{call.latency_ms ? 'ms' : ''}
                        </td>
                        <td className="px-5 py-3.5">
                          {call.data_source === 'blocked' ? (
                            <span className="badge badge-warning">拦截</span>
                          ) : call.is_error ? (
                            <span className="badge badge-error">失败</span>
                          ) : (
                            <span className="badge badge-success">成功</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
