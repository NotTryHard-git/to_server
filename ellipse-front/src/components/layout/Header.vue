<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'

import logo from '@/assets/images/eng_logo.png'
import AppNav from '@/components/layout/AppNav.vue'
import MegaMenu from '@/components/layout/MegaMenu.vue'
import HeaderSearch from '@/components/layout/HeaderSearch.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import CitySelect from '@/components/ui/CitySelect.vue'

const route = useRoute()

const isMegaMenuOpen = ref(false)
const isMobile = ref(false)

const catalogButtonRef = ref(null)
const megaMenuRef = ref(null)

let mediaQuery = null

function updateMobileState() {
  isMobile.value = mediaQuery.matches
}

function toggleMegaMenu() {
  isMegaMenuOpen.value = !isMegaMenuOpen.value
}

function closeMegaMenu() {
  isMegaMenuOpen.value = false
}

watch(
  () => route.fullPath,
  () => closeMegaMenu()
)

function handleOutsideClick(event) {
  if (!isMegaMenuOpen.value) return

  const clickedCatalogButton =
    catalogButtonRef.value?.$el?.contains(event.target)

  const clickedInsideMenu =
    megaMenuRef.value?.contains(event.target)

  if (!clickedCatalogButton && !clickedInsideMenu) {
    closeMegaMenu()
  }
}

onMounted(() => {
  mediaQuery = window.matchMedia('(max-width: 768px)')

  updateMobileState()
  mediaQuery.addEventListener('change', updateMobileState)

  document.addEventListener('click', handleOutsideClick)
})

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener('change', updateMobileState)
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<template>
  <header class="app-header">
    <div class="app-header__top">
      <div class="app-header__top-side">
        <CitySelect />
      </div>

      <RouterLink to="/" class="app-header__logo">
        <img :src="logo" alt="e'llipse" width="170" height="68" />
      </RouterLink>

      <div class="app-header__top-side" />
    </div>

    <div class="app-header__main">
      <BaseButton
        ref="catalogButtonRef"
        color="gold"
        size="md"
        shape="pill"
        class="app-header__catalog"
        @click="toggleMegaMenu"
      >
        <span class="app-header__catalog-icon">☰</span>
        Каталог
        <span class="app-header__catalog-arrow">▾</span>
      </BaseButton>

      <HeaderSearch />

      <div class="app-header__actions">
        <!-- TODO: ссылка на личный кабинет, когда появится авторизация -->
        <BaseButton color="gold" size="md" shape="circle" variant="outline" aria-label="Личный кабинет">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8">
            <circle cx="12" cy="8" r="4" />
            <path d="M4 20c0-4.4 3.6-7 8-7s8 2.6 8 7" />
          </svg>
        </BaseButton>

        <!-- TODO: ссылка на избранное, когда появится функциональность -->
        <BaseButton color="gold" size="md" shape="circle" variant="outline" aria-label="Избранное">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M12 20s-7-4.4-9.5-9C.8 7.4 3 4 6.5 4 9 4 11 6 12 7c1-1 3-3 5.5-3C21 4 23.2 7.4 21.5 11 19 15.6 12 20 12 20z" />
          </svg>
        </BaseButton>

        <!-- TODO: ссылка на корзину, когда появится функциональность -->
        <BaseButton color="gold" size="md" shape="circle" variant="outline" aria-label="Корзина">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M3 4h2l2.2 11.4a2 2 0 0 0 2 1.6h7.6a2 2 0 0 0 2-1.6L21 8H6" />
            <circle cx="9" cy="20" r="1.4" fill="currentColor" stroke="none" />
            <circle cx="18" cy="20" r="1.4" fill="currentColor" stroke="none" />
          </svg>
        </BaseButton>
      </div>
    </div>

    <div class="app-header__nav-row">
      <AppNav :direction="isMobile ? 'column' : 'row'" />
    </div>

      <div v-if="isMegaMenuOpen" ref="megaMenuRef">
        <MegaMenu class="app-header__mega-menu" />
      </div>
  </header>
</template>

<style scoped>
.app-header {
  position: relative;
  top: 0;
  z-index: 1000;
  background-color: var(--color-header-footer-bg-glass);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  color: var(--color-header-footer-text);
  font-family: var(--font-family-base);
  box-sizing: border-box;
  padding: 14px 38px;
}

.app-header__top {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 16px;
}

.app-header__top-side {
  display: flex;
  align-items: center;
}

.app-header__logo {
  display: flex;
  opacity: 0.85;
  transition: opacity 0.25s ease;
}

.app-header__logo img {
  mix-blend-mode: screen;
  display: block;
  max-width: 100%;
  height: auto;
}

.app-header__logo:hover {
  opacity: 1;
}

.app-header__main {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 14px;
}

.app-header__catalog {
  flex-shrink: 0;
}

.app-header__catalog-icon {
  font-size: 15px;
}

.app-header__catalog-arrow {
  font-size: 12px;
}

.app-header__actions {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.app-header__nav-row {
  display: flex;
  justify-content: center;
  margin-top: 14px;
}

.app-header__mega-menu {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  z-index: 20;
  box-sizing: border-box;
}


/* =========================
   TABLET
   ========================= */

@media (max-width: 1000px) {
  .app-header {
    padding: 14px 24px;
  }

  .app-header__main {
    gap: 14px;
  }

  .app-header__actions {
    gap: 8px;
  }

  .app-header__logo img {
    width: 140px;
    height: auto;
  }
}


/* =========================
   MOBILE
   ========================= */

@media (max-width: 768px) {
  .app-header {
    padding: 12px 16px;
  }

  .app-header__top {
    grid-template-columns: 1fr;
    justify-items: center;
    gap: 10px;
  }

  .app-header__top-side {
    width: 100%;
    justify-content: center;
  }

  .app-header__top-side:last-child {
    display: none;
  }

  .app-header__logo img {
    width: 150px;
    height: auto;
  }

  .app-header__main {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    margin-top: 16px;
  }

  .app-header__catalog {
    width: 100%;
  }

  .app-header__actions {
    justify-content: center;
    width: 100%;
  }

  .app-header__nav-row {
    margin-top: 16px;
    width: 100%;
  }

  .app-header__mega-menu {
    width: 100%;
  }
}


/* =========================
   SMALL MOBILE
   ========================= */

@media (max-width: 480px) {
  .app-header {
    padding: 10px 12px;
  }

  .app-header__logo img {
    width: 130px;
  }

  .app-header__actions {
    gap: 10px;
  }
}
</style>