<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps({
  promotion: {
    type: Object,
    required: true,
  },
})

const period = computed(() => {
  if (props.promotion.type === 'permanent') {
    return 'Постоянная акция'
  }

  const start = new Date(props.promotion.startDate).toLocaleDateString('ru-RU')
  const end = new Date(props.promotion.endDate).toLocaleDateString('ru-RU')

  return `${start} — ${end}`
})
</script>

<template>
  <article class="promotion-card">
    <RouterLink
      :to="`/sale/${promotion.id}`"
      class="promotion-card__image-wrapper"
    >
      <img
        :src="promotion.image"
        :alt="promotion.title"
        class="promotion-card__image"
      />

      <span
        v-if="promotion.type === 'permanent'"
        class="promotion-card__badge"
      >
        Постоянно
      </span>
    </RouterLink>

    <div class="promotion-card__content">
      <p class="promotion-card__period">
        {{ period }}
      </p>

      <h3 class="promotion-card__title">
        {{ promotion.title }}
      </h3>

      <p class="promotion-card__description">
        {{ promotion.shortDescription }}
      </p>

      <RouterLink
          :to="`/sale/${promotion.id}`"
          class="promotion-card"
      >
        <BaseButton color="gold" class="promotion-card__button">
          Подробнее
        </BaseButton>
      </RouterLink>
    </div>
  </article>
</template>

<style scoped>
.promotion-card {
  display: flex;
  flex-direction: column;

  background: var(--color-header-footer-bg);
  color: var(--color-header-footer-text);

  border-radius: 18px;
  overflow: hidden;

  transition: .25s;
}

.promotion-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 18px 40px rgba(0,0,0,.18);
}

.promotion-card__image-wrapper {
  position: relative;
  display: block;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.promotion-card__image {
  width: 100%;
  height: 100%;

  object-fit: cover;

  transition: .35s;
}

.promotion-card:hover .promotion-card__image {
  transform: scale(1.05);
}

.promotion-card__badge {
  position: absolute;
  top: 14px;
  right: 14px;

  padding: 6px 12px;

  border-radius: 999px;

  background: var(--color-main-accent);
  color: var(--color-header-footer-bg);

  font-size: var(--text-caption);
  font-weight: var(--font-weight-semibold);
}

.promotion-card__content {
  display: flex;
  flex-direction: column;
  gap: 14px;

  padding: 24px;

  flex: 1;
}

.promotion-card__period {
  margin: 0;

  color: var(--color-main-accent);

  font-size: var(--text-small);
  font-weight: var(--font-weight-medium);
}

.promotion-card__title {
  margin: 0;

  font-size: var(--text-subtitle);
  font-weight: var(--font-weight-bold);

  line-height: 1.3;
}

.promotion-card__description {
  margin: 0;

  color: rgba(255,255,255,.75);

  line-height: 1.6;
}

.promotion-card__button {
  width: 100%;
  margin-top: auto;
}
</style>