<script setup>
import { useCityStore } from '@/stores/city'

const cityStore = useCityStore()

function handleChange(event) {
  cityStore.selectCity(event.target.value)
}
</script>

<template>
  <div class="city-select">
    <select :value="cityStore.selectedCity" class="city-select__control" @change="handleChange">
      <option v-for="city in cityStore.cities" :key="city" :value="city">
        {{ city }}
      </option>
    </select>
    <span class="city-select__arrow">▾</span>
  </div>
</template>

<style scoped>
.city-select {
  position: relative;
  display: inline-flex;
}

.city-select__control {
  appearance: none;
  background-color: transparent;
  color: var(--color-header-footer-text);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 6px;
  padding: 6px 26px 6px 12px;
  font-family: inherit;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.25s ease, color 0.25s ease;
}

.city-select__control:hover,
.city-select__control:focus {
  border-color: var(--color-header-footer-accent);
  color: var(--color-header-footer-accent);
  outline: none;
}

.city-select__arrow {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  font-size: 11px;
  color: var(--color-header-footer-text);
  pointer-events: none;
  transition: color 0.25s ease;
}

.city-select:hover .city-select__arrow,
.city-select:focus-within .city-select__arrow {
  color: var(--color-header-footer-accent);
}
</style>