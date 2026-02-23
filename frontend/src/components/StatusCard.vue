<template>
  <div class="bg-white rounded-lg shadow-md p-6 max-w-md mx-auto">
    <div v-if="checkinStore.isCheckedIn" class="text-center">
      <div class="text-6xl mb-4">✓</div>
      <h2 class="text-2xl font-bold text-green-600 mb-2">Checked In</h2>
      <p v-if="checkinStore.todayStats?.latest_checkin" class="text-gray-600">
        Since {{ formatTime(checkinStore.todayStats.latest_checkin.timestamp) }}
      </p>
      <button
        @click="showCheckout = true"
        class="mt-4 bg-red-500 text-white px-6 py-2 rounded hover:bg-red-600 transition"
      >
        Check Out
      </button>
    </div>

    <div v-else class="text-center">
      <div class="text-6xl mb-4">○</div>
      <h2 class="text-2xl font-bold text-gray-600 mb-2">Checked Out</h2>
      <button
        @click="openCheckinModal"
        class="mt-4 bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600 transition"
      >
        Check In
      </button>
    </div>

    <!-- Check In Modal -->
    <div v-if="showCheckin" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-bold mb-4">Check In</h3>

        <div class="space-y-4">
          <!-- Mood -->
          <div>
            <label class="block text-sm font-medium mb-1">Mood Level (1-5)</label>
            <div class="flex gap-2">
              <button
                v-for="level in [1, 2, 3, 4, 5]"
                :key="level"
                @click="moodLevel = level"
                :class="[
                  'flex-1 py-2 rounded transition',
                  moodLevel === level ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'
                ]"
              >
                {{ moodEmojis[level - 1] }}
              </button>
            </div>
          </div>

          <!-- Location Map -->
          <div>
            <label class="block text-sm font-medium mb-1">Location</label>

            <!-- Location Name Display -->
            <div class="flex items-center gap-2 mb-2">
              <input
                v-model="locationName"
                type="text"
                placeholder="Location name (optional)"
                class="flex-1 px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
              <button
                @click="getCurrentLocation"
                :disabled="isGettingLocation"
                class="px-3 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition text-sm flex items-center gap-1 whitespace-nowrap"
                title="Use my current location"
              >
                <span>{{ isGettingLocation ? '⌛' : '📍' }}</span>
                <span>{{ isGettingLocation ? 'Locating...' : 'My Location' }}</span>
              </button>
            </div>

            <!-- Lat/Lng Display -->
            <div v-if="selectedLat !== null" class="text-xs text-gray-500 mb-2 font-mono bg-gray-50 px-2 py-1 rounded">
              {{ selectedLat.toFixed(6) }}, {{ selectedLng.toFixed(6) }}
            </div>

            <!-- Map Container -->
            <div
              ref="mapContainer"
              class="w-full h-48 rounded border border-gray-300 overflow-hidden relative"
              style="z-index: 1;"
            >
              <div v-if="!mapReady" class="absolute inset-0 flex items-center justify-center bg-gray-100 text-gray-500 text-sm">
                Loading map...
              </div>
            </div>
            <p class="text-xs text-gray-400 mt-1">Click on the map to pin your location</p>
          </div>

          <!-- Notes -->
          <div>
            <label class="block text-sm font-medium mb-1">Notes</label>
            <textarea
              v-model="notes"
              placeholder="Any notes about your day..."
              class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
            ></textarea>
          </div>

          <div class="flex gap-2">
            <button
              @click="submitCheckin"
              :disabled="isLoading"
              class="flex-1 bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:bg-gray-400 transition"
            >
              {{ isLoading ? 'Checking in...' : 'Confirm' }}
            </button>
            <button
              @click="cancelCheckin"
              class="flex-1 bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400 transition"
            >
              Cancel
            </button>
          </div>

          <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Check Out Modal -->
    <div v-if="showCheckout" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Check Out</h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Mood Level (1-5)</label>
            <div class="flex gap-2">
              <button
                v-for="level in [1, 2, 3, 4, 5]"
                :key="level"
                @click="moodLevel = level"
                :class="[
                  'flex-1 py-2 rounded transition',
                  moodLevel === level ? 'bg-blue-500 text-white' : 'bg-gray-200 hover:bg-gray-300'
                ]"
              >
                {{ moodEmojis[level - 1] }}
              </button>
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Notes</label>
            <textarea
              v-model="notes"
              placeholder="Reflections on today..."
              class="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="3"
            ></textarea>
          </div>

          <div class="flex gap-2">
            <button
              @click="submitCheckout"
              :disabled="isLoading"
              class="flex-1 bg-red-500 text-white py-2 rounded hover:bg-red-600 disabled:bg-gray-400 transition"
            >
              {{ isLoading ? 'Checking out...' : 'Confirm' }}
            </button>
            <button
              @click="cancelCheckout"
              class="flex-1 bg-gray-300 text-gray-700 py-2 rounded hover:bg-gray-400 transition"
            >
              Cancel
            </button>
          </div>

          <p v-if="error" class="text-red-500 text-sm text-center">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useCheckinStore } from '@/stores/checkin'
