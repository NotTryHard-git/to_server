<script setup>
import BaseButton from '@/components/ui/BaseButton.vue'

const timeline = [
  {
    year: '1991',
    title: 'Первый магазин',
    text: 'В Томске открылся первый магазин e\'llipse. Мы первыми в Сибири предложили формат самообслуживания в сфере косметики и парфюмерии.',
  },
  {
    year: '2000+',
    title: 'Развитие сети',
    text: 'Ассортимент расширился, появились новые магазины и сотрудничество с мировыми брендами.',
  },
  {
    year: 'Сегодня',
    title: 'Крупная региональная сеть',
    text: 'e\'llipse работает в Томске, Кемерове и Новокузнецке, предлагая тысячи товаров для красоты.',
  },
]

const advantages = [
  {
    title: 'Только проверенные бренды',
    text: 'Каждый бренд проходит тщательный отбор. Мы предлагаем только оригинальную продукцию.',
  },
  {
    title: 'Трендовый ассортимент',
    text: 'У нас представлены популярные бренды и самые обсуждаемые новинки индустрии красоты.',
  },
  {
    title: 'Профессиональные консультанты',
    text: 'Наши сотрудники регулярно проходят обучение и помогают подобрать подходящий уход.',
  },
  {
    title: 'Честные цены',
    text: 'Мы ежедневно следим за рынком и предлагаем выгодные акции, скидки и подарки.',
  },
]

const brands = [
  'SHIK',
  'Stellary',
  'Vivienne Sabo',
  'FarmStay',
  'Aravia',
  'Art&Fact',
  'Mixit',
  'Kerasys',
]

const services = [
  {
    title: 'Подарочные карты',
    text: 'Подарок, который всегда будет к месту.',
  },
  {
    title: 'Бьюти-боксы',
    text: 'Готовые наборы для ухода и макияжа.',
  },
  {
    title: 'Программа лояльности',
    text: 'Персональные скидки и специальные предложения.',
  },
]
</script>

<template>
  <div class="about">
    <section class="hero">
      <div class="hero__content">
        <p class="hero__label">С 1991 года</p>

        <h1>Более 30 лет создаём пространство красоты</h1>

        <p class="hero__text">
          e'llipse — крупнейшая сеть магазинов косметики, парфюмерии и ухода в Сибири. Мы объединяем
          мировые бренды, профессиональную консультацию и доступные цены.
        </p>
      </div>
    </section>

    <section class="numbers">
      <div class="number">
        <span>30+</span>

        <p>лет опыта</p>
      </div>

      <div class="number">
        <span>4</span>

        <p>города</p>
      </div>

      <div class="number">
        <span>100+</span>

        <p>брендов</p>
      </div>

      <div class="number">
        <span>10000+</span>

        <p>товаров</p>
      </div>
    </section>

    <section class="history">
      <h2>История компании</h2>

      <div class="timeline">
        <div class="timeline-item" v-for="item in timeline" :key="item.year">
          <div class="timeline-year">
            {{ item.year }}
          </div>

          <div class="timeline-content">
            <h3>
              {{ item.title }}
            </h3>

            <p>
              {{ item.text }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <section class="mission">
      <blockquote>
        «Мы помогаем людям чувствовать уверенность в себе, делая качественную косметику доступной
        каждому.»
      </blockquote>
    </section>
    <section class="advantages">
      <div class="section-header">
        <p class="section-label">Почему выбирают e'llipse</p>

        <h2>Мы создаём комфортный бьюти-шопинг</h2>
      </div>

      <div class="advantages-grid">
        <div v-for="item in advantages" :key="item.title" class="advantage-card">
          <h3>
            {{ item.title }}
          </h3>

          <p>
            {{ item.text }}
          </p>
        </div>
      </div>
    </section>

    <section class="brands">
      <div class="section-header">
        <p class="section-label">Любимые бренды</p>

        <h2>Только оригинальная продукция</h2>
      </div>

      <div class="brands-grid">
        <div class="brand-card" v-for="brand in brands" :key="brand">
          {{ brand }}
        </div>
      </div>
    </section>

    <section class="services">
      <div class="section-header">
        <p class="section-label">Больше чем магазин</p>

        <h2>Мы стараемся сделать покупки ещё приятнее</h2>
      </div>

      <div class="services-grid">
        <div class="service-card" v-for="item in services" :key="item.title">
          <h3>
            {{ item.title }}
          </h3>

          <p>
            {{ item.text }}
          </p>
        </div>
      </div>
    </section>

    <section class="cta">
      <div class="cta-content">
        <h2>Добро пожаловать в e'llipse</h2>

        <p>
          Приходите в наши магазины, знакомьтесь с мировыми брендами, получайте консультации
          специалистов и открывайте для себя мир красоты.
        </p>

        <BaseButton color="accent" size="lg" shape="pill" class="cta-button">
          Найти ближайший магазин
        </BaseButton>
      </div>
    </section>
  </div>
</template>
<style scoped>
.about {
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
  min-height: 550px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background:
    linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)),
    url('@/assets/images/about1.jpg');
  background-size: cover;
  background-position: center;
}

