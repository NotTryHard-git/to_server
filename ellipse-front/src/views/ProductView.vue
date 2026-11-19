<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

import { useCatalogStore } from '@/stores/catalog'
import BaseButton from '@/components/ui/BaseButton.vue'

const route = useRoute()
const catalogStore = useCatalogStore()

const product = ref(null)
const isLoading = ref(false)
const notFound = ref(false)

async function loadProduct(id) {
  isLoading.value = true
  notFound.value = false
  product.value = null
  try {
    product.value = await catalogStore.fetchProductById(id)
  } catch {
    notFound.value = true
  } finally {
    isLoading.value = false
  }
}

onMounted(() => loadProduct(route.params.id))
watch(() => route.params.id, (id) => loadProduct(id))

const galleryImages = computed(() => product.value?.images || [])
const mainImage = computed(() => galleryImages.value[0] || null)

// Минимальная цена среди магазинов, где цена вообще заведена — используется
// как ориентир в заголовке ("от X ₽"). Если цену нигде не завели — не показываем.
const minPrice = computed(() => {
  const prices = (product.value?.storePrices || [])
    .map((sp) => sp.price)
    .filter((price) => price != null)
  return prices.length ? Math.min(...prices) : null
})

const characteristics = computed(() => {
  if (!product.value) return []

  return [
    { label: 'Бренд', value: product.value.brand?.name },
    { label: 'Категория', value: product.value.category?.name },
    { label: 'Артикул', value: product.value.barcode },
  ].filter((item) => item.value)
})

// TODO: подставить реальный состав, когда появится у backend/поставщика
const composition = computed(
  () => product.value?.composition || 'Полный состав уточняйте у консультанта в магазине или на упаковке товара.'
)

// TODO: подключить реальные отзывы, когда появится функциональность
const reviews = computed(() => product.value?.reviews || [])

const tabs = [
  { id: 'description', label: 'Описание' },
  { id: 'characteristics', label: 'Характеристики' },
  { id: 'stores', label: 'Наличие и цены' },
  { id: 'composition', label: 'Состав' },
  { id: 'reviews', label: 'Отзывы' },
]

const activeTab = ref('description')
</script>

<template>
  <div class="product-view">
    <template v-if="isLoading">
      <p class="product-view__status">Загрузка...</p>
    </template>

    <template v-else-if="notFound || !product">
      <div class="product-view__status">
        <p>Товар не найден.</p>
        <RouterLink to="/catalog" class="product-view__back-link">← Вернуться в каталог</RouterLink>
      </div>
    </template>

    <template v-else>
      <div class="breadcrumbs">
        <RouterLink to="/catalog">Каталог</RouterLink>

        <template v-for="crumb in product.categoryPath" :key="crumb.id">
          <span> / </span>
          <RouterLink :to="{ path: '/catalog', query: { category: crumb.id } }">
            {{ crumb.name }}
          </RouterLink>
        </template>

        <span> / </span>
        <span class="breadcrumbs__current">{{ product.name }}</span>
      </div>

      <section class="product">
        <div class="product__gallery">
          <img v-if="mainImage" :src="mainImage" :alt="product.name" class="product__image" />
          <div v-else class="product__gallery-placeholder" />
        </div>

        <div class="product__info">
          <p v-if="product.brand" class="product__brand">{{ product.brand.name }}</p>
          <h1>{{ product.name }}</h1>

          <p v-if="minPrice != null" class="product__price">от {{ minPrice }} ₽</p>
          <p v-else class="product__price product__price--unknown">Узнать цену и количество</p>

          <div class="product__actions">
            <!-- TODO: подключить реальное добавление в корзину, когда появится функциональность -->
            <BaseButton color="accent" size="lg" shape="pill">В корзину</BaseButton>

            <!-- TODO: подключить реальное избранное, когда появится функциональность -->
            <BaseButton color="pink" size="lg" shape="pill" variant="outline">В избранное</BaseButton>
          </div>
        </div>
      </section>

      <section class="product-tabs">
        <div class="product-tabs__nav">
          <BaseButton
            v-for="tab in tabs"
            :key="tab.id"
            :color="tab.id === activeTab ? 'accent' : 'pink'"
            shape="pill"
            size="md"
            :variant="tab.id === activeTab ? 'solid' : 'outline'"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </BaseButton>
        </div>

        <div class="product-tabs__content">
          <p v-if="activeTab === 'description'">{{ product.description }}</p>

          <table v-else-if="activeTab === 'characteristics'" class="product-tabs__table">
            <tbody>
              <tr v-for="item in characteristics" :key="item.label">
                <th>{{ item.label }}</th>
                <td>{{ item.value }}</td>
              </tr>
            </tbody>
          </table>

          <p v-else-if="activeTab === 'composition'">{{ composition }}</p>

          <template v-else-if="activeTab === 'stores'">
            <table v-if="product.storePrices.length" class="product-tabs__table product-tabs__table--stores">
              <thead>
                <tr>
                  <th>Магазин</th>
                  <th>Цена</th>
                  <th>Количество</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in product.storePrices" :key="row.storeId">
                  <td>{{ row.storeName }}</td>
                  <td>{{ row.price != null ? `${row.price} ₽` : 'Уточняйте' }}</td>
                  <td>{{ row.quantity }} шт.</td>
                </tr>
              </tbody>
            </table>

            <p v-else class="product-tabs__empty">
              Сейчас этого товара нет в наличии ни в одном магазине.
            </p>
          </template>

          <template v-else-if="activeTab === 'reviews'">
            <p v-if="!reviews.length" class="product-tabs__empty">
              Отзывов пока нет. Будьте первым, кто оставит отзыв об этом товаре.
            </p>

            <div v-else class="product-tabs__reviews">
              <div v-for="(review, index) in reviews" :key="index" class="review-card">
                <p class="review-card__author">{{ review.author }}</p>
                <p class="review-card__text">{{ review.text }}</p>
              </div>
            </div>
          </template>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.product-view {
  background: var(--color-main-bg);
  color: var(--color-main-text);
  font-family: var(--font-family-base);
  min-height: 60vh;
  padding: 40px 20px 90px;
}