import { useCheckin } from '@/composables/useCheckin'
import { format } from 'date-fns'
import { useLocation } from '@/composables/useLocation'

const checkinStore = useCheckinStore()
const { handleCheckIn, handleCheckOut } = useCheckin()

const showCheckin = ref(false)
const showCheckout = ref(false)
const moodLevel = ref(3)
const locationName = ref('')
const notes = ref('')
const error = ref<string | null>(null)
const isLoading = ref(false)
const { getCurrentLocation: getGPS, loading: isGettingLocation } = useLocation()  

// Map state
const mapContainer = ref<HTMLElement | null>(null)
const mapReady = ref(false)
const selectedLat = ref<number | null>(null)
const selectedLng = ref<number | null>(null)

const moodEmojis = ['😞', '😕', '😐', '😊', '😄']

// Leaflet instance references (avoid reactivity issues)
let leafletMap: any = null
let marker: any = null
let L: any = null

const loadLeaflet = async () => {
  if (L) return L

  // Load Leaflet CSS
  if (!document.getElementById('leaflet-css')) {
    const link = document.createElement('link')
    link.id = 'leaflet-css'
    link.rel = 'stylesheet'
    link.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'
    document.head.appendChild(link)
  }

  // Load Leaflet JS
  if (!(window as any).L) {
    await new Promise<void>((resolve, reject) => {
      const script = document.createElement('script')
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'
      script.onload = () => resolve()
      script.onerror = () => reject(new Error('Failed to load Leaflet'))
      document.head.appendChild(script)
    })
  }

  L = (window as any).L
  return L
}

const initMap = async (lat: number, lng: number) => {
  if (!mapContainer.value) return

  try {
    await loadLeaflet()

    // Destroy existing map
    if (leafletMap) {
      leafletMap.remove()
      leafletMap = null
      marker = null
    }

    await nextTick()

    leafletMap = L.map(mapContainer.value).setView([lat, lng], 15)

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(leafletMap)

    // Custom marker icon (fix default Leaflet icon path issue in bundlers)
    const icon = L.icon({
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41],
    })

    marker = L.marker([lat, lng], { icon, draggable: true }).addTo(leafletMap)
    selectedLat.value = lat
    selectedLng.value = lng

    // Click on map to move marker
    leafletMap.on('click', (e: any) => {
      const { lat, lng } = e.latlng
      marker.setLatLng([lat, lng])
      selectedLat.value = lat
      selectedLng.value = lng
    })

    // Drag marker
    marker.on('dragend', (e: any) => {
      const pos = e.target.getLatLng()
      selectedLat.value = pos.lat
      selectedLng.value = pos.lng
    })

    mapReady.value = true

    // Fix map size after modal renders
    setTimeout(() => leafletMap?.invalidateSize(), 100)
  } catch (err) {
    console.error('Map init failed:', err)
    mapReady.value = false
  }
}

const getCurrentLocation = async () => {
  try {
    const loc = await getGPS()
    await initMap(loc.latitude, loc.longitude)
  } catch (err: any) {
    error.value = err.message
  }
}

const openCheckinModal = async () => {
  showCheckin.value = true
  await nextTick()

  try {
    const loc = await getGPS()
    await initMap(loc.latitude, loc.longitude)
  } catch {
    // fallback to Bangkok
    await initMap(13.7563, 100.5018)
  }
}

const formatTime = (timestamp: string) => {
  return format(new Date(timestamp), 'HH:mm')
}

const submitCheckin = async () => {
  isLoading.value = true
  error.value = null

  try {
    await handleCheckIn({
      location_name: locationName.value || 'Unknown',
      latitude: selectedLat.value ?? undefined,
      longitude: selectedLng.value ?? undefined,
      notes: notes.value,
      mood: {
        mood_level: moodLevel.value,
        emotion: getEmotion(moodLevel.value),
      },
    })
    showCheckin.value = false
    destroyMap()
    resetForm()
  } catch (err: any) {
    error.value = err.message || 'Check-in failed'
  } finally {
    isLoading.value = false
  }
}

const submitCheckout = async () => {
  isLoading.value = true
  error.value = null

  try {
    await handleCheckOut({
      notes: notes.value,
      mood: {
        mood_level: moodLevel.value,
        emotion: getEmotion(moodLevel.value),
      },
    })
    showCheckout.value = false
    resetForm()
  } catch (err: any) {
    error.value = err.message || 'Check-out failed'
  } finally {
    isLoading.value = false
  }
}

const destroyMap = () => {
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
    marker = null
    mapReady.value = false
  }
}

const cancelCheckin = () => {
  showCheckin.value = false
  destroyMap()
  resetForm()
}

const cancelCheckout = () => {
  showCheckout.value = false
  resetForm()
}

const resetForm = () => {
  moodLevel.value = 3
  locationName.value = ''
  notes.value = ''
  error.value = null
  selectedLat.value = null
  selectedLng.value = null
}

const getEmotion = (level: number): string => {
  const emotions = ['very_sad', 'sad', 'neutral', 'happy', 'very_happy']
  return emotions[level - 1] || 'neutral'
}

onUnmounted(() => {
  destroyMap()
})
</script>