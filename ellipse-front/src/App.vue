<script setup>
import { onMounted } from 'vue'
import { useCityStore } from '@/stores/city'
import CityModal from '@/components/layout/CityModal.vue'
import Header from '@/components/layout/Header.vue'
import Footer from '@/components/layout/Footer.vue'
import CookieConsent from '@/components/layout/CookieConsent.vue'

const cityStore = useCityStore()

onMounted(() => {
  cityStore.init()
})
</script>

<template>
  <CookieConsent />
  <CityModal />
  <Header />
  <RouterView />
  <Footer />
</template>