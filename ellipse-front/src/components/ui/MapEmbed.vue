<script>
// Модульный (не per-instance) кэш загрузки скрипта — чтобы при нескольких картах
// на странице loader.js подключался только один раз.
let loaderPromise = null

function load2gisApi() {
  if (typeof window === 'undefined') return Promise.resolve()
  if (window.DG) return Promise.resolve()

  if (!loaderPromise) {
    loaderPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.src = 'https://maps.api.2gis.ru/2.0/loader.js'
      script.onload = resolve
      script.onerror = reject
      document.head.appendChild(script)
    })
  }

  return loaderPromise
}
</script>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

// TODO: указать реальный ключ API 2ГИС. Проще всего — задать VITE_2GIS_API_KEY
// в .env файле проекта, тогда его не нужно будет передавать пропом на каждой странице.
const props = defineProps({
  lat: {
    type: Number,
    required: true,
  },
  lon: {
    type: Number,
    required: true,
  },
  zoom: {
    type: Number,
    default: 100,
  },
  height: {
    type: String,
    default: '480px',
  },
  apiKey: {
    type: String,
    default: () => import.meta.env.VITE_2GIS_API_KEY || '',
  },
  ariaLabel: {
    type: String,
    default: 'Карта 2ГИС',
  },
})

const mapContainer = ref(null)
let mapInstance = null
let markerInstance = null

onMounted(async () => {
  await load2gisApi()

  window.DG.then(() => {
    mapInstance = window.DG.map(mapContainer.value, {
      center: [props.lat, props.lon],
      zoom: props.zoom,
      key: props.apiKey,
    })

    markerInstance = window.DG.marker([props.lat, props.lon]).addTo(mapInstance)
  })
})

// Перецентровываем карту, если координаты меняются (например, выбрали другой магазин)
watch(
  () => [props.lat, props.lon],
  ([newLat, newLon]) => {
    if (!mapInstance) return

    mapInstance.setView([newLat, newLon], props.zoom)
    markerInstance?.setLatLng?.([newLat, newLon])
  }
)

onBeforeUnmount(() => {
  mapInstance?.remove?.()
})
</script>

<template>
  <div ref="mapContainer" class="map-embed" :style="{ height }" :aria-label="ariaLabel" role="img" />
</template>

<style scoped>
.map-embed {
  width: 100%;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
}
</style>