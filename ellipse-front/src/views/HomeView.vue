<script setup>
import PromoSlider from '@/components/ui/PromoSlider.vue'
import HitProducts from '@/components/ui/HitProducts.vue'
import { usePromotionStore } from '@/stores/promotion'
import {  onMounted } from 'vue'
const promotionStore = usePromotionStore()

onMounted(async () => {
  if (!promotionStore.promotions.length) {
    await promotionStore.fetchPromotions()
  }
})
</script>

<template>
  <div class="home-view">
    <PromoSlider :promotions="promotionStore.featuredPromotions" />
    <HitProducts />
  </div>
</template>

<style scoped>
.home-view {
  background-color: var(--color-main-bg);
  font-family: var(--font-family-base);
}
</style>