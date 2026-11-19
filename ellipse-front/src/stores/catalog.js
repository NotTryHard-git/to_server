import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiFetch } from '@/api/client'

// Категории — общий реактивный источник, доступный и как именованный экспорт
// (для мест, где раньше импортировали статический массив напрямую), и как
// состояние стора. Заполняется после вызова fetchCatalog()/fetchCategories().
// Форма — как отдаёт backend: { id, name, children: [...] } рекурсивно,
// на любую глубину, с реальным id на каждом уровне.
export const categories = ref([])

const PAGE_SIZE = 20

function mapProductListItem(item) {
  return {
    id: item.id,
    name: item.name,
    image: item.image,
    brand: item.brand,
    isHit: item.is_hit,
    // Цены здесь больше нет: она теперь за магазином, а не за товаром.
    // На карточке в каталоге фронт показывает фразу "Узнать цену и количество".
  }
}

function mapProductDetail(item) {
  return {
    id: item.id,
    name: item.name,
    description: item.description,
    barcode: item.barcode,
    brand: item.brand, // { id, name } | null — как отдаёт backend
    category: item.category, // { id, name } | null
    categoryPath: item.category_path || [], // [{ id, name }] от корня к текущей категории
    // Раньше здесь были отдельные price/availability — теперь у каждого
    // магазина своя цена, поэтому backend отдаёт единую таблицу store_prices
    storePrices: (item.store_prices || []).map((sp) => ({
      storeId: sp.store_id,
      storeName: sp.store_name,
      price: sp.price,
      currency: sp.currency,
      quantity: sp.quantity,
    })),
    images: item.images,
    promotions: item.promotions,
  }
}

export const useCatalogStore = defineStore('catalog', () => {
  const products = ref([])
  const isLoading = ref(false)
  // Раньше здесь хранилось название подкатегории (строка). Теперь это id
  // категории/подкатегории из дерева backend, так как товары в БД привязаны
  // к category_id, а не к текстовому названию.
  const selectedCategoryId = ref(null)
  const selectedSubcategoryId = ref(null)
  const selectedSearch = ref(null)

  // Пагинация — раньше вообще не хранилась: fetchProducts всегда слал limit=100
  // и отбрасывал page/pages/total из ответа backend, поэтому листать было нечем.
  const page = ref(1)
  const totalPages = ref(1)
  const total = ref(0)

  // Фильтрация теперь выполняется backend'ом (через query-параметр category_id),
  // поэтому просто отдаём то, что пришло с сервера.
  const filteredProducts = computed(() => products.value)

  async function fetchProducts() {
    isLoading.value = true
    try {
      const categoryId = selectedSubcategoryId.value || selectedCategoryId.value
      const params = new URLSearchParams({
        limit: String(PAGE_SIZE),
        page: String(page.value),
      })
      if (categoryId) params.set('category_id', categoryId)
      if (selectedSearch.value) params.set('search', selectedSearch.value)

      const data = await apiFetch(`/api/products?${params.toString()}`)
      products.value = data.items.map(mapProductListItem)
      page.value = data.page
      totalPages.value = data.pages
      total.value = data.total
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCategories() {
    const data = await apiFetch('/api/products/categories')
    categories.value = data
  }

  async function fetchCatalog() {
    isLoading.value = true
    try {
      await Promise.all([fetchCategories(), fetchProducts()])
    } finally {
      isLoading.value = false
    }
  }

  // Единая точка применения фильтров + страницы — чтобы не забыть сбросить
  // страницу на 1-ю при смене категории (иначе можно застрять на "странице 5",
  // когда в новой категории всего 1 страница товаров, и получить пустой список).
  function setFilters({
    categoryId = null,
    subcategoryId = null,
    search = null,
    page: targetPage = 1,
  } = {}) {
    selectedCategoryId.value = categoryId
    selectedSubcategoryId.value = subcategoryId
    selectedSearch.value = search
    page.value = targetPage
    fetchProducts()
  }

  function setCategory(categoryId) {
    setFilters({ categoryId, page: 1 })
  }

  // Второй аргумент теперь id подкатегории (не название)
  function setSubcategory(categoryId, subcategoryId) {
    setFilters({ categoryId, subcategoryId, page: 1 })
  }

  // Текстовый поиск — глобальный, сбрасывает выбранную категорию/подкатегорию
  function setSearch(search) {
    setFilters({ search, page: 1 })
  }

  function clearFilters() {
    setFilters({ page: 1 })
  }

  function setPage(newPage) {
    setFilters({
      categoryId: selectedCategoryId.value,
      subcategoryId: selectedSubcategoryId.value,
      search: selectedSearch.value,
      page: newPage,
    })
  }

  // Синхронный поиск по уже загруженному списку (для карточек в каталоге).
  // Для полной информации о товаре (описание, остатки, акции) используйте
  // fetchProductById.
  function getProductById(id) {
    return products.value.find((product) => String(product.id) === String(id)) || null
  }

  async function fetchProductById(id) {
    const data = await apiFetch(`/api/products/${id}`)
    return mapProductDetail(data)
  }

  return {
    categories,
    products,
    isLoading,
    selectedCategoryId,
    selectedSubcategoryId,
    selectedSearch,
    page,
    totalPages,
    total,
    filteredProducts,
    setCategory,
    setSubcategory,
    setSearch,
    setFilters,
    setPage,
    clearFilters,
    getProductById,
    fetchProductById,
    fetchCategories,
    fetchCatalog,
  }
})