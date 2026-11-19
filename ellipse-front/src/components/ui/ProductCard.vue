<script setup>
defineProps({
  id: {
    type: [String, Number],
    required: true,
  },
  name: {
    type: String,
    required: true,
  },
  price: {
    type: [String, Number],
    required: true,
  },
  image: {
    type: String,
    default: '',
  },
})

// TODO: заменить путь, когда появится страница товара и роут /product/:id
</script>

<template>
  <RouterLink :to="`/product/${id}`" class="product-card">
    <img v-if="image" :src="image" :alt="name" class="product-card__image" />
    <div v-else class="product-card__image product-card__image--placeholder" />

    <p class="product-card__name">{{ name }}</p>
    <p class="product-card__price"> Узнать цену и количество ></p>
  </RouterLink>
</template>

<style scoped>
.product-card {
  display: flex;
  flex-direction: column;
  background-color: #fff;
  color: #222;
  border-radius: 18px;
  padding: 20px;
  text-decoration: none;
  font-family: var(--font-family-base);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.product-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
}

.product-card__image {
  width: auto;
  max-width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  object-fit: cover;
}

.product-card__image--placeholder {
  background-color: var(--color-main-accent);
}

.product-card__name {
  margin: 16px 0 4px;
  font-size: 15px;
}

.product-card__price {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}
</style>