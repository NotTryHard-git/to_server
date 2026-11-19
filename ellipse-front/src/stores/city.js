import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'ellips-selected-city'

const CITIES = ['Томск', 'Северск', 'Кемерово', 'Новокузнецк']

export const useCityStore = defineStore('city', () => {
  const cities = CITIES
  const selectedCity = ref(null)
  const isModalOpen = ref(false)

  // Вызывается один раз при старте приложения (в App.vue)
  function init() {
    const saved = localStorage.getItem(STORAGE_KEY)

    if (saved && cities.includes(saved)) {
      selectedCity.value = saved
    } else {
      // Города ещё нет — показываем модалку выбора при первом визите
      selectedCity.value = cities[0]
      isModalOpen.value = true
    }
  }

  function selectCity(city) {
    selectedCity.value = city
    localStorage.setItem(STORAGE_KEY, city)
    isModalOpen.value = false
  }

  function openModal() {
    isModalOpen.value = true
  }

  function closeModal() {
    isModalOpen.value = false
  }

  return {
    cities,
    selectedCity,
    isModalOpen,
    init,
    selectCity,
    openModal,
    closeModal,
  }
})