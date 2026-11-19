<script setup>
import { computed } from 'vue'

const props = defineProps({
  // button | a | router-link — что рендерить
  tag: {
    type: String,
    default: 'button',
  },
  to: {
    type: [String, Object],
    default: null,
  },
  href: {
    type: String,
    default: null,
  },
  type: {
    type: String,
    default: 'button',
  },
  color: {
    type: String,
    default: 'black', // black | gold | pink | accent
  },
  size: {
    type: String,
    default: 'md', // sm | md | lg
  },
  shape: {
    type: String,
    default: 'default', // default | pill | circle | block
  },
  variant: {
    type: String,
    default: 'solid', // solid | outline | ghost
  },
  // используется с variant="ghost" для табов/списков (например, категории MegaMenu)
  active: {
    type: Boolean,
    default: false,
  },
})

const componentTag = computed(() => {
  if (props.tag === 'router-link') return 'RouterLink'
  return props.tag
})

const tagAttrs = computed(() => {
  if (props.tag === 'a') return { href: props.href }
  if (props.tag === 'router-link') return { to: props.to }
  return { type: props.type }
})
</script>

<template>
  <component
    :is="componentTag"
    v-bind="tagAttrs"
    class="base-button"
    :class="[
      `base-button--${color}`,
      `base-button--${size}`,
      `base-button--shape-${shape}`,
      `base-button--variant-${variant}`,
      { 'base-button--active': active },
    ]"
  >
    <slot />
  </component>
</template>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: none;
  cursor: pointer;
  font-family: inherit;
  text-decoration: none;
  transition: color 0.25s ease, background-color 0.25s ease, border-color 0.25s ease,
    transform 0.25s ease, opacity 0.25s ease;
}

.base-button:hover {
  opacity: 0.9;
}

.base-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none !important;
}

/* ---------- Размеры ---------- */

.base-button--sm {
  padding: 6px 12px;
  font-size: 14px;
}

.base-button--md {
  padding: 10px 20px;
  font-size: 16px;
}

.base-button--lg {
  padding: 14px 28px;
  font-size: 18px;
}

/* ---------- Формы ---------- */

.base-button--shape-default {
  border-radius: 4px;
}

.base-button--shape-pill {
  border-radius: 999px;
}

.base-button--shape-block {
  width: 100%;
  justify-content: flex-start;
  text-align: left;
  border-radius: 10px;
}

.base-button--shape-circle {
  padding: 0;
  border-radius: 50%;
  flex-shrink: 0;
}

.base-button--shape-circle.base-button--sm {
  width: 32px;
  height: 32px;
}

.base-button--shape-circle.base-button--md {
  width: 40px;
  height: 40px;
}

.base-button--shape-circle.base-button--lg {
  width: 48px;
  height: 48px;
}

/* ---------- solid: чёрный/золотой/розовый/акцентный фон ---------- */

.base-button--variant-solid.base-button--black {
  background-color: var(--color-header-footer-bg);
  color: var(--color-header-footer-text);
}

.base-button--variant-solid.base-button--gold {
  background-color: var(--color-header-footer-accent);
  color: var(--color-header-footer-bg);
  font-weight: 600;
}

.base-button--variant-solid.base-button--pink {
  background-color: var(--color-main-bg);
  color: var(--color-main-accent);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.base-button--variant-solid.base-button--pink:hover {
  color: var(--color-main-text);
}

.base-button--variant-solid.base-button--accent {
  background-color: var(--color-main-accent);
  color: #fff;
}

.base-button--variant-solid:not(.base-button--shape-circle):hover {
  transform: translateY(-2px);
}

/* ---------- outline: прозрачный фон, обводка, заливка на hover (иконки/соцсети/фильтры) ---------- */

.base-button--variant-outline {
  background: none;
}

.base-button--variant-outline:hover {
  transform: translateY(-2px) scale(1.03);
  opacity: 1;
}

.base-button--variant-outline.base-button--gold {
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--color-header-footer-text);
}

.base-button--variant-outline.base-button--gold:hover {
  background-color: var(--color-header-footer-accent);
  border-color: var(--color-header-footer-accent);
  color: var(--color-header-footer-bg);
}

.base-button--variant-outline.base-button--pink {
  border: 1px solid var(--color-main-accent);
  color: var(--color-main-accent);
}

.base-button--variant-outline.base-button--pink:hover {
  background-color: var(--color-main-accent);
  border-color: var(--color-main-accent);
  color: #fff;
}

/* ---------- ghost: список/табы (например, категории MegaMenu) ---------- */

.base-button--variant-ghost {
  background: none;
}

.base-button--variant-ghost:hover {
  background-color: color-mix(in srgb, currentColor 8%, transparent);
  opacity: 1;
}

.base-button--variant-ghost.base-button--active {
  background-color: var(--color-header-footer-accent);
  color: var(--color-header-footer-bg);
  font-weight: 600;
}
</style>