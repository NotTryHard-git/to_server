<script setup>
import logo from '@/assets/images/eng_logo.png'

// TODO: заменить на реальные контакты, когда появится источник данных
const contacts = {
  phone: '+7(3822)46-99-66',
  INN: 'ООО "Эллипс" ИНН 7021003260',
}

// TODO: заменить на реальный список городов присутствия
const stores = ['Томск', 'Северск', 'Кемерово', 'Новокузнецк']

const customerLinks = [
  { to: { name: 'about' }, label: 'О компании' },
  { to: { name: 'contacts' }, label: 'Контакты' },
  { to: { name: 'career' }, label: 'Карьера' },
  { to: { name: 'giftCards' }, label: 'Подарочные карты' },
]
</script>


<template>
  <div class="app-footer-line" />

  <footer class="app-footer">
    <div class="app-footer__top">
      <div class="app-footer__brand">
        <RouterLink to="/" class="app-footer__logo">
          <img :src="logo" alt="e'llipse" width="150" height="60" />
        </RouterLink>
        <p class="app-footer__tagline">Красота доступна каждому<br />с 1991 года</p>

        <div class="app-footer__socials">
          <!-- TODO: заменить на реальные ссылки на соцсети -->
          <BaseButton tag="a" href="#" color="gold" size="md" shape="circle" variant="outline" aria-label="ВКонтакте">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M13.5 17.2c-5.6 0-9-3.9-9.1-10.3H7c.1 4.4 2 6.3 3.5 6.6V6.9h2.4v4.1c1.5-.2 3.1-1.9 3.6-4.1h2.4c-.4 2.7-2.4 4.6-3.8 5.4 1.4.6 3.6 2.3 4.5 5.1h-2.7c-.7-2-2.3-3.5-4.4-3.7v3.7h-.3z" />
            </svg>
          </BaseButton>
          <BaseButton tag="a" href="#" color="gold" size="md" shape="circle" variant="outline" aria-label="Telegram">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M21.9 4.6 18.7 19c-.2 1-.9 1.3-1.8.8l-4.9-3.6-2.4 2.3c-.3.3-.5.5-1 .5l.3-4.9L18 6.7c.5-.4-.1-.7-.7-.3L7 12.7l-4.7-1.5c-1-.3-1-1 .2-1.5L20.6 3.5c.9-.3 1.6.2 1.3 1.1z" />
            </svg>
          </BaseButton>
        </div>
      </div>

      <div class="app-footer__column">
        <p class="app-footer__column-title">Покупателям</p>
        <RouterLink
          v-for="link in customerLinks"
          :key="link.label"
          :to="link.to"
          class="app-footer__link"
        >
          {{ link.label }}
        </RouterLink>
      </div>

      <div class="app-footer__column">
        <p class="app-footer__column-title">Магазины</p>
        <!-- TODO: сделать ссылками на страницы магазинов по городам -->
        <span v-for="city in stores" :key="city" class="app-footer__text-item">
          {{ city }}
        </span>
      </div>

      <div class="app-footer__column">
        <p class="app-footer__column-title">Контакты</p>
        <span class="app-footer__text-item">{{ contacts.phone }}</span>
        <span class="app-footer__text-item">{{ contacts.INN }}</span>
      </div>
    </div>

    <div class="app-footer__divider" />

    <p class="app-footer__copyright">
      © e'llipse, 1995–2026. Все права защищены.
    </p>
  </footer>
</template>

<style scoped>
.app-footer-line {
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--color-header-footer-accent),
    transparent
  );
}

.app-footer {
  background-color: var(--color-header-footer-bg);
  color: var(--color-header-footer-text);
  font-family: var(--font-family-base);
  box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.08);
  padding: 56px 32px 24px;
}

.app-footer__top {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 1fr;
  gap: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.app-footer__brand {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.app-footer__logo {
  display: flex;
  opacity: 0.85;
  transition: opacity 0.25s ease;
}

.app-footer__logo img {
  mix-blend-mode: screen;
}

.app-footer__logo:hover {
  opacity: 1;
}

.app-footer__tagline {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--color-header-footer-accent);
  opacity: 0.9;
}

.app-footer__socials {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.app-footer__column {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.app-footer__column-title {
  margin: 0 0 4px;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-header-footer-accent);
}

.app-footer__link {
  color: var(--color-header-footer-text);
  text-decoration: none;
  font-size: 14px;
  width: fit-content;
  transition: color 0.25s ease;
}

.app-footer__link:hover {
  color: var(--color-header-footer-accent);
}

.app-footer__text-item {
  font-size: 14px;
  opacity: 0.85;
}

.app-footer__divider {
  max-width: 1200px;
  margin: 40px auto 20px;
  height: 1px;
  background-color: var(--color-header-footer-accent);
  opacity: 0.25;
}

.app-footer__copyright {
  margin: 0;
  font-size: 13px;
  color: var(--color-header-footer-text);
  opacity: 0.6;
  text-align: center;
}

@media (max-width: 900px) {
  .app-footer__top {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 560px) {
  .app-footer {
    padding: 40px 20px 20px;
  }

  .app-footer__top {
    grid-template-columns: 1fr;
    gap: 32px;
    text-align: center;
  }

  .app-footer__brand {
    align-items: center;
  }

  .app-footer__logo {
    justify-content: center;
  }

  .app-footer__tagline {
    text-align: center;
  }

  .app-footer__socials {
    justify-content: center;
  }

  .app-footer__column {
    align-items: center;
    text-align: center;
  }

  .app-footer__column-title {
    text-align: center;
  }

  .app-footer__link {
    width: auto;
    text-align: center;
  }

  .app-footer__text-item {
    text-align: center;
  }

  .app-footer__divider {
    margin: 32px auto 20px;
  }

  .app-footer__copyright {
    text-align: center;
    line-height: 1.5;
  }
}
</style>