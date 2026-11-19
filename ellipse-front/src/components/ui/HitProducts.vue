<script setup>
import { onMounted } from 'vue'

import { useHomeStore } from '@/stores/home'
import ProductCard from '@/components/ui/ProductCard.vue'

const homeStore = useHomeStore()

onMounted(() => {
  homeStore.fetchHitProducts()
})
</script>

<template>
  <section class="hit-products">
    <div class="hit-products__header">
      <p class="hit-products__label">Выбор покупателей</p>
      <h2 class="hit-products__title">Хиты продаж</h2>
    </div>

    <p v-if="homeStore.isLoading" class="hit-products__status">Загрузка...</p>

    <div v-else class="hit-products__grid">
      <ProductCard
        v-for="product in homeStore.hitProducts"
        :key="product.id"
        :id="product.id"
        :name="product.name"
        :price="product.price"
        :image="product.image"
      />
    </div>
  </section>
</template>

<style scoped>
.hit-products {
  padding: 90px 20px;
  font-family: var(--font-family-base);
  color: var(--color-main-text);
}

.hit-products__header {
  max-width: 700px;
  margin: 0 auto 60px;
  text-align: center;
}

.hit-products__label {
  margin: 0 0 12px;
  color: var(--color-main-accent);
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-size: 14px;
}

.hit-products__title {
  margin: 0;
  font-size: 42px;
  line-height: 1.2;
}

.hit-products__status {
  text-align: center;
}

.hit-products__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
  max-width: 1200px;
  margin: 0 auto;
}

@media (max-width: 900px) {
  .hit-products__grid {
    grid-template-columns: 1fr;
  }

  .hit-products__title {
    font-size: 34px;
  }
}
</style>