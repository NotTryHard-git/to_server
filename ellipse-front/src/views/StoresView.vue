<script setup>
import { onMounted } from 'vue'

import { useStoresStore } from '@/stores/stores'
import BaseButton from '@/components/ui/BaseButton.vue'
import MapEmbed from '@/components/ui/MapEmbed.vue'
import PhotoGallery from '@/components/ui/PhotoGallery.vue'

const storesStore = useStoresStore()

onMounted(() => {
  storesStore.fetchStores()
})
</script>

<template>
  <div class="stores-view">
    <section class="hero">
      <div class="hero__content">
        <p class="hero__label">Магазины e'llipse</p>
        <h1>Найдите магазин рядом с вами</h1>
        <p class="hero__text">Выберите город — покажем адреса, контакты и режим работы.</p>
      </div>
    </section>

    <section class="stores">
      <div class="city-tabs">
        <BaseButton
          v-for="city in storesStore.cities"
          :key="city"
          :color="city === storesStore.selectedCity ? 'accent' : 'pink'"
          :variant="city === storesStore.selectedCity ? 'solid' : 'outline'"
          shape="pill"
          size="md"
          @click="storesStore.selectCity(city)"
        >
          {{ city }}
        </BaseButton>
      </div>

      <p v-if="storesStore.isLoading" class="stores__status">Загрузка...</p>

      <template v-else-if="storesStore.selectedStore">
        <div class="stores-layout">
          <div class="store-list">
            <BaseButton
              v-for="store in storesStore.storesInSelectedCity"
              :key="store.id"
              color="pink"
              shape="block"
              variant="ghost"
              :active="store.id === storesStore.selectedStoreId"
              class="store-list__item"
              @click="storesStore.selectStore(store.id)"
            >
              {{ store.adress }}
            </BaseButton>
          </div>

          <div class="store-map">
            <MapEmbed
              :lat="storesStore.selectedStore.location[0]"
              :lon="storesStore.selectedStore.location[1]"
              :aria-label="`Магазин: ${storesStore.selectedStore.adress}`"
              height="100%"
            />
          </div>
        </div>

        <div class="store-info">
          <h3>{{ storesStore.selectedStore.city }}, {{ storesStore.selectedStore.adress }}</h3>

          <div class="store-info__row">
            <a :href="`tel:${storesStore.selectedStore.phone.replace(/\\D/g, '')}`" class="store-info__link">
              {{ storesStore.selectedStore.phone }}
            </a>
            <span class="store-info__hours">{{ storesStore.selectedStore.working_hours }}</span>
          </div>
        </div>

        <div class="store-photos">
          <PhotoGallery
            :photos="storesStore.selectedStore.photos"
            :gridThreshold="1"
            :alt="`Магазин: ${storesStore.selectedStore.adress}`"
          />
        </div>
      </template>
    </section>
  </div>
</template>

<style scoped>
.stores-view {
  background: var(--color-main-bg);
  color: var(--color-main-text);
  font-family: var(--font-family-base);
}

/* ---------- Hero ---------- */

.hero {
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: linear-gradient(160deg, var(--color-header-footer-bg), #1a1a1a);
}

.hero__content {
  max-width: 700px;
  padding: 0 20px;
}

.hero__label {
  color: var(--color-header-footer-accent);
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 16px;
}

.hero h1 {
  color: white;
  font-size: 44px;
  line-height: 1.15;
  margin-bottom: 16px;
}

.hero__text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 17px;
}

/* ---------- Stores ---------- */

.stores {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px 90px;
}

.stores__status {
  text-align: center;
}

.city-tabs {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 14px;
  margin-bottom: 48px;
}

.stores-layout {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 30px;
  align-items: stretch;
}

.store-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: white;
  border-radius: 18px;
  padding: 16px;
  max-height: 420px;
  overflow-y: auto;
}

.store-list__item {
  color: #222;
}

.store-map {
  min-height: 420px;
}

.store-info {
  background: white;
  border-radius: 18px;
  padding: 32px;
  margin-top: 30px;
}

.store-info h3 {
  font-size: 20px;
  margin-bottom: 14px;
}

.store-info__row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
}

.store-info__link {
  color: var(--color-main-accent);
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
}

.store-info__link:hover {
  text-decoration: underline;
}

.store-info__hours {
  color: #555;
  font-size: 15px;
}

.store-photos {
  margin-top: 30px;
}

/* ---------- Адаптив ---------- */

@media (max-width: 900px) {
  .stores-layout {
    grid-template-columns: 1fr;
  }

  .store-list {
    max-height: 260px;
  }

  .store-map {
    min-height: 320px;
  }

  .hero h1 {
    font-size: 32px;
  }
}
</style>