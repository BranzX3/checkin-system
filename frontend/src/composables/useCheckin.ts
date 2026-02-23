import { ref } from 'vue'
import { useCheckinStore } from '@/stores/checkin'
import { useLocation } from './useLocation'

export function useCheckin() {
  const checkinStore = useCheckinStore()
  const { location, getCurrentLocation } = useLocation()
  const error = ref<string | null>(null)
  const isLoading = ref(false)

  const handleCheckIn = async (data: {
    notes?: string
    mood?: { mood_level: number; emotion?: string; notes?: string }
    goal_id?: string
  }) => {
    isLoading.value = true
    error.value = null
    try {
      const loc = await getCurrentLocation()
      await checkinStore.checkIn({
        ...data,
        location_latitude: loc.latitude,
        location_longitude: loc.longitude,
      })
      return true
    } catch (err: any) {
      error.value = err.message || 'Check-in failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const handleCheckOut = async (data: {
    notes?: string
    mood?: { mood_level: number; emotion?: string; notes?: string }
  }) => {
    isLoading.value = true
    error.value = null
    try {
      await checkinStore.checkOut(data)
      return true
    } catch (err: any) {
      error.value = err.message || 'Check-out failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    location,
    error,
    isLoading,
    isCheckedIn: () => checkinStore.isCheckedIn,
    handleCheckIn,
    handleCheckOut,
    clearError,
  }
}
