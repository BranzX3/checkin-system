import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { checkinService } from '@/services/checkinService'
import type { Checkin, DailyStats, Goal, Mood } from '@/types'

export const useCheckinStore = defineStore('checkin', () => {
  const checkins = ref<Checkin[]>([])
  const todayStats = ref<DailyStats | null>(null)
  const goals = ref<Goal[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isCheckedIn = computed(() => todayStats.value?.is_checked_in ?? false)
  const totalDurationToday = computed(() => todayStats.value?.total_duration_minutes ?? 0)

  const fetchTodayStats = async () => {
    loading.value = true
    error.value = null
    try {
      todayStats.value = await checkinService.getTodayStats()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch today stats'
      throw err
    } finally {
      loading.value = false
    }
  }

  const checkIn = async (data: {
    location_latitude?: number
    location_longitude?: number
    location_name?: string
    notes?: string
    mood?: { mood_level: number; emotion?: string; notes?: string }
    goal_id?: string
  }) => {
    loading.value = true
    error.value = null
    try {
      const checkin = await checkinService.checkIn(data)
      checkins.value.unshift(checkin)
      await fetchTodayStats()
      return checkin
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Check-in failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const checkOut = async (data: {
    notes?: string
    mood?: { mood_level: number; emotion?: string; notes?: string }
  }) => {
    loading.value = true
    error.value = null
    try {
      const checkout = await checkinService.checkOut(data)
      checkins.value.unshift(checkout)
      await fetchTodayStats()
      return checkout
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Check-out failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCheckins = async (skip = 0, limit = 50) => {
    loading.value = true
    error.value = null
    try {
      checkins.value = await checkinService.getCheckins(skip, limit)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch checkins'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteCheckin = async (checkinId: string) => {
    try {
      await checkinService.deleteCheckin(checkinId)
      checkins.value = checkins.value.filter(c => c.id !== checkinId)
      await fetchTodayStats()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete checkin'
      throw err
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    checkins,
    todayStats,
    goals,
    loading,
    error,
    isCheckedIn,
    totalDurationToday,
    fetchTodayStats,
    checkIn,
    checkOut,
    fetchCheckins,
    deleteCheckin,
    clearError,
  }
})
