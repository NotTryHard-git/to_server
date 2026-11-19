<script setup>
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Pagination,Autoplay } from 'swiper/modules'
import BaseButton from '@/components/ui/BaseButton.vue'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

defineProps({
  images: {
    type: Array,
    required: true,
  },
  height: {
    type: String,
    default: '420px',
  },
})
</script>

<template>
  <div class="image-slider" :style="{ height }">
    <Swiper
      :modules="[Navigation, Pagination, Autoplay]"
      :slides-per-view="1"
      :space-between="16"
      :observer="true"
      :observe-parents="true"
      :autoplay="{ delay: 4000, disableOnInteraction: false }"
      loop
      :navigation="{ nextEl: '.image-slider__nav--next', prevEl: '.image-slider__nav--prev' }"
      :pagination="{ clickable: true }"
      class="image-slider__swiper"
    >
      <SwiperSlide v-for="(image, index) in images" :key="index" class="image-slider__slide">
        <img :src="image" :alt="`Фото ${index + 1}`" class="image-slider__image" />
      </SwiperSlide>
    </Swiper>

    <BaseButton
      color="pink"
      shape="circle"
      size="sm"
      class="image-slider__nav image-slider__nav--prev"
      aria-label="Предыдущее фото"
    >
      ‹
    </BaseButton>
    <BaseButton
      color="pink"
      shape="circle"
      size="sm"
      class="image-slider__nav image-slider__nav--next"
      aria-label="Следующее фото"
    >
      ›
    </BaseButton>
  </div>
</template>

<style scoped>
.image-slider {
  position: relative;
  width: 100%;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
  max-width: 1200px;
}

.image-slider__swiper {
  width: 100%;
  height: 100%;
}

.image-slider__slide {
  display: flex;
  height: 100%;
}

.image-slider__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-slider__nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
  font-size: 22px;
  line-height: 1;
}

.image-slider__nav--prev {
  left: 16px;
}

.image-slider__nav--next {
  right: 16px;
}
</style>