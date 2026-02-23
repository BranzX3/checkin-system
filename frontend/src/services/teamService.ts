import api from './api'
import type { Team, TeamMember } from '@/types'

export const teamService = {
  async createTeam(data: { name: string; description?: string }): Promise<Team> {
    const response = await api.post('/api/v1/teams', data)
    return response.data
  },

  async getUserTeams(): Promise<Team[]> {
    const response = await api.get('/api/v1/teams')
    return response.data
  },

  async getTeamDetails(teamId: string): Promise<Team & { members: TeamMember[] }> {
    const response = await api.get(`/api/v1/teams/${teamId}`)
    return response.data
  },

  async joinTeam(teamCode: string): Promise<Team> {
    const response = await api.post('/api/v1/teams/join', {
      team_code: teamCode,
    })
    return response.data
  },

  async removeTeamMember(teamId: string, userId: string): Promise<void> {
    await api.post(`/api/v1/teams/${teamId}/members/${userId}/remove`)
  },
}
