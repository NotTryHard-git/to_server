<script setup>
const model = defineModel({ type: String, default: '' })

defineProps({
  color: {
    type: String,
    default: 'black', // black | gold | pink
  },
  size: {
    type: String,
    default: 'md', // sm | md | lg
  },
  placeholder: {
    type: String,
    default: 'Введите значение',
  },
})
</script>

<template>
  <input
    v-model="model"
    class="base-input"
    :class="[`base-input--${color}`, `base-input--${size}`]"
    :placeholder="placeholder"
  />
</template>

<style scoped>
.base-input {
  width: 100%;
  border-radius: 4px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s ease;
}

/* Colors */
.base-input--black {
  background-color: var(--color-header-footer-bg);
  color: var(--color-header-footer-text);
  border: 1px solid var(--color-header-footer-accent);
}

.base-input--black::placeholder {
  color: var(--color-header-footer-text);
  opacity: 0.6;
}

.base-input--gold {
  background-color: transparent;
  color: var(--color-header-footer-text);
  border: 1px solid var(--color-header-footer-accent);
}

.base-input--gold::placeholder {
  color: var(--color-header-footer-accent);
  opacity: 0.7;
}

.base-input--pink {
  background-color: var(--color-main-bg);
  color: var(--color-main-text);
  border: 1px solid var(--color-main-accent);
}

.base-input--pink::placeholder {
  color: var(--color-main-text);
  opacity: 0.5;
}

/* Sizes */
.base-input--sm {
  padding: 6px 10px;
  font-size: 14px;
}

.base-input--md {
  padding: 10px 14px;
  font-size: 16px;
}

.base-input--lg {
  padding: 14px 18px;
  font-size: 18px;
}
</style>
