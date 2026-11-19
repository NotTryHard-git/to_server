<script setup>
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Pagination } from 'swiper/modules'

import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

const props = defineProps({
  photos: {
    type: Array,
    default: () => [],
  },
  // Порог, после которого сетка превращается в слайдер
  gridThreshold: {
    type: Number,
    default: 3,
  },
  alt: {
    type: String,
    default: '',
  },
})

const modules = [Navigation, Pagination]
</script>

<template>
  <div class="photo-gallery">
    <Swiper
      v-if="props.photos.length > props.gridThreshold"
      :modules="modules"
      :slides-per-view="1"
      :centered-slides="true"
      :space-between="16"
      navigation
      :pagination="{ clickable: true }"
      class="photo-gallery__slider"
    >
      <SwiperSlide v-for="(photo, index) in props.photos" :key="index">
        <img :src="photo" :alt="`${props.alt} — фото ${index + 1}`" class="photo-gallery__image" />
      </SwiperSlide>
    </Swiper>

    <div v-else-if="props.photos.length" class="photo-gallery__grid">
      <img
        v-for="(photo, index) in props.photos"
        :key="index"
        :src="photo"
        :alt="`${props.alt} — фото ${index + 1}`"
        class="photo-gallery__image"
      />
    </div>

    <div v-else class="photo-gallery__grid">
      <div v-for="n in 3" :key="n" class="photo-gallery__image photo-gallery__image--placeholder" />
    </div>
  </div>
</template>

<style scoped>
.photo-gallery__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.photo-gallery__image {
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: 14px;
  object-fit: cover;
  display: block;
}

.photo-gallery__image--placeholder {
  background-color: var(--color-main-accent);
  opacity: 0.4;
}

.photo-gallery__slider {
  padding-bottom: 36px; /* место под точки пагинации */
}

.photo-gallery__slider :deep(.swiper-button-next),
.photo-gallery__slider :deep(.swiper-button-prev) {
  color: var(--color-main-accent);
}

.photo-gallery__slider :deep(.swiper-pagination-bullet-active) {
  background: var(--color-main-accent);
}

@media (max-width: 900px) {
  .photo-gallery__grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 560px) {
  .photo-gallery__grid {
    grid-template-columns: 1fr;
  }
}
</style>