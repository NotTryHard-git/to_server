<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'
import MapEmbed from '@/components/ui/MapEmbed.vue'
import FeedbackForm from '@/components/ui/FeedbackForm.vue'

// TODO: координаты приблизительные (по адресу улицы), уточнить точную геометку здания в 2ГИС
const officeLocation = { lat: 56.501508,  lon: 84.965365 }

const contactGroups =  [
  {
    title: 'Главный офис (секретарь)',
    contacts: [
      {
        type: 'phone',
        label: '+7 (3822) 46-99-66',
        href: 'tel:+73822469966',
      },
      {
        type: 'email',
        label: 'secretary@ellips.biz',
        href: 'mailto:secretary@ellips.biz',
      },
      {
        type: 'address',
        label: 'г. Томск, ул. Дальне-Ключевская, 64ст3',
        href: 'https://ellips.biz/about/contacts/#',
      },
    ],
  },

  {
    title: 'Отдел розничных продаж',
    contacts: [
      {
        type: 'phone',
        label: '+7 (3822) 46-99-66',
        href: 'tel:+73822469966',
      },
      {
        type: 'email',
        label: 'info@ellips.biz',
        href: 'mailto:opt@ellips.biz',
      },
      {
        type: 'address',
        label: 'г. Томск, ул. Дальне-Ключевская, 64ст2',
        href: 'https://ellips.biz/about/contacts/#',
      },
    ],
  },

  {
    title: 'Кадровый центр',
    contacts: [
      {
        type: 'phone',
        label: '+7 (3822) 46-99-66 доб. 104',
        href: 'tel:+73822469966',
      },
      
      {
        type: 'phone',
        label: '+7 923 429-38-18',
        href: 'tel:+79234293818',
      },
      {
        type: 'email',
        label: 'personal1@ellips.biz',
        href: 'mailto:personal1@ellips.biz',
      },

      {
        type: 'email',
        label: 'nb@ellips.biz',
        href: 'mailto:nb@ellips.biz',
      },
      {
        type: 'address',
        label: 'г. Томск, ул. Дальне-Ключевская, 64ст2',
        href: 'https://ellips.biz/about/contacts/#',
      },
      ],
  },
]
</script>

<template>
  <div class="contacts">
    <section class="hero">
      <div class="hero__content">
        <p class="hero__label">Мы на связи</p>
        <h1>Контакты e'llipse</h1>
        <p class="hero__text">
          Свяжитесь с нужным отделом напрямую или найдите нас на карте — мы всегда рады ответить
          на ваши вопросы.
        </p>
      </div>
    </section>

    <section class="location">
      <div class="section-header">
        <p class="section-label">Как нас найти</p>
        <h2>Главный офис в Томске</h2>
      </div>

      <div class="location-grid">
        <div class="map-card">
          <MapEmbed
            :lat="officeLocation.lat"
            :lon="officeLocation.lon"
            aria-label="e'llipse на карте 2ГИС"
            height="100%"
          />
        </div>

        <div class="contacts-list">
          <div v-for="group in contactGroups" :key="group.title" class="contact-card">
            <h3>{{ group.title }}</h3>

            <a
              v-for="contact in group.contacts"
              :key="contact.type + contact.href"
              :href="contact.href"
              class="contact-card__link"
              :target="contact.type === 'address' ? '_blank' : undefined"
              :rel="contact.type === 'address' ? 'noopener' : undefined"
            >
              {{ contact.label }}
            </a>
          </div>

          <div class="contact-card">
            <h3>Мы в социальных сетях</h3>

            <div class="contact-card__socials">
              <!-- TODO: заменить на реальные ссылки на соцсети -->
              <BaseButton tag="a" href="#" color="pink" size="md" shape="circle" variant="outline" aria-label="ВКонтакте">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M13.5 17.2c-5.6 0-9-3.9-9.1-10.3H7c.1 4.4 2 6.3 3.5 6.6V6.9h2.4v4.1c1.5-.2 3.1-1.9 3.6-4.1h2.4c-.4 2.7-2.4 4.6-3.8 5.4 1.4.6 3.6 2.3 4.5 5.1h-2.7c-.7-2-2.3-3.5-4.4-3.7v3.7h-.3z" />
                </svg>
              </BaseButton>
              <BaseButton tag="a" href="#" color="pink" size="md" shape="circle" variant="outline" aria-label="Telegram">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M21.9 4.6 18.7 19c-.2 1-.9 1.3-1.8.8l-4.9-3.6-2.4 2.3c-.3.3-.5.5-1 .5l.3-4.9L18 6.7c.5-.4-.1-.7-.7-.3L7 12.7l-4.7-1.5c-1-.3-1-1 .2-1.5L20.6 3.5c.9-.3 1.6.2 1.3 1.1z" />
                </svg>
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="feedback">
      <div class="section-header">
        <p class="section-label">Есть вопрос?</p>
        <h2>Напишите нам</h2>
      </div>

      <FeedbackForm />
    </section>
  </div>
</template>

<style scoped>
.contacts {
  background: var(--color-main-bg);
  color: var(--color-main-text);
  font-family: var(--font-family-base);
}

/* ---------- Общие ---------- */

section {
  padding: 90px 20px;
}

.section-header {
  max-width: 700px;
  margin: 0 auto 60px;
  text-align: center;
}

.section-label {
  color: var(--color-main-accent);
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.section-header h2 {
  font-size: 42px;
  line-height: 1.2;
}

/* ---------- Hero ---------- */

.hero {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: linear-gradient(160deg, var(--color-header-footer-bg), #1a1a1a);
}

.hero__content {
  max-width: 750px;
  padding: 0 20px;
}

.hero__label {
  color: var(--color-header-footer-accent);
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 20px;
}

.hero h1 {
  color: white;
  font-size: 52px;
  line-height: 1.1;
  margin-bottom: 20px;
}

.hero__text {
  color: rgba(255, 255, 255, 0.85);
  font-size: 18px;
  line-height: 1.8;
}

/* ---------- Location ---------- */

.location-grid {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 30px;
  max-width: 1200px;
  margin: auto;
  align-items: stretch;
}

.map-card {
  min-height: 480px;
}

.contacts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.contact-card {
  background: white;
  color: #222;
  padding: 28px;
  border-radius: 18px;
  transition: 0.3s;
}

.contact-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.contact-card h3 {
  margin-bottom: 14px;
  font-size: 18px;
}

.contact-card__link {
  display: block;
  color: #222;
  text-decoration: none;
  font-size: 15px;
  line-height: 1.9;
  transition: color 0.25s ease;
}

.contact-card__link:hover {
  color: var(--color-main-accent);
}

.contact-card__socials {
  display: flex;
  gap: 12px;
}

/* ---------- Feedback form ---------- */

.feedback {
  background: var(--color-header-footer-bg);
}

.feedback .section-label {
  color: var(--color-header-footer-accent);
}

.feedback .section-header h2 {
  color: white;
}

/* ---------- Адаптив ---------- */

@media (max-width: 900px) {
  .location-grid {
    grid-template-columns: 1fr;
  }

  .map-card,
  .map-card__frame {
    min-height: 320px;
  }

  .hero h1 {
    font-size: 36px;
  }

  .section-header h2 {
    font-size: 34px;
  }
}
</style>