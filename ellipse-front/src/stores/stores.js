import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/api/client'

const CITIES = ['Томск', 'Северск', 'Новокузнецк', 'Кемерово']

function mapStore(item) {
  return {
    id: item.id,
    city: item.city,
    adress: item.address,
    location:
      item.latitude != null && item.longitude != null
        ? [Number(item.latitude), Number(item.longitude)]
        : null,
    phone: item.phone,
    working_hours: item.working_hours,
    photos: item.images || [],
  }
}

export const useStoresStore = defineStore('stores', () => {
  const cities = CITIES

  const stores = ref([])
  const isLoading = ref(false)
  const selectedCity = ref(cities[0])
  const selectedStoreId = ref(null)

  const storesInSelectedCity = computed(() =>
    stores.value.filter((store) => store.city === selectedCity.value)
  )

  const selectedStore = computed(
    () => stores.value.find((store) => store.id === selectedStoreId.value) || null
  )

  function selectCity(city) {
    selectedCity.value = city
    const firstStore = stores.value.find((store) => store.city === city)
    selectedStoreId.value = firstStore ? firstStore.id : null
  }

  function selectStore(id) {
    selectedStoreId.value = id
  }

  async function fetchStores() {
    isLoading.value = true
    try {
      const data = await apiFetch('/stores/')
      stores.value = data.map(mapStore)
      selectCity(selectedCity.value)
    } finally {
      isLoading.value = false
    }
  }

  return {
    cities,
    stores,
    isLoading,
    selectedCity,
    selectedStoreId,
    storesInSelectedCity,
    selectedStore,
    fetchStores,
    selectCity,
    selectStore,
  }
})