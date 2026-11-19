<script setup>
import { onMounted, computed, ref } from 'vue'

import { useCatalogStore } from '@/stores/catalog'
import BaseButton from '@/components/ui/BaseButton.vue'

const catalogStore = useCatalogStore()

const activeCategoryId = ref(null)

onMounted(async () => {
  await catalogStore.fetchCategories()
  if (catalogStore.categories.length) {
    activeCategoryId.value = catalogStore.categories[0].id
  }
})

const activeCategory = computed(() =>
  catalogStore.categories.find((category) => category.id === activeCategoryId.value) || null
)

function setActiveCategory(id) {
  activeCategoryId.value = id
}
</script>

<template>
  <div class="mega-menu">
    <div class="mega-menu__categories">
      <BaseButton
        v-for="category in catalogStore.categories"
        :key="category.id"
        color="gold"
        shape="block"
        variant="ghost"
        :active="category.id === activeCategoryId"
        class="mega-menu__category"
        @mouseenter="setActiveCategory(category.id)"
        @focus="setActiveCategory(category.id)"
      >
        {{ category.name }}
      </BaseButton>

      <RouterLink to="/catalog" class="mega-menu__all-link">
        Все товары →
      </RouterLink>
    </div>

    <div v-if="activeCategory" class="mega-menu__subcategories">
      <RouterLink
        :to="{ path: '/catalog', query: { category: activeCategoryId } }"
        class="mega-menu__all-category-link"
      >
        Все товары категории
      </RouterLink>

      <div class="mega-menu__columns">
        <div v-for="subcategory in activeCategory.children" :key="subcategory.id" class="mega-menu__column">
          <RouterLink
            :to="{ path: '/catalog', query: { category: activeCategoryId, sub: subcategory.id } }"
            class="mega-menu__column-heading"
          >
            {{ subcategory.name }}
          </RouterLink>

          <RouterLink
            v-for="item in subcategory.children"
            :key="item.id"
            :to="{ path: '/catalog', query: { category: activeCategoryId, sub: item.id } }"
            class="mega-menu__column-item"
          >
            {{ item.name }}
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
.mega-menu {
  display: flex;
  width: 100%;
  max-height: calc(100vh - var(--header-height));
  background-color: var(--color-main-bg);
  color: var(--color-main-text);
  font-family: var(--font-family-base);
  border-radius: 0 0 18px 18px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  box-sizing: border-box;
}

.mega-menu__categories {
  position: relative;
  display: flex;
  flex-direction: column;
  width: 360px;
  flex-shrink: 0;
  padding: 24px 16px;
  gap: 4px;
  box-sizing: border-box;
}

.mega-menu__categories::after {
  content: '';
  position: absolute;
  top: 24px;
  bottom: 24px;
  right: 0;
  width: 1px;
  background-color: var(--color-main-accent);
  opacity: 0.3;
}

.mega-menu__category {
  font-size: 15px;
  flex-shrink: 0;
}

.mega-menu__all-link {
  margin-top: 12px;
  padding: 0 20px;
  color: var(--color-main-accent);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
}

.mega-menu__all-link:hover {
  text-decoration: underline;
}

.mega-menu__subcategories {
  min-width: 0;
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  box-sizing: border-box;
}

.mega-menu__all-category-link {
  display: inline-block;
  margin-bottom: 28px;
  color: var(--color-main-accent);
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
}

.mega-menu__all-category-link:hover {
  text-decoration: underline;
}

.mega-menu__columns {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 28px 32px;
}

.mega-menu__column {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mega-menu__column-heading {
  color: var(--color-main-text);
  text-decoration: none;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
  transition: color 0.25s ease;
}

.mega-menu__column-heading:hover {
  color: var(--color-main-accent);
}

.mega-menu__column-item {
  color: var(--color-main-text);
  text-decoration: none;
  font-size: 14px;
  opacity: 0.75;
  transition:
    color 0.25s ease,
    opacity 0.25s ease,
    transform 0.25s ease;
}

.mega-menu__column-item:hover {
  color: var(--color-main-accent);
  opacity: 1;
  transform: translateX(4px);
}


/* =========================
   TABLET
   ========================= */

@media (max-width: 1000px) {
  .mega-menu__categories {
    width: 280px;
    padding: 20px 12px;
  }

  .mega-menu__categories::after {
    top: 20px;
    bottom: 20px;
  }

  .mega-menu__subcategories {
    padding: 28px;
  }

  .mega-menu__columns {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 24px;
  }
}


/* =========================
   MOBILE
   ========================= */
@media (max-width: 768px) {
  .mega-menu {
    flex-direction: column;
    max-height: calc(100vh - var(--header-height));
    border-radius: 0 0 14px 14px;
    overflow-y: auto;
    text-align: center;
  }

  .mega-menu__categories {
    width: 100%;
    flex-shrink: 0;
    padding: 14px 12px;
    gap: 4px;

  }

  .mega-menu__categories::after {
    display: none;
  }

  .mega-menu__category {
    width: 100%;
    font-size: 14px;
    
    display: block;
    text-align: center;
  }

  .mega-menu__all-link {
    margin-top: 8px;
    padding: 6px 16px;
    font-size: 14px;
  }

  .mega-menu__subcategories {
    width: 100%;
    flex: none;
    padding: 20px 16px 24px;
    overflow-y: visible;
    border-top: 1px solid var(--color-main-accent);
    border-top-opacity: 0.2;
  }

  .mega-menu__all-category-link {
    margin-bottom: 20px;
    font-size: 14px;
    display: block;
  }

  .mega-menu__columns {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .mega-menu__column {
    gap: 8px;
    align-items: center;
  }

  .mega-menu__column-heading {
    font-size: 15px;
    margin-bottom: 3px;
  }

  .mega-menu__column-item {
    font-size: 14px;
  }

  .mega-menu__column-item:hover {
    transform: none;
  }
}


/* =========================
   SMALL MOBILE
   ========================= */

@media (max-width: 480px) {
  .mega-menu {
    max-height: calc(100vh - var(--header-height));
  }

  .mega-menu__categories {
    padding: 10px 8px;
  }

  .mega-menu__subcategories {
    padding: 16px 12px 20px;
  }

  .mega-menu__all-category-link {
    margin-bottom: 16px;
  }

  .mega-menu__columns {
    gap: 20px;
  }

  .mega-menu__column {
    gap: 7px;
  }
}
</style>