import client, { ApiResponseRaw } from './client'

export interface Provider {
  id: number
  name: string
  base_url: string
  status: string
  detect_result: Record<string, any> | null
  created_at: string
}

export interface CreateProviderParams {
  name: string
  base_url: string
  api_key: string
}

export interface DetectResult {
  api_connected: boolean
  models_found: string[]
  token_mode: string
  matched_prices: {
    model: string
    input_price: number | null
    output_price: number | null
    status: string
  }[]
}

export function listProviders(): Promise<ApiResponseRaw<Provider[]>> {
  return client.get('/providers/')
}

export function createProvider(data: CreateProviderParams): Promise<ApiResponseRaw<Provider>> {
  return client.post('/providers/', data)
}

export function updateProvider(id: number, data: Partial<Provider>): Promise<ApiResponseRaw<Provider>> {
  return client.patch(`/providers/${id}/`, data)
}

export function deleteProvider(id: number): Promise<ApiResponseRaw<any>> {
  return client.delete(`/providers/${id}/`)
}

export function detectProvider(id: number): Promise<ApiResponseRaw<DetectResult>> {
  return client.post(`/providers/${id}/detect/`)
}
