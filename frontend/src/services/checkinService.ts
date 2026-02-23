import api from './api'
import type { Checkin, DailyStats, Goal, Mood } from '@/types'

export const checkinService = {
  async checkIn(data: {
    location_latitude?: number
    location_longitude?: number
    location_name?: string
    notes?: string
    mood?: { mood_level: number; emotion?: string; notes?: string }
    goal_id?: string
  }): Promise<Checkin> {
    const response = await api.post('/api/v1/checkins/check-in', data)
    return response.data
  },

  async checkOut(data: {
    notes?: string
    mood?: { mood_level: number; emotion?: string; notes?: string }
  }): Promise<Checkin> {
    const response = await api.post('/api/v1/checkins/check-out', data)
    return response.data
  },

  async getTodayStats(): Promise<DailyStats> {
    const response = await api.get('/api/v1/checkins/today')
    return response.data
  },

  async getCheckins(skip = 0, limit = 50): Promise<Checkin[]> {
    const response = await api.get('/api/v1/checkins', {
      params: { skip, limit },
    })
    return response.data
  },

  async getCheckin(checkinId: string): Promise<Checkin> {
    const response = await api.get(`/api/v1/checkins/${checkinId}`)
    return response.data
  },

  async updateCheckin(checkinId: string, data: Partial<Checkin>): Promise<Checkin> {
    const response = await api.patch(`/api/v1/checkins/${checkinId}`, data)
    return response.data
  },

  async deleteCheckin(checkinId: string): Promise<void> {
    await api.delete(`/api/v1/checkins/${checkinId}`)
  },
}

export const goalService = {
  async createGoal(data: { title: string; description?: string; priority?: string }): Promise<Goal> {
    const response = await api.post('/api/v1/goals', data)
    return response.data
  },

  async getGoals(completed?: boolean, skip = 0, limit = 50): Promise<Goal[]> {
    const response = await api.get('/api/v1/goals', {
      params: { completed, skip, limit },
    })
    return response.data
  },

  async getGoal(goalId: string): Promise<Goal> {
    const response = await api.get(`/api/v1/goals/${goalId}`)
    return response.data
  },

  async updateGoal(goalId: string, data: Partial<Goal>): Promise<Goal> {
    const response = await api.patch(`/api/v1/goals/${goalId}`, data)
    return response.data
  },

  async deleteGoal(goalId: string): Promise<void> {
    await api.delete(`/api/v1/goals/${goalId}`)
  },
}
