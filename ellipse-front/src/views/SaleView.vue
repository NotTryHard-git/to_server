<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePromotionStore } from '@/stores/promotion'

const route = useRoute()
const saleStore = usePromotionStore()

onMounted(async () => {
  if (!saleStore.promotions.length) {
    await saleStore.fetchPromotions()
  }
})

const promotion = computed(() =>
  saleStore.promotions.find((p) => p.id === route.params.id)
)
</script>

<template>
  <div class="promotion-view">
    <p v-if="saleStore.isLoading" class="promotion-view__status">Загрузка...</p>

    <div v-else-if="!promotion" class="promotion-view__status">
      <p>Акция не найдена.</p>
      <RouterLink to="/promotions" class="promotion-view__back-link">← Все акции</RouterLink>
    </div>

    <template v-else>
      <section class="hero">
        <img :src="promotion.image" :alt="promotion.title" class="hero__image" />

        <div class="hero__content">
          <span class="badge">{{ promotion.type }}</span>
          <h1>{{ promotion.title }}</h1>
          <p class="hero__text">{{ promotion.shortDescription }}</p>
        </div>
      </section>

      <section class="section">
        <div class="section-header">
          <p class="section-label">Подробнее</p>
          <h2>Описание</h2>
        </div>

        <p class="section__text">{{ promotion.description }}</p>
      </section>

      <section v-if="promotion.conditions?.length" class="section section--alt">
        <div class="section-header">
          <p class="section-label">Важно</p>
          <h2>Условия акции</h2>
        </div>

        <ul class="conditions-list">
          <li v-for="item in promotion.conditions" :key="item">{{ item }}</li>
        </ul>
      </section>
    </template>
  </div>
</template>

<style scoped>
.promotion-view {
  background: var(--color-main-bg);
  color: var(--color-main-text);
  font-family: var(--font-family-base);
}

.promotion-view__status {
  max-width: 600px;
  margin: 0 auto;
  padding: 100px 20px;
  text-align: center;
}

.promotion-view__back-link {
  display: inline-block;
  margin-top: 16px;
  color: var(--color-main-accent);
  text-decoration: none;
}

.promotion-view__back-link:hover {
  text-decoration: underline;
}

/* ---------- Hero ---------- */

.hero {
  position: relative;
  min-height: 420px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  background-color: var(--color-header-footer-bg);
}

.hero__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.55;
}

.hero__content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  padding: 60px;
  color: white;
}

.badge {
  display: inline-block;
  background-color: var(--color-header-footer-accent);
  color: var(--color-header-footer-bg);
  border-radius: 999px;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 16px;
}

.hero h1 {
  font-size: 40px;
  line-height: 1.15;
  margin-bottom: 12px;
}

.hero__text {
  font-size: 18px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.85);
}

/* ---------- Секции ---------- */

.section {
  padding: 70px 20px;
}

.section--alt {
  background: white;
}

.section-header {
  max-width: 700px;
  margin: 0 auto 32px;
  text-align: center;
}

.section-label {
  color: var(--color-main-accent);
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 12px;
  font-size: 14px;
}

.section-header h2 {
  font-size: 32px;
  line-height: 1.2;
}

.section__text {
  max-width: 700px;
  margin: 0 auto;
  font-size: 16px;
  line-height: 1.8;
  text-align: center;
}

.conditions-list {
  max-width: 700px;
  margin: 0 auto;
  padding-left: 20px;
}

.conditions-list li {
  font-size: 15px;
  line-height: 1.8;
  margin-bottom: 10px;
}

@media (max-width: 700px) {
  .hero h1 {
    font-size: 30px;
  }

  .hero__content {
    padding: 32px 24px;
  }

  .section-header h2 {
    font-size: 26px;
  }
}
</style>