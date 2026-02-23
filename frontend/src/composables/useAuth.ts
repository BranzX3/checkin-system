import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAuth() {
  const authStore = useAuthStore()
  const error = ref<string | null>(null)
  const isLoading = ref(false)

  const handleRegister = async (email: string, password: string, fullName?: string) => {
    isLoading.value = true
    error.value = null
    try {
      await authStore.register(email, password, fullName)
      return true
    } catch (err) {
      error.value = authStore.error || 'Registration failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const handleLogin = async (email: string, password: string) => {
    isLoading.value = true
    error.value = null
    try {
      await authStore.login(email, password)
      return true
    } catch (err) {
      error.value = authStore.error || 'Login failed'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const handleLogout = () => {
    authStore.logout()
  }

  const clearError = () => {
    error.value = null
    authStore.clearError()
  }

  return {
    user: computed(() => authStore.user),
    isAuthenticated: computed(() => authStore.isAuthenticated),
    loading: computed(() => authStore.loading),
    error: computed(() => error.value || authStore.error),
    handleRegister,
    handleLogin,
    handleLogout,
    clearError,
  }
}
