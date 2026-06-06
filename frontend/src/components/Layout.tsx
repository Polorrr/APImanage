import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom'

const NAV_ITEMS = [
  { path: '/', label: '概览', icon: '📊', desc: '数据看板' },
  { path: '/call-logs', label: '调用日志', icon: '📋', desc: '请求记录' },
  { path: '/api-keys', label: 'API Keys', icon: '🔑', desc: '密钥管理' },
  { path: '/providers', label: '供应商', icon: '🏢', desc: '供应商管理' },
  { path: '/routing', label: '模型路由', icon: '🔀', desc: '路由配置' },
  { path: '/pricing', label: '价格配置', icon: '💰', desc: '价格管理' },
  { path: '/detection', label: '自动检测', icon: '🔍', desc: '一键配置' },
  { path: '/alerts', label: '告警设置', icon: '🔔', desc: '预算告警' },
]

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true'
  })

  useEffect(() => {
    localStorage.setItem('darkMode', String(darkMode))
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  const handleLogout = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  const handleToggleDarkMode = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDarkMode(!darkMode)
  }

  const handleToggleCollapse = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setCollapsed(!collapsed)
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* 侧边栏 */}
      <aside className={`flex flex-col transition-all duration-300 ${collapsed ? 'w-[76px]' : 'w-[240px]'} ${
        darkMode 
          ? 'bg-gray-800 border-r border-gray-700' 
          : 'bg-[#0f172a]'
      }`}>
        {/* Logo */}
        <div className={`flex items-center py-6 ${collapsed ? 'justify-center px-2' : 'gap-3 px-4'}`}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-lg flex-shrink-0">
            A
          </div>
          {!collapsed && (
            <div>
              <h1 className="text-white font-bold text-lg">AIManage</h1>
              <p className="text-gray-400 text-xs">成本管理平台</p>
            </div>
          )}
        </div>

        {/* 导航菜单 - 可滚动区域 */}
        <nav className="flex-1 overflow-y-auto space-y-1 px-2 pb-4">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 ${
                  collapsed ? 'justify-center px-0' : ''
                } ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                    : darkMode
                      ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
                      : 'text-gray-400 hover:bg-white/10 hover:text-white'
                }`}
                title={collapsed ? item.label : undefined}
              >
                <span className={`${collapsed ? 'text-2xl' : 'text-xl'} flex-shrink-0`}>{item.icon}</span>
                {!collapsed && (
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm">{item.label}</div>
                    <div className={`text-xs ${isActive ? 'text-blue-200' : 'opacity-70'}`}>{item.desc}</div>
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* 底部控制区 */}
        <div className={`flex-shrink-0 py-4 px-2 border-t ${
          darkMode ? 'border-gray-700' : 'border-white/10'
        }`}>
          {/* 设置 */}
          <Link
            to="/settings"
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 mb-1 ${
              collapsed ? 'justify-center px-0' : ''
            } ${
              location.pathname === '/settings'
                ? 'bg-blue-600 text-white'
                : darkMode
                  ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  : 'text-gray-400 hover:bg-white/10 hover:text-white'
            }`}
            title={collapsed ? '设置' : undefined}
          >
            <span className={`${collapsed ? 'text-2xl' : 'text-xl'} flex-shrink-0`}>⚙️</span>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm">设置</div>
                <div className={`text-xs ${location.pathname === '/settings' ? 'text-blue-200' : 'opacity-70'}`}>系统设置</div>
              </div>
            )}
          </Link>

          {/* 深色模式切换 */}
          <button
            type="button"
            onClick={handleToggleDarkMode}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 mb-1 ${
              collapsed ? 'justify-center px-0' : ''
            } ${
              darkMode
                ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
                : 'text-gray-400 hover:bg-white/10 hover:text-white'
            }`}
            title={collapsed ? (darkMode ? '浅色模式' : '深色模式') : undefined}
          >
            <span className={`${collapsed ? 'text-2xl' : 'text-xl'} flex-shrink-0`}>
              {darkMode ? '☀️' : '🌙'}
            </span>
            {!collapsed && (
              <div className="flex-1 min-w-0 text-left">
                <div className="font-medium text-sm">{darkMode ? '浅色模式' : '深色模式'}</div>
              </div>
            )}
          </button>

          {/* 折叠按钮 */}
          <button
            type="button"
            onClick={handleToggleCollapse}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 ${
              collapsed ? 'justify-center px-0' : ''
            } ${
              darkMode
                ? 'text-gray-300 hover:bg-gray-700 hover:text-white'
                : 'text-gray-400 hover:bg-white/10 hover:text-white'
            }`}
            title={collapsed ? '展开侧边栏' : '收起侧边栏'}
          >
            <span className={`${collapsed ? 'text-2xl' : 'text-xl'} flex-shrink-0 transition-transform duration-300 ${collapsed ? 'rotate-180' : ''}`}>
              ◀
            </span>
            {!collapsed && (
              <div className="flex-1 min-w-0 text-left">
                <div className="font-medium text-sm">收起侧边栏</div>
              </div>
            )}
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className={`flex-1 overflow-auto ${darkMode ? 'bg-gray-900 text-white' : 'bg-[#f0f5ff]'}`}>
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
