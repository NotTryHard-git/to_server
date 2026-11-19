<script setup>
import { ref } from 'vue'

import BaseButton from '@/components/ui/BaseButton.vue'

const STORAGE_KEY = 'ellips-cookie-consent'

const isVisible = ref(!localStorage.getItem(STORAGE_KEY))

function acceptCookies() {
  localStorage.setItem(STORAGE_KEY, 'accepted')
  isVisible.value = false
}
</script>

<template>
  <Teleport to="body">
    <div v-if="isVisible" class="cookie-consent">
      <p class="cookie-consent__text">
        Мы используем файлы cookie, чтобы сайт работал корректно и был удобнее для вас.
        Продолжая пользоваться сайтом, вы соглашаетесь с
        <!-- TODO: заменить на реальную страницу политики обработки данных, когда она появится -->
        <RouterLink to="/about">политикой обработки данных</RouterLink>.
      </p>

      <BaseButton color="accent" size="md" shape="pill" @click="acceptCookies">
        Принять
      </BaseButton>
    </div>
  </Teleport>
</template>

<style scoped>
.cookie-consent {
  position: fixed;
  left: 20px;
  right: 20px;
  bottom: 20px;
  z-index: 1500;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 20px;
  max-width: 900px;
  margin: 0 auto;
  background: var(--color-header-footer-bg);
  color: var(--color-header-footer-text);
  font-family: var(--font-family-base);
  border-radius: 14px;
  padding: 20px 28px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
}

.cookie-consent__text {
  flex: 1;
  min-width: 240px;
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.85);
}

.cookie-consent__text a {
  color: var(--color-header-footer-accent);
}
</style>