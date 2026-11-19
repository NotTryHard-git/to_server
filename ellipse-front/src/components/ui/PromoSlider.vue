<script setup>
import { computed } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Pagination, Autoplay } from 'swiper/modules'
import { RouterLink } from 'vue-router'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

const props = defineProps({
  promotions: {
    type: Array,
    default: () => [],
  },
})

// Слайдер — визуальная карусель баннеров, а не список текста. Бессрочные
// акции без картинки (скидка по средам, имениннику, студентам и т.п.) сюда
// не подходят — для них есть отдельный список на странице акций. Показываем
// только те акции, у которых реально есть баннер.
const slides = computed(() => props.promotions.filter((promotion) => promotion.image))
</script>

<template>
  <div v-if="slides.length" class="promo-slider">
    <Swiper
      :modules="[Navigation, Pagination, Autoplay]"
      :slides-per-view="1"
      :space-between="16"
      :observer="true"
      :observe-parents="true"
      :autoplay="{ delay: 4000, disableOnInteraction: false }"
      :loop="slides.length > 1"
      :navigation="slides.length > 1"
      :pagination="{ clickable: true }"
      class="promo-slider__swiper"
    >
      <SwiperSlide
        v-for="promotion in slides"
        :key="promotion.id"
        class="promo-slider__slide"
      >
        <RouterLink :to="`/sale/${promotion.id}`" class="promo-slider__card">
          <img
            :src="promotion.image"
            :alt="promotion.title"
            class="promo-slider__image"
          />
        </RouterLink>
      </SwiperSlide>
    </Swiper>
  </div>
</template>

<style scoped>
/*
  Рекомендуемое соотношение сторон баннера — 1920:600 (стандартный широкий
  промо-баннер интернет-магазинов). Картинка растягивается на всю область
  слайда (object-fit: cover, без чёрных полос) — если баннер сильно
  отличается по пропорциям от 1920:600, края будут обрезаны, поэтому
  желательно всё же готовить баннеры в этом разрешении (или кратном ему).
*/
.promo-slider {
  position: relative;
  width: 100%;
  aspect-ratio: 1920 / 800;
}

.promo-slider__swiper {
  width: 100%;
  height: 100%;
}

.promo-slider__slide {
  display: flex;
  height: 100%;
}

.promo-slider__card {
  display: flex;
  justify-content: center;
  align-items: center;

  width: 100%;
  height: 100%;
}

.promo-slider__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.promo-slider__title {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  margin: 0;
  padding: 8px 24px;
  font-size: 20px;
  font-weight: 600;
  text-align: center;
}

.promo-slider__swiper :deep(.swiper-button-next),
.promo-slider__swiper :deep(.swiper-button-prev) {
  color: var(--color-main-accent);
}

.promo-slider__swiper :deep(.swiper-pagination-bullet-active) {
  background-color: var(--color-main-accent);
}
</style>