import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiFetch } from '@/api/client'

export const useHomeStore = defineStore('home', () => {
  const hitProducts = ref([])
  const isLoading = ref(false)

  async function fetchHitProducts() {
    isLoading.value = true
    try {
      const data = await apiFetch('/api/products/hits')
      hitProducts.value = data.map((item) => ({
        id: item.id,
        name: item.name,
        price: item.price,
        image: item.image,
        brand: item.brand,
      }))
    } finally {
      isLoading.value = false
    }
  }

  return {
    hitProducts,
    isLoading,
    fetchHitProducts,
  }
})