import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { teamService } from '@/services/teamService'
import type { Team, TeamMember } from '@/types'

export const useTeamStore = defineStore('team', () => {
  const teams = ref<Team[]>([])
  const currentTeam = ref<Team | null>(null)
  const teamMembers = ref<TeamMember[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchUserTeams = async () => {
    loading.value = true
    error.value = null
    try {
      teams.value = await teamService.getUserTeams()
      if (teams.value.length > 0 && !currentTeam.value) {
        currentTeam.value = teams.value[0]
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch teams'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createTeam = async (data: { name: string; description?: string }) => {
    loading.value = true
    error.value = null
    try {
      const team = await teamService.createTeam(data)
      teams.value.push(team)
      currentTeam.value = team
      return team
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create team'
      throw err
    } finally {
      loading.value = false
    }
  }

  const joinTeam = async (teamCode: string) => {
    loading.value = true
    error.value = null
    try {
      const team = await teamService.joinTeam(teamCode)
      teams.value.push(team)
      currentTeam.value = team
      return team
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to join team'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchTeamDetails = async (teamId: string) => {
    loading.value = true
    error.value = null
    try {
      const teamDetail = await teamService.getTeamDetails(teamId)
      teamMembers.value = teamDetail.members
      return teamDetail
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch team details'
      throw err
    } finally {
      loading.value = false
    }
  }

  const removeTeamMember = async (teamId: string, userId: string) => {
    try {
      await teamService.removeTeamMember(teamId, userId)
      teamMembers.value = teamMembers.value.filter(m => m.user_id !== userId)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to remove member'
      throw err
    }
  }

  const setCurrentTeam = (team: Team) => {
    currentTeam.value = team
  }

  const clearError = () => {
    error.value = null
  }

  return {
    teams,
    currentTeam,
    teamMembers,
    loading,
    error,
    fetchUserTeams,
    createTeam,
    joinTeam,
    fetchTeamDetails,
    removeTeamMember,
    setCurrentTeam,
    clearError,
  }
})
