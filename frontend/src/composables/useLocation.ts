import { ref } from 'vue'

export interface Location {
  latitude: number
  longitude: number
  accuracy?: number
  timestamp: number
}

export function useLocation() {
  const location = ref<Location | null>(null)
  const error = ref<string | null>(null)
  const loading = ref(false)

  const getCurrentLocation = (): Promise<Location> => {
    return new Promise((resolve, reject) => {
      loading.value = true
      error.value = null

      if (!navigator.geolocation) {
        error.value = 'Geolocation is not supported by this browser'
        loading.value = false
        reject(new Error(error.value))
        return
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const loc: Location = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: position.timestamp,
          }
          location.value = loc
          loading.value = false
          resolve(loc)
        },
        (err) => {
          let errorMsg = 'Failed to get location'
          switch (err.code) {
            case err.PERMISSION_DENIED:
              errorMsg = 'Permission denied. Please enable location access.'
              break
            case err.POSITION_UNAVAILABLE:
              errorMsg = 'Position information unavailable.'
              break
            case err.TIMEOUT:
              errorMsg = 'Request timeout for geolocation.'
              break
          }
          error.value = errorMsg
          loading.value = false
          reject(new Error(errorMsg))
        },
        {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0,
        }
      )
    })
  }

  const watchLocation = (callback: (location: Location) => void) => {
    if (!navigator.geolocation) {
      error.value = 'Geolocation is not supported'
      return null
    }

    return navigator.geolocation.watchPosition(
      (position) => {
        const loc: Location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          timestamp: position.timestamp,
        }
        location.value = loc
        callback(loc)
      },
      (err) => {
        error.value = `Geolocation error: ${err.message}`
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0,
      }
    )
  }

  return {
    location,
    error,
    loading,
    getCurrentLocation,
    watchLocation,
  }
}
