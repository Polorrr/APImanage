import client from './client'

export interface ModelRouting {
  id: number
  model_name: string
  provider: number
  provider_name: string
  is_active: boolean
  created_at: string
}

export interface CreateRoutingParams {
  model_name: string
  provider: number
  is_active?: boolean
}

export const getRoutings = () =>
  client.get<{ code: number; data: ModelRouting[] }>('/routing/')

export const createRouting = (data: CreateRoutingParams) =>
  client.post('/routing/', data)

export const updateRouting = (id: number, data: Partial<CreateRoutingParams>) =>
  client.put(`/routing/${id}/`, data)

export const deleteRouting = (id: number) =>
  client.delete(`/routing/${id}/`)
