import { reactive } from 'vue'

export interface User {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  timezone: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Checkin {
  id: string
  user_id: string
  status: 'checked_in' | 'checked_out'
  timestamp: string
  location_latitude?: number
  location_longitude?: number
  location_name?: string
  notes?: string
  duration_minutes?: number
  mood_id?: string
  goal_id?: string
  created_at: string
  updated_at: string
}

export interface Mood {
  id: string
  user_id: string
  mood_level: number
  emotion?: string
  notes?: string
  created_at: string
}

export interface Goal {
  id: string
  user_id: string
  title: string
  description?: string
  is_completed: boolean
  priority: 'high' | 'medium' | 'low'
  created_at: string
  updated_at: string
}

export interface Team {
  id: string
  name: string
  code: string
  description?: string
  created_by: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TeamMember {
  user_id: string
  role: 'owner' | 'manager' | 'member'
  joined_at: string
}

export interface TokenData {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface DailyStats {
  total_checkins_today: number
  is_checked_in: boolean
  latest_checkin?: Checkin
  total_duration_minutes: number
  mood_history: Mood[]
}
