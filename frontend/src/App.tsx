import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ToastContainer from './components/Toast'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import CallLogs from './pages/CallLogs'
import ApiKeys from './pages/ApiKeys'
import Providers from './pages/Providers'
import Pricing from './pages/Pricing'
import Detection from './pages/Detection'
import Alerts from './pages/Alerts'
import ModelRouting from './pages/ModelRouting'
import Settings from './pages/Settings'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token')
  if (!token) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

export default function App() {
  return (
    <>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="call-logs" element={<CallLogs />} />
          <Route path="api-keys" element={<ApiKeys />} />
          <Route path="providers" element={<Providers />} />
          <Route path="pricing" element={<Pricing />} />
          <Route path="detection" element={<Detection />} />
          <Route path="routing" element={<ModelRouting />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="settings" element={<Settings />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <ToastContainer />
    </>
  )
}
