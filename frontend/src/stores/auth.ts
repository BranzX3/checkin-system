import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService, userService } from '@/services/authService'
import type { User, TokenData } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('accessToken'))
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)

  const setTokens = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  }

  const register = async (email: string, password: string, full_name?: string) => {
    loading.value = true
    error.value = null
    try {
      const newUser = await authService.register(email, password, full_name)
      user.value = newUser
      return newUser
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const login = async (email: string, password: string) => {
    loading.value = true
    error.value = null
    try {
      const tokenData: TokenData = await authService.login(email, password)
      setTokens(tokenData.access_token, tokenData.refresh_token)
      
      // Fetch current user
      const currentUser = await userService.getCurrentUser()
      user.value = currentUser
      
      return currentUser
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    error.value = null
  }

  const getCurrentUser = async () => {
    if (!isAuthenticated.value) return null
    try {
      const currentUser = await userService.getCurrentUser()
      user.value = currentUser
      return currentUser
    } catch (err) {
      logout()
      throw err
    }
  }

  const updateProfile = async (data: Partial<User>) => {
    try {
      const updated = await userService.updateProfile(data)
      user.value = updated
      return updated
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Update failed'
      throw err
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    isAuthenticated,
    setTokens,
    register,
    login,
    logout,
    getCurrentUser,
    updateProfile,
  }
})
