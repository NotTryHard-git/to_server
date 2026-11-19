<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useCatalogStore } from '@/stores/catalog'
import BaseButton from '@/components/ui/BaseButton.vue'
import ProductCard from '@/components/ui/ProductCard.vue'

const route = useRoute()
const router = useRouter()
const catalogStore = useCatalogStore()

const selectedCategory = computed(() =>
  catalogStore.categories.find((category) => category.id === catalogStore.selectedCategoryId)
)

function findCategoryNode(nodes, id) {
  for (const node of nodes || []) {
    if (node.id === id) return node
    const found = findCategoryNode(node.children, id)
    if (found) return found
  }
  return null
}

// Ищем на любой глубине: выбранной может быть как подкатегория 2-го уровня,
// так и вложенный пункт 3-го уровня — у обоих теперь настоящий id.
const selectedSubcategoryObj = computed(() =>
  findCategoryNode(selectedCategory.value?.children, catalogStore.selectedSubcategoryId)
)

function applyFiltersFromQuery() {
  const { category, sub, search, page } = route.query
  const targetPage = Number(page) > 0 ? Number(page) : 1

  catalogStore.setFilters({
    categoryId: category || null,
    subcategoryId: sub || null,
    search: search || null,
    page: targetPage,
  })
}

function goToPage(newPage) {
  router.push({ query: { ...route.query, page: newPage } })
}

onMounted(async () => {
  await catalogStore.fetchCatalog()
  applyFiltersFromQuery()
})

watch(() => route.query, applyFiltersFromQuery)
</script>

<template>
  <div class="catalog-view">
    <section class="hero">
      <div class="hero__content">
        <template v-if="catalogStore.selectedSearch">
          <p class="hero__label">Результаты поиска</p>
          <h1>«{{ catalogStore.selectedSearch }}»</h1>
        </template>
        <template v-else>
          <p class="hero__label">Каталог</p>
          <h1>Вся косметика Ellips</h1>
        </template>
      </div>
    </section>

    <section class="catalog">
      <aside class="catalog-sidebar">
        <template v-if="!selectedCategory">
          <p class="catalog-sidebar__title">Категории</p>

          <BaseButton
            color="pink"
            shape="block"
            variant="ghost"
            active
          >
            Все категории
          </BaseButton>

          <BaseButton
            v-for="category in catalogStore.categories"
            :key="category.id"
            color="pink"
            shape="block"
            variant="ghost"
            @click="catalogStore.setCategory(category.id)"
          >
            {{ category.name }}
          </BaseButton>
        </template>

        <template v-else-if="!selectedSubcategoryObj">
          <button type="button" class="catalog-sidebar__back" @click="catalogStore.clearFilters()">
            ← Все категории
          </button>

          <h2 class="catalog-sidebar__heading">{{ selectedCategory.name }}</h2>

          <div class="catalog-sidebar__subcategories">
            <BaseButton
              color="pink"
              shape="block"
              variant="ghost"
              size="sm"
              :active="!catalogStore.selectedSubcategoryId"
              @click="catalogStore.setCategory(selectedCategory.id)"
            >
              Все товары категории
            </BaseButton>

            <BaseButton
              v-for="subcategory in selectedCategory.children"
              :key="subcategory.id"
              color="pink"
              shape="block"
              variant="ghost"
              size="sm"
              @click="catalogStore.setSubcategory(selectedCategory.id, subcategory.id)"
            >
              {{ subcategory.name }}
            </BaseButton>
          </div>
        </template>

        <template v-else>
          <button
            type="button"
            class="catalog-sidebar__back"
            @click="catalogStore.setCategory(selectedCategory.id)"
          >
            ← {{ selectedCategory.name }}
          </button>

          <h2 class="catalog-sidebar__heading">{{ selectedSubcategoryObj.name }}</h2>

          <div class="catalog-sidebar__subcategories">
            <BaseButton color="pink" shape="block" variant="ghost" size="sm" active>
              Все товары подкатегории
            </BaseButton>

            <BaseButton
              v-for="item in selectedSubcategoryObj.children"
              :key="item.id"
              color="pink"
              shape="block"
              variant="ghost"
              size="sm"
              @click="catalogStore.setSubcategory(selectedCategory.id, item.id)"
            >
              {{ item.name }}
            </BaseButton>
          </div>
        </template>
      </aside>

      <div class="catalog-products">
        <p v-if="catalogStore.isLoading" class="catalog-products__status">Загрузка...</p>

        <p v-else-if="!catalogStore.filteredProducts.length" class="catalog-products__status">
          В этой категории пока нет товаров.
        </p>

        <div v-else class="catalog-products__grid">
          <ProductCard
            v-for="product in catalogStore.filteredProducts"
            :key="product.id"
            :id="product.id"
            :name="product.name"
            :price="product.price"
            :image="product.image"
          />
        </div>

        <div v-if="catalogStore.totalPages > 1" class="catalog-pagination">
          <BaseButton
            color="pink"
            shape="pill"
            variant="outline"
            size="sm"
            :disabled="catalogStore.page <= 1"
            @click="goToPage(catalogStore.page - 1)"
          >
            ← Назад
          </BaseButton>

          <span class="catalog-pagination__info">
            Страница {{ catalogStore.page }} из {{ catalogStore.totalPages }}
          </span>

          <BaseButton
            color="pink"
            shape="pill"
            variant="outline"
            size="sm"
            :disabled="catalogStore.page >= catalogStore.totalPages"
            @click="goToPage(catalogStore.page + 1)"
          >
            Вперёд →
          </BaseButton>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.catalog-view {
  background: var(--color-main-bg);
  color: var(--color-main-text);
  font-family: var(--font-family-base);
}

.hero {
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: linear-gradient(160deg, var(--color-header-footer-bg), #1a1a1a);
}

.hero__label {
  color: var(--color-header-footer-accent);
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.hero h1 {
  color: white;
  font-size: 38px;
}

.catalog {
  max-width: 1600px;
  margin: 0 auto;
  padding: 60px 20px 90px;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 32px;
  align-items: start;
}

.catalog-sidebar {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: white;
  color: #222;
  border-radius: 18px;
  padding: 16px;
  top: calc(var(--header-height) + 20px);
  align-self: start;
  max-height: calc(100vh - var(--header-height) - 40px);
  overflow-y: auto;
}

.catalog-sidebar__title {
  margin: 4px 0 8px;
  padding: 0 20px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-main-accent);
}

.catalog-sidebar__back {
  align-self: flex-start;
  background: none;
  border: none;
  padding: 0 20px;
  margin-bottom: 12px;
  font-family: inherit;
  font-size: 14px;
  color: #888;
  cursor: pointer;
  transition: color 0.25s ease;
}

.catalog-sidebar__back:hover {
  color: var(--color-main-accent);
}

.catalog-sidebar__heading {
  padding: 0 20px;
  margin: 0 0 16px;
  font-size: 22px;
  line-height: 1.2;
}

.catalog-sidebar__subcategories {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 8px;
}

.catalog-products__status {
  text-align: center;
  padding: 40px 0;
}

.catalog-products__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.catalog-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.catalog-pagination__info {
  font-size: 14px;
  color: #777;
}

@media (min-width: 1500px) {
  .catalog-products__grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 900px) {
  .catalog {
    grid-template-columns: 1fr;
  }

  .catalog-sidebar {
    position: static;
    max-height: none;
  }

  .catalog-products__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 560px) {
  .catalog-products__grid {
    grid-template-columns: 1fr;
  }
}
</style>