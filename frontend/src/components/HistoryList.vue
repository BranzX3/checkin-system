<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-bold mb-4">Check-in History</h2>
    
    <div v-if="checkinStore.loading" class="text-center py-8">
      <p class="text-gray-500">Loading...</p>
    </div>

    <div v-else-if="checkinStore.checkins.length === 0" class="text-center py-8">
      <p class="text-gray-500">No check-ins yet</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="checkin in checkinStore.checkins"
        :key="checkin.id"
        class="border rounded-lg p-4 hover:shadow-md transition"
      >
        <div class="flex justify-between items-start mb-2">
          <div>
            <p class="font-semibold">
              {{ checkin.status === 'checked_in' ? '✓ Checked In' : '○ Checked Out' }}
            </p>
            <p class="text-sm text-gray-600">
              {{ formatDateTime(checkin.timestamp) }}
            </p>
          </div>
          <button
            @click="deleteCheckin(checkin.id)"
            class="text-red-500 hover:text-red-700 text-sm"
          >
            Delete
          </button>
        </div>

        <div class="text-sm text-gray-700 space-y-1">
          <p v-if="checkin.location_name">
            📍 {{ checkin.location_name }}
          </p>
          <p v-if="checkin.duration_minutes">
            ⏱️ {{ checkin.duration_minutes }} minutes
          </p>
          <p v-if="checkin.notes" class="text-gray-600">
            📝 {{ checkin.notes }}
          </p>
          <p v-if="checkin.mood">
            😊 Mood: {{ checkin.mood.mood_level }}/5
          </p>
        </div>
      </div>
    </div>

    <button
      v-if="!checkinStore.loading && checkinStore.checkins.length > 0"
      @click="loadMore"
      class="w-full mt-4 py-2 text-blue-500 hover:text-blue-700 border border-blue-500 rounded hover:bg-blue-50 transition"
    >
      Load More
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCheckinStore } from '@/stores/checkin'
import { format } from 'date-fns'

const checkinStore = useCheckinStore()
const page = ref(0)
const limit = 20

onMounted(async () => {
  await checkinStore.fetchCheckins(0, limit)
})

const formatDateTime = (timestamp: string) => {
  return format(new Date(timestamp), 'MMM d, yyyy HH:mm')
}

const deleteCheckin = async (checkinId: string) => {
  if (confirm('Are you sure?')) {
    await checkinStore.deleteCheckin(checkinId)
  }
}

const loadMore = async () => {
  page.value++
  const checkins = await checkinStore.fetchCheckins(page.value * limit, limit)
}
</script>
