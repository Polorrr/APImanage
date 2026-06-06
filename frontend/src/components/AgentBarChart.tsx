import ReactECharts from 'echarts-for-react'

interface AgentData {
  agent_id: string
  cost: number
  calls: number
}

interface Props {
  data: AgentData[]
}

export default function AgentBarChart({ data }: Props) {
  if (!data || data.length === 0) {
    return (
      <div className="card p-5">
        <h3 className="font-semibold text-gray-800 mb-4">Agent 消耗排行</h3>
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <div className="empty-state-text">暂无 Agent 数据</div>
        </div>
      </div>
    )
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = params[0]
        return `
          <div style="font-size:12px;padding:4px 8px;">
            <div style="font-weight:600;margin-bottom:4px;">${item.name}</div>
            <div style="color:#64748b;">费用: <span style="color:#1a73e8;font-weight:600;">¥${item.value.toFixed(4)}</span></div>
          </div>
        `
      },
      backgroundColor: 'white',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      borderRadius: 8,
      shadowColor: 'rgba(0,0,0,0.1)',
      shadowBlur: 10,
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.agent_id || '未分类'),
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: {
        fontSize: 11,
        color: '#64748b',
        rotate: data.length > 5 ? 30 : 0,
      },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: {
        formatter: '¥{value}',
        fontSize: 11,
        color: '#64748b',
      },
    },
    series: [
      {
        type: 'bar',
        data: data.map(d => d.cost),
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#4285f4' },
              { offset: 1, color: '#1a73e8' },
            ],
          },
          borderRadius: [6, 6, 0, 0],
        },
        barWidth: '40%',
      },
    ],
  }

  return (
    <div className="card p-5">
      <h3 className="font-semibold text-gray-800 mb-4">Agent 消耗排行</h3>
      <ReactECharts option={option} style={{ height: 300 }} />
    </div>
  )
}
