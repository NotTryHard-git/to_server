<script setup>
import { useCityStore } from '@/stores/city'
import BaseButton from '@/components/ui/BaseButton.vue'

const cityStore = useCityStore()

function handleSelect(city) {
  cityStore.selectCity(city)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="cityStore.isModalOpen" class="city-modal-overlay">
      <div class="city-modal">
        <p class="city-modal__label">Добро пожаловать в e'llipse</p>
        <h2>Выберите ваш город</h2>
        <p class="city-modal__text">
          Так мы покажем актуальные адреса магазинов и наличие товаров рядом с вами.
        </p>

        <div class="city-modal__grid">
          <BaseButton
            v-for="city in cityStore.cities"
            :key="city"
            color="gold"
            variant="outline"
            shape="pill"
            size="md"
            @click="handleSelect(city)"
          >
            {{ city }}
          </BaseButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.city-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  padding: 20px;
}

.city-modal {
  width: 100%;
  max-width: 480px;
  background: var(--color-header-footer-bg);
  color: var(--color-header-footer-text);
  font-family: var(--font-family-base);
  border-radius: 18px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.city-modal__label {
  color: var(--color-header-footer-accent);
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-size: 13px;
  margin-bottom: 12px;
}

.city-modal h2 {
  font-size: 26px;
  margin-bottom: 12px;
}

.city-modal__text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin-bottom: 28px;
}

.city-modal__grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}
</style>