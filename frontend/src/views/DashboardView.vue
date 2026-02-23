<template>
  <div class="space-y-8">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <StatusCard />
      
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold mb-4">Today's Stats</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-600">Check-ins:</span>
            <span class="font-semibold">{{ checkinStore.todayStats?.total_checkins_today || 0 }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Duration:</span>
            <span class="font-semibold">{{ checkinStore.totalDurationToday }} mins</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Status:</span>
            <span :class="checkinStore.isCheckedIn ? 'text-green-500 font-semibold' : 'text-gray-500'">
              {{ checkinStore.isCheckedIn ? 'Checked In' : 'Checked Out' }}
            </span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-bold mb-4">Today's Goals</h2>
        <div v-if="goals.length === 0" class="text-gray-500 text-sm">
          No goals yet
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="goal in goals"
            :key="goal.id"
            class="text-sm flex items-start gap-2"
          >
            <input
              type="checkbox"
              :checked="goal.is_completed"
              @change="updateGoal(goal.id, !goal.is_completed)"
              class="mt-1"
            />
            <span :class="goal.is_completed && 'line-through text-gray-400'">
              {{ goal.title }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <HistoryList />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCheckinStore } from '@/stores/checkin'
import { goalService } from '@/services/checkinService'
import StatusCard from '@/components/StatusCard.vue'
import HistoryList from '@/components/HistoryList.vue'
import type { Goal } from '@/types'

const checkinStore = useCheckinStore()
const goals = ref<Goal[]>([])

onMounted(async () => {
  await checkinStore.fetchTodayStats()
  const activeGoals = await goalService.getGoals(false)
  goals.value = activeGoals
})

const updateGoal = async (goalId: string, completed: boolean) => {
  await goalService.updateGoal(goalId, { is_completed: completed })
  goals.value = goals.value.map(g =>
    g.id === goalId ? { ...g, is_completed: completed } : g
  )
}
</script>