.product-view__status {
  max-width: 600px;
  margin: 0 auto;
  padding: 80px 0;
  text-align: center;
}

.product-view__back-link {
  display: inline-block;
  margin-top: 16px;
  color: var(--color-main-accent);
  text-decoration: none;
}

.breadcrumbs {
  max-width: 1200px;
  margin: 0 auto 30px;
  font-size: 14px;
  color: #777;
}

.breadcrumbs a {
  color: #777;
  text-decoration: none;
}

.breadcrumbs a:hover {
  color: var(--color-main-accent);
}

.breadcrumbs__current {
  color: var(--color-main-text);
}

.product {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
  align-items: start;
}

.product__gallery-placeholder {
  width: 100%;
  height: 480px;
  border-radius: 18px;
  background-color: var(--color-main-accent);
  opacity: 0.35;
}


.product__gallery { 
  padding: 16px; 
  border: 1px solid #e5e5e5;
  border-radius: 20px; 
  background: #fff; 
  height: 480px;
  display: flex;
  justify-content: center;
} 
.product__image { 
  display: block; 
  width: auto; 
  border-radius: 12px; 
  max-height: 460px;
}


.product__brand {
  color: var(--color-main-accent);
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-size: 13px;
  margin-bottom: 8px;
}

.product__info h1 {
  font-size: 30px;
  line-height: 1.2;
  margin-bottom: 8px;
}

.product__price {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
}

.product__price--unknown {
  font-size: 20px;
  color: #777;
}

.product__description {
  font-size: 16px;
  line-height: 1.7;
  margin-bottom: 32px;
}

.product__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.product-tabs {
  max-width: 1200px;
  margin: 60px auto 0;
}

.product-tabs__nav {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 28px;
}

.product-tabs__content {
  background: white;
  border-radius: 18px;
  padding: 32px;
  font-size: 16px;
  line-height: 1.7;
}

.product-tabs__table {
  width: 100%;
  border-collapse: collapse;
}

.product-tabs__table th,
.product-tabs__table td {
  text-align: left;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  font-weight: 400;
}

.product-tabs__table th {
  color: #777;
  width: 220px;
}

.product-tabs__table--stores thead th {
  width: auto;
  color: var(--color-main-text);
  font-weight: 600;
  border-bottom: 2px solid rgba(0, 0, 0, 0.12);
}

.product-tabs__empty {
  color: #777;
}

.product-tabs__reviews {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-card {
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  padding-bottom: 20px;
}

.review-card:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.review-card__author {
  font-weight: 600;
  margin-bottom: 6px;
}

.review-card__text {
  margin: 0;
  color: #444;
}

@media (max-width: 800px) {
  .product {
    grid-template-columns: 1fr;
  }
}
</style>