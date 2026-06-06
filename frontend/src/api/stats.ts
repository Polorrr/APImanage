import client, { ApiResponseRaw } from './client'

export interface OverviewData {
  total_cost: number
  total_calls: number
  avg_latency: number
  active_keys: number
  cost_change: number
  calls_change: number
  latency_change: number
}

export interface DailyData {
  date: string
  cost: number
  calls: number
}

export interface ModelData {
  model: string
  cost: number
  calls: number
  percentage: number
}

export interface AgentData {
  agent_id: string
  cost: number
  calls: number
}

export interface CallLog {
  id: number
  model: string
  agent_id: string
  input_tokens_reported: number | null
  output_tokens_reported: number | null
  input_tokens_estimated: number | null
  output_tokens_estimated: number | null
  cost_yuan: string | number | null
  latency_ms: number | null
  status_code: number
  is_error: boolean
  data_source: string
  created_at: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface CallLogParams {
  page?: number
  page_size?: number
  model?: string
  agent_id?: string
  start_date?: string
  end_date?: string
  is_error?: boolean
}

export function getOverview(): Promise<ApiResponseRaw<OverviewData>> {
  return client.get('/stats/overview/')
}

export function getDaily(params?: { start_date?: string; end_date?: string }): Promise<ApiResponseRaw<DailyData[]>> {
  return client.get('/stats/daily/', { params })
}

export function getByModel(): Promise<ApiResponseRaw<ModelData[]>> {
  return client.get('/stats/by-model/')
}

export function getByAgent(): Promise<ApiResponseRaw<AgentData[]>> {
  return client.get('/stats/by-agent/')
}

export function getCallLogs(params: CallLogParams): Promise<ApiResponseRaw<PaginatedResponse<CallLog>>> {
  return client.get('/stats/calls/', { params })
}
