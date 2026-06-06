import client, { ApiResponseRaw } from './client'

export interface ApiKey {
  id: number
  name: string
  key_prefix: string
  permissions: { read: boolean; write: boolean }
  rate_limit_rpm: number
  is_active: boolean
  last_used_at: string | null
  expires_at: string | null
  created_at: string
  full_key?: string
}

export interface CreateKeyParams {
  name: string
  rate_limit_rpm?: number
  permissions?: { read: boolean; write: boolean }
  expires_at?: string
}

export function listKeys(): Promise<ApiResponseRaw<ApiKey[]>> {
  return client.get('/keys/')
}

export function createKey(data: CreateKeyParams): Promise<ApiResponseRaw<ApiKey & { full_key: string }>> {
  return client.post('/keys/', data)
}

export function updateKey(id: number, data: Partial<ApiKey>): Promise<ApiResponseRaw<ApiKey>> {
  return client.patch(`/keys/${id}/`, data)
}

export function deleteKey(id: number): Promise<ApiResponseRaw<any>> {
  return client.delete(`/keys/${id}/`)
}
