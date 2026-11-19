import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Боевая сборка без адреса API ушла бы на http://localhost:8000 — не даём так собрать
  if (mode === 'production') {
    const env = loadEnv(mode, process.cwd(), 'VITE_')
    const api = env.VITE_API_BASE_URL || process.env.VITE_API_BASE_URL
    if (!api || /localhost|127\.0\.0\.1/.test(api)) {
      throw new Error(
        'VITE_API_BASE_URL не задан или указывает на localhost. ' +
          'Создайте .env.production (см. .env.production.example) или передайте переменную при сборке.',
      )
    }
  }

  return {
    plugins: [vue(), vueDevTools()],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
  }
})
