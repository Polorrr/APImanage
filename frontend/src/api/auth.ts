import client, { ApiResponseRaw } from './client'

export interface LoginParams {
  email: string
  password: string
}

export interface RegisterParams {
  username: string
  email: string
  password: string
}

export interface UserInfo {
  id: number
  username: string
  email: string
  is_active: boolean
  is_staff: boolean
  created_at: string
}

export interface TokenPair {
  access: string
  refresh: string
}

export function login(data: LoginParams): Promise<ApiResponseRaw<TokenPair>> {
  return client.post('/auth/login/', data)
}

export function register(data: RegisterParams): Promise<ApiResponseRaw<any>> {
  return client.post('/auth/register/', data)
}

export function getMe(): Promise<ApiResponseRaw<UserInfo>> {
  return client.get('/auth/me/')
}

export function refreshToken(refresh: string): Promise<ApiResponseRaw<{ access: string }>> {
  return client.post('/auth/refresh/', { refresh })
}
