import client, { ApiResponseRaw } from './client'

export interface AlertRule {
  id: number
  name: string
  rule_type: string
  threshold_yuan: number
  alert_channel: string
  webhook_url: string | null
  is_active: boolean
  last_triggered: string | null
  created_at: string
}

export interface AlertLog {
  id: number
  rule_id: number
  rule_name?: string
  trigger_cost: number
  threshold: number
  channel: string
  send_status: string
  created_at: string
}

export interface CreateRuleParams {
  name: string
  rule_type: string
  threshold_yuan: number
  alert_channel: string
  webhook_url?: string
}

export function listRules(): Promise<ApiResponseRaw<AlertRule[]>> {
  return client.get('/alerts/rules/')
}

export function createRule(data: CreateRuleParams): Promise<ApiResponseRaw<AlertRule>> {
  return client.post('/alerts/rules/', data)
}

export function updateRule(id: number, data: Partial<AlertRule>): Promise<ApiResponseRaw<AlertRule>> {
  return client.put(`/alerts/rules/${id}/`, data)
}

export function deleteRule(id: number): Promise<ApiResponseRaw<any>> {
  return client.delete(`/alerts/rules/${id}/`)
}

export function listAlertLogs(): Promise<ApiResponseRaw<AlertLog[]>> {
  return client.get('/alerts/logs/')
}
