import api from './api'
import type { TokenData, User } from '@/types'

export const authService = {
  async register(email: string, password: string, full_name?: string): Promise<User> {
    const response = await api.post('/api/v1/auth/register', {
      email,
      password,
      full_name,
    })
    return response.data
  },

  async login(email: string, password: string): Promise<TokenData> {
    const response = await api.post('/api/v1/auth/login', {
      email,
      password,
    })
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<TokenData> {
    const response = await api.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}

export const userService = {
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/api/v1/users/me')
    return response.data
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.put('/api/v1/users/me', data)
    return response.data
  },

  async getUserProfile(userId: string): Promise<User> {
    const response = await api.get(`/api/v1/users/${userId}`)
    return response.data
  },
}
