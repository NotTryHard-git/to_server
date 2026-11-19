import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    isMenuOpen: false,
    isLoading: false,
  }),

  actions: {
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen
    },

    startLoading() {
      this.isLoading = true
    },

    stopLoading() {
      this.isLoading = false
    },
  },
})
