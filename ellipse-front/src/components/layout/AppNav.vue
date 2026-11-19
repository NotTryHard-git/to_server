<script setup>
defineProps({
  direction: {
    type: String,
    default: 'row', // row | column
  },
})

const links = [
  { to: { name: 'home' }, label: 'Главная' },
  { to: { name: 'stores' }, label: 'Магазины' },
  { to: { name: 'promotions' }, label: 'Акции' },
  { to: { name: 'giftCards' }, label: 'Подарочные карты' },
  { to: { name: 'about' }, label: 'О компании' },
  { to: { name: 'contacts' }, label: 'Контакты' },
  { to: { name: 'career' }, label: 'Карьера' },
]
</script>

<template>
  <nav class="app-nav" :class="`app-nav--${direction}`">
    <RouterLink
      v-for="link in links"
      :key="link.label"
      :to="link.to"
      class="app-nav__link"
      active-class="app-nav__link--active"
    >
      {{ link.label }}
    </RouterLink>
  </nav>
</template>

<style scoped>
.app-nav {
  display: flex;
  align-items: center;
  gap: 28px;
}

.app-nav--column {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.app-nav__link {
  position: relative;
  color: var(--color-header-footer-text);
  text-decoration: none;
  font-size: 15px;
  padding-bottom: 4px;
}

.app-nav__link::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 0;
  height: 2px;
  background-color: var(--color-header-footer-accent);
  transition: width 0.25s ease;
}

.app-nav__link:hover::after,
.app-nav__link--active::after {
  width: 100%;
}
</style>
