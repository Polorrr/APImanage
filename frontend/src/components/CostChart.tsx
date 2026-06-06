import ReactECharts from 'echarts-for-react'

interface DailyData {
  date: string
  cost: number
  calls: number
}

interface Props {
  data: DailyData[]
}

export default function CostChart({ data }: Props) {
  const option = {
    tooltip: {
      trigger: 'axis',
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
      boundaryGap: false,
      data: data.map((d) => d.date),
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: {
        fontSize: 11,
        color: '#64748b',
        formatter: (value: string) => {
          const parts = value.split('-')
          return `${parts[1]}-${parts[2]}`
        }
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
        name: '费用',
        type: 'line',
        smooth: true,
        data: data.map((d) => d.cost),
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(26,115,232,0.2)' },
              { offset: 1, color: 'rgba(26,115,232,0.02)' },
            ],
          },
        },
        lineStyle: {
          color: '#1a73e8',
          width: 3,
        },
        itemStyle: {
          color: '#1a73e8',
          borderColor: 'white',
          borderWidth: 2,
        },
        symbol: 'circle',
        symbolSize: 8,
      },
    ],
  }

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">每日消耗趋势</h3>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span>费用</span>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: 300 }} />
    </div>
  )
}
