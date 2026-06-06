import ReactECharts from 'echarts-for-react'

interface ModelData {
  model: string
  cost: number
  calls: number
  percentage: number
}

interface Props {
  data: ModelData[]
}

const COLORS = [
  '#1a73e8', '#4285f4', '#669df6', '#8ab4f8', '#aecbfa',
  '#c6dafc', '#174ea6', '#1967d2', '#5e97f6', '#93c5fd',
  '#bfdbfe', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe',
  '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#dbeafe',
]

export default function ModelPieChart({ data }: Props) {
  // Filter out models with zero cost
  const filteredData = data.filter(d => d.cost > 0)

  if (filteredData.length === 0) {
    return (
      <div className="card p-5">
        <h3 className="font-semibold text-gray-800 mb-4">模型消耗分布</h3>
        <div className="empty-state">
          <div className="empty-state-icon">📊</div>
          <div className="empty-state-text">暂无消耗数据</div>
        </div>
      </div>
    )
  }

  const chartHeight = Math.max(300, filteredData.length * 28)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => `
        <div style="font-size:12px;padding:4px 8px;">
          <div style="font-weight:600;margin-bottom:4px;">${params.name}</div>
          <div style="color:#64748b;">费用: <span style="color:#1a73e8;font-weight:600;">¥${params.value.toFixed(4)}</span></div>
          <div style="color:#64748b;">占比: <span style="font-weight:600;">${params.percent}%</span></div>
        </div>
      `,
      backgroundColor: 'white',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      borderRadius: 8,
      shadowColor: 'rgba(0,0,0,0.1)',
      shadowBlur: 10,
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: '2%',
      top: 'middle',
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 8,
      selectedMode: true,
      textStyle: {
        fontSize: 11,
        color: '#64748b',
        width: 130,
        overflow: 'truncate',
      },
      pageIconColor: '#1a73e8',
      pageIconInactiveColor: '#c6dafc',
      pageTextStyle: {
        color: '#64748b',
      },
      formatter: (name: string) => {
        if (name.length > 22) {
          return name.substring(0, 20) + '...'
        }
        return name
      },
    },
    series: [
      {
        type: 'pie',
        radius: ['35%', '65%'],
        center: ['38%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 3,
        },
        label: {
          show: false,
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 13,
            fontWeight: 'bold',
          },
          scaleSize: 8,
        },
        data: filteredData.map((d, i) => ({
          name: d.model,
          value: d.cost,
          itemStyle: { color: COLORS[i % COLORS.length] },
        })),
      },
    ],
  }

  return (
    <div className="card p-5">
      <h3 className="font-semibold text-gray-800 mb-4">模型消耗分布</h3>
      <ReactECharts option={option} style={{ height: chartHeight }} />
    </div>
  )
}
