// src/stores/promotionStore.js

import { defineStore } from 'pinia'
import { apiFetch } from '@/api/client'

function mapPromotion(item) {
  return {
    id: item.id,
    title: item.title,
    shortDescription: item.short_description,
    description: item.description,
    image: item.banner,
    bannerImage: item.banner,
    type: item.type,
    startDate: item.start_date,
    endDate: item.end_date,
    isPublished: item.is_active,
  }
}

export const usePromotionStore = defineStore('promotions', {
  state: () => ({
    promotions: [],
    isLoading: false,
  }),

  getters: {
    // backend пока не хранит priority/isFeatured — сортировки по приоритету нет,
    // возвращаются все опубликованные акции
    featuredPromotions: (state) => state.promotions.filter((p) => p.isPublished),

    permanentPromotions: (state) =>
      state.promotions.filter((p) => p.isPublished && p.type === 'permanent'),

    temporaryPromotions: (state) =>
      state.promotions.filter((p) => p.isPublished && p.type === 'temporary'),

    // backend пока не хранит slug — всегда вернёт undefined, см. комментарий в чате
    getPromotionBySlug: (state) => (slug) =>
      state.promotions.find((promotion) => promotion.slug === slug),

    promotionsByDate: (state) => (date) =>
      state.promotions.filter((promotion) => {
        if (promotion.type === 'permanent' || !promotion.startDate || !promotion.endDate) {
          return false
        }

        const current = new Date(date)
        current.setHours(0, 0, 0, 0)
        const start = new Date(promotion.startDate)
        start.setHours(0, 0, 0, 0)
        const end = new Date(promotion.endDate)
        end.setHours(0, 0, 0, 0)
        return current >= start && current <= end
      }),
  },

  actions: {
    async fetchPromotions() {
      this.isLoading = true
      try {
        const data = await apiFetch('/promotions/')
        this.promotions = data.map(mapPromotion)
      } finally {
        this.isLoading = false
      }
    },
  },
})