interface Props {
  title: string
  value: string | number
  suffix?: string
  icon?: string
  iconBg?: string
  change?: number | null
}

export default function StatsCard({ title, value, suffix, icon, iconBg, change }: Props) {
  return (
    <div className="stat-card">
      <div className="flex items-start justify-between mb-4">
        <div className={`stat-card-icon ${iconBg || 'bg-blue-100'}`}>
          {icon || '📊'}
        </div>
        {change !== null && change !== undefined && (
          <div className={`flex items-center gap-1 text-sm font-medium ${
            change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-gray-500'
          }`}>
            {change > 0 ? '↑' : change < 0 ? '↓' : '→'}
            {Math.abs(change)}%
          </div>
        )}
      </div>
      <div className="stat-card-value">
        {value}{suffix && <span className="text-lg text-gray-500 ml-1">{suffix}</span>}
      </div>
      <div className="stat-card-label">{title}</div>
    </div>
  )
}
