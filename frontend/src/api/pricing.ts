import client, { ApiResponseRaw } from './client'

export interface Pricing {
  id: number
  model_keyword: string
  provider_name: string | null
  input_price: number | string
  input_price_cached: number | string
  output_price: number | string
  currency: string
  is_builtin: boolean
  created_at: string
}

export interface CreatePricingParams {
  model_keyword: string
  provider_name?: string
  input_price: number
  input_price_cached?: number
  output_price: number
  currency?: string
}

export function listPricing(): Promise<ApiResponseRaw<Pricing[]>> {
  return client.get('/pricing/')
}

export function createPricing(data: CreatePricingParams): Promise<ApiResponseRaw<Pricing>> {
  return client.post('/pricing/', data)
}

export function updatePricing(id: number, data: Partial<Pricing>): Promise<ApiResponseRaw<Pricing>> {
  return client.put(`/pricing/${id}/`, data)
}

export function deletePricing(id: number): Promise<ApiResponseRaw<any>> {
  return client.delete(`/pricing/${id}/`)
}

export function listBuiltinPricing(): Promise<ApiResponseRaw<Pricing[]>> {
  return client.get('/pricing/builtin/')
}
