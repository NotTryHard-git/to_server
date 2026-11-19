<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const query = ref(route.query.search || '')

// Синхронизация с URL — если поиск сбросили/поменяли откуда-то ещё
// (например, кнопкой "Все категории" в каталоге), поле тоже обновится.
watch(
  () => route.query.search,
  (value) => {
    query.value = value || ''
  }
)

function submitSearch() {
  const trimmed = query.value.trim()
  if (!trimmed) return

  // Новый поиск — это всегда свежая выдача каталога, поэтому не тащим
  // за собой старые category/sub/page из текущего URL.
  router.push({ path: '/catalog', query: { search: trimmed } })
}
</script>

<template>
  <form class="header-search" @submit.prevent="submitSearch">
    <button type="submit" class="header-search__submit" aria-label="Искать">
      <svg
        class="header-search__icon"
        viewBox="0 0 24 24"
        width="18"
        height="18"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.5-3.5" />
      </svg>
    </button>

    <input
      v-model="query"
      type="text"
      placeholder="Поиск косметики..."
      class="header-search__input"
    />
  </form>
</template>

<style scoped>
.header-search {
  min-width: 0;
  flex: 1;
  width: 100%;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #fff;
  border: 1.5px solid var(--color-header-footer-accent);
  border-radius: 12px;
  padding: 10px 16px;
  transition: box-shadow 0.25s ease, border-color 0.25s ease;
}

.header-search:focus-within {
  border-color: var(--color-header-footer-accent);
  box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.2);
}

.header-search__submit {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: var(--color-header-footer-accent);
}

.header-search__input {
  min-width: 0;
  width: 100%;
  flex: 1;
  border: none;
  outline: none;
  font-family: inherit;
  font-size: 15px;
  color: #1a1a1a;
  background: transparent;
}

.header-search__input::placeholder {
  color: #9a9a9a;
}

@media (max-width: 480px) {
  .header-search {
    padding: 9px 12px;
  }

  .header-search__input {
    font-size: 14px;
  }
}
</style>