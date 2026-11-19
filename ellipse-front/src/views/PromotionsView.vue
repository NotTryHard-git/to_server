<script setup>
import { computed, onMounted, ref } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Pagination } from 'swiper/modules'
import { usePromotionStore } from '@/stores/promotion'
import PromotionCard from '@/components/ui/PromotionCard.vue'
import PromotionCalendar from '@/components/ui/PromotionCalendar.vue'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

const promotionStore = usePromotionStore()
const modules = [Navigation, Pagination]

// Такой же порог, как у слайдера фотографий магазинов: больше — слайдер, меньше/равно — сетка
const GRID_THRESHOLD = 3
const promotionSliderBreakpoints = {
  0: { slidesPerView: 1.1, spaceBetween: 16 },
  640: { slidesPerView: 2, spaceBetween: 20 },
  1024: { slidesPerView: 3, spaceBetween: 24 },
}

const selectedDate = ref(new Date())

onMounted(async () => {
  if (!promotionStore.promotions.length) {
    await promotionStore.fetchPromotions()
  }
})

// Используется в закомментированной секции «Главная акция» ниже
// eslint-disable-next-line no-unused-vars
const featuredPromotions = computed(() => promotionStore.featuredPromotions)
const temporaryPromotions = computed(() => promotionStore.temporaryPromotions)
const permanentPromotions = computed(() => promotionStore.permanentPromotions)

const selectedDayPromotions = computed(() =>
  promotionStore.promotionsByDate(selectedDate.value),
)
</script>

<template>
  <div class="sale-view">
    <!-- Hero -->
    <section class="sale-hero">
      <h1 class="sale-hero__title">Акции и специальные предложения</h1>

      <p class="sale-hero__subtitle">
        Выгодные предложения, подарки и скидки, которые сделают ваши покупки ещё приятнее.
      </p>
    </section>

    <!-- Главная акция 
    <section
      v-if="featuredPromotions.length"
      class="sale-section"
    >
      <div class="section-header">
        <p class="section-label">Главное предложение</p>
        <h2>Акция месяца</h2>
      </div>

      <div class="featured-promotion">
       позже сюда баннер 
      </div>
    </section>-->

    <!-- Все временные акции -->
    <section class="sale-section">
      <div class="section-header">
        <p class="section-label">Сейчас действует</p>
        <h2>Временные акции</h2>
      </div>

      <Swiper
        v-if="temporaryPromotions.length > GRID_THRESHOLD"
        :modules="modules"
        :breakpoints="promotionSliderBreakpoints"
        navigation
        :pagination="{ clickable: true }"
        class="promotion-slider"
      >
        <SwiperSlide v-for="promotion in temporaryPromotions" :key="promotion.id">
          <PromotionCard :promotion="promotion" />
        </SwiperSlide>
      </Swiper>

      <div v-else class="promotion-grid">
         <PromotionCard
            v-for="promotion in temporaryPromotions"
            :key="promotion.id"
            :promotion="promotion"
          />
      </div>
    </section>

    <!-- Календарь -->
    <section class="sale-section">
      <div class="section-header">
        <p class="section-label">Календарь</p>
        <h2>Акции по дням</h2>
      </div>

      <div class="calendar-block">
            <PromotionCalendar
          v-model="selectedDate"
          :promotions="temporaryPromotions"
            />
      </div>

      <div class="promotion-grid">
        
        <PromotionCard
            v-for="promotion in selectedDayPromotions"
            :key="promotion.id"
            :promotion="promotion"
          />
      </div>
    </section>

    <!-- Постоянные предложения -->
    <section class="sale-section">
      <div class="section-header">
        <p class="section-label">Всегда доступно</p>
        <h2>Постоянные предложения</h2>
      </div>

      <div class="promotion-grid">
        <PromotionCard
            v-for="promotion in permanentPromotions"
            :key="promotion.id"
            :promotion="promotion"
          />
      </div>
    </section>
  </div>
</template>
<style scoped>
.sale-view {
  background-color: var(--color-main-bg);
  color: var(--color-main-text);
  font-family: var(--font-family-base);
}

.sale-hero {
  max-width: 900px;
  margin: 0 auto;
  padding: 64px 32px 40px;
  text-align: center;
}

.sale-hero__title {
  margin: 0 0 16px;
  font-size: var(--text-page-title);
  font-weight: var(--font-weight-bold);
}

.sale-hero__subtitle {
  margin: 0;
  color: var(--color-main-accent);
  font-size: var(--text-body-lg);
  line-height: var(--line-height-normal);
}

.sale-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 32px;
}

.section-header {
  margin-bottom: 32px;
  text-align: center;
}

.section-label {
  margin: 0 0 8px;
  color: var(--color-main-accent);
  font-size: var(--text-caption);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.section-header h2 {
  margin: 0;
  font-size: var(--text-title);
  font-weight: var(--font-weight-bold);
}

/* ------------------------------ */
/* Главная акция                  */
/* ------------------------------ */

.featured-promotion {
  min-height: 380px;

  display: flex;
  justify-content: center;
  align-items: center;

  border-radius: 20px;

  background: var(--color-header-footer-bg);
  color: var(--color-header-footer-text);

  border: 1px solid rgba(255,255,255,.08);
}

/* ------------------------------ */
/* Сетка карточек                 */
/* ------------------------------ */

.promotion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.promotion-slider {
  padding-bottom: 40px; /* место под точки пагинации */
}

.promotion-slider :deep(.swiper-slide) {
  height: auto;
}

.promotion-slider :deep(.swiper-button-next),
.promotion-slider :deep(.swiper-button-prev) {
  color: var(--color-main-accent);
}

.promotion-slider :deep(.swiper-pagination-bullet-active) {
  background: var(--color-main-accent);
}

.promotion-card {
  min-height: 260px;

  display: flex;
  flex-direction: column;

  border-radius: 16px;

  background: var(--color-header-footer-bg);
  color: var(--color-header-footer-text);

  overflow: hidden;

  transition:
    transform .25s ease,
    box-shadow .25s ease;
}

.promotion-card:hover {
  transform: translateY(-6px);

  box-shadow: 0 16px 40px rgba(0,0,0,.18);
}

/* ------------------------------ */
/* Календарь                      */
/* ------------------------------ */

.calendar-block {
  min-height: 420px;

  margin-bottom: 40px;

  border-radius: 20px;

  background: var(--color-header-footer-bg);

  display: flex;
  justify-content: center;
  align-items: center;

  color: var(--color-header-footer-text);

  border: 1px solid rgba(255,255,255,.08);
}

/* ------------------------------ */
/* Адаптив                        */
/* ------------------------------ */

@media (max-width: 900px) {
  .sale-section {
    padding: 40px 24px;
  }

  .promotion-grid {
    grid-template-columns: 1fr;
  }

  .featured-promotion {
    min-height: 300px;
  }

  .calendar-block {
    min-height: 360px;
  }
}

@media (max-width: 600px) {
  .sale-hero {
    padding: 48px 20px 32px;
  }

  .sale-section {
    padding: 32px 20px;
  }

  .sale-hero__title {
    font-size: var(--text-title);
  }

  .sale-hero__subtitle {
    font-size: var(--text-body);
  }
}
</style>