.hero__content {
  max-width: 850px;
}

.hero__label {
  color: var(--color-main-accent);
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 20px;
}

.hero h1 {
  color: white;
  font-size: 64px;
  line-height: 1.1;
  margin-bottom: 30px;
}

.hero__text {
  color: rgba(255, 255, 255, 0.85);
  font-size: 20px;
  line-height: 1.8;
}

/* ---------- Numbers ---------- */

.numbers {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: auto;
}

.number {
  text-align: center;
  padding: 35px;
  border-radius: 18px;
  background: var(--color-header-footer-bg);
}

.number span {
  display: block;
  color: var(--color-header-footer-accent);
  font-size: 56px;
  font-weight: bold;
}

.number p {
  margin-top: 12px;
  color: var(--color-header-footer-text);
}

/* ---------- History ---------- */

.history {
  max-width: 1200px;
  margin: auto;
}

.history h2 {
  text-align: center;
  font-size: 42px;
  margin-bottom: 70px;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 45px;
}

.timeline-item {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.timeline-year {
  min-width: 140px;
  font-size: 32px;
  font-weight: bold;
  color: var(--color-main-accent);
}

.timeline-content {
  flex: 1;
  border-left: 3px solid var(--color-main-accent);
  padding-left: 30px;
}

.timeline-content h3 {
  margin-bottom: 12px;
  font-size: 24px;
}

.timeline-content p {
  line-height: 1.8;
}

/* ---------- Mission ---------- */

.mission {
  background: var(--color-header-footer-bg);
}

.mission blockquote {
  max-width: 900px;
  margin: auto;
  text-align: center;
  color: white;
  font-size: 34px;
  line-height: 1.6;
  font-style: italic;
}

/* ---------- Advantages ---------- */

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: auto;
}

.advantage-card {
  background: white;
  color: #222;
  padding: 40px;
  border-radius: 18px;
  transition: 0.3s;
}

.advantage-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
}

.advantage-card h3 {
  margin-bottom: 16px;
  font-size: 24px;
}

.advantage-card p {
  line-height: 1.7;
}

/* ---------- Brands ---------- */

.brands-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: auto;
}

.brand-card {
  border: 2px solid var(--color-main-accent);
  border-radius: 14px;
  padding: 35px;
  text-align: center;
  font-size: 22px;
  font-weight: bold;
  transition: 0.25s;
}

.brand-card:hover {
  background: var(--color-main-accent);
  color: white;
}

/* ---------- Services ---------- */

.services-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: auto;
}

.service-card {
  text-align: center;
  padding: 40px;
  background: var(--color-header-footer-bg);
  color: white;
  border-radius: 18px;
}
.service-card:hover {
  background: var(--color-main-accent);
  color: white;
}

.service-card h3 {
  margin-bottom: 15px;
}

/* ---------- CTA ---------- */

.cta {
  background:
    linear-gradient(rgba(0, 0, 0, 0.82), rgba(0, 0, 0, 0.82)),
    url('@/assets/images/about2.jpg');
  background-size: cover;
  background-position: center;
}

.cta-content {
  max-width: 800px;
  margin: auto;
  text-align: center;
}

.cta h2 {
  color: white;
  font-size: 48px;
  margin-bottom: 24px;
}

.cta p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 20px;
  line-height: 1.8;
  margin-bottom: 40px;
}

/* ---------- Адаптив ---------- */

@media (max-width: 900px) {
  .numbers,
  .advantages-grid,
  .brands-grid,
  .services-grid {
    grid-template-columns: 1fr;
  }

  .timeline-item {
    flex-direction: column;
  }

  .timeline-year {
    min-width: auto;
  }

  .hero h1 {
    font-size: 42px;
  }

  .section-header h2 {
    font-size: 34px;
  }

  .mission blockquote {
    font-size: 26px;
  }

  .cta h2 {
    font-size: 36px;
  }
}
</style>