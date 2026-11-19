<script setup>
import FeedbackForm from '@/components/ui/FeedbackForm.vue'

const vacancies = [
  {
    title: 'Экспедитор',
    salary: 'от 35 000 ₽',
    requirements:
      'Соблюдение трудовой дисциплины. Пунктуальность, ответственность. Готовность к физическим нагрузкам. Правила применения простейших погрузочно-разгрузочных приспособлений и средств транспортировки.',
    duties: 'Погрузо-разгрузочные работы, подъём, перемещение, укладка груза.',
    conditions:
      'График работы пн.–пт. с 9:00 до 18:00, командировки. Разъездной характер работы. Стабильная оплата труда. Официальное трудоустройство по ТК РФ.',
  },
  {
    title: 'Кладовщик',
    salary: 'от 32 000 ₽',
    requirements: 'Внимательность, пунктуальность. Опыт от года.',
    duties:
      'Приём товара, поступающего на склад, сборка и расстановка товара, выдача товара. При необходимости — погрузочно-разгрузочные работы при отпуске и поступлении товара, расстановке товара.',
    conditions: 'Пятидневная рабочая неделя с понедельника по пятницу, выходные — суббота, воскресенье.',
  },
  {
    title: 'Ведущий специалист по налоговому и бухгалтерскому учёту',
    salary: 'от 55 000 ₽',
    requirements:
      'Высшее профессиональное (экономическое, бухгалтерское) образование. Опыт работы. Уверенный пользователь ПК. Владение программой 1С:8.',
    duties:
      'Ведение 3-х юридических лиц на УСН (доходы — расходы); подготовка и сдача бухгалтерской, статистической и налоговой отчётности; контроль за правильностью отражения документов в бухгалтерском учёте; организация системы внутреннего контроля за правильностью оформления хозяйственных операций; работа по обеспечению финансовой и кассовой дисциплин.',
    conditions: '',
  },
  {
    title: 'Категорийный менеджер',
    salary: 'от 55 000 ₽',
    requirements: 'Высшее образование, знание 1С 8, Word, Excel.',
    duties:
      'Категория: уходовая косметика, поиск и выбор поставщиков. Переговоры с поставщиками, заключение договоров, организация закупки товара и его доставки, работа с поставщиками по разработке и проведению маркетинговых мероприятий, управление и анализ ассортиментной матрицы, взаимодействие с магазинами по вопросам поставок, недопоставок, возвратов товара, отчёты по вверенным категориям товара.',
    conditions: 'Пятидневная рабочая неделя с 9:00 до 18:00, выходные — суббота, воскресенье.',
  },
  {
    title: 'Продавцы-консультанты',
    salary: 'от 35 000 ₽',
    requirements:
      'Вежливость и доброжелательность. Активность, стремление к развитию и обучению. Интерес к Beauty-индустрии. Хорошие коммуникативные навыки.',
    duties:
      'Активная работа с покупателями. Консультирование покупателей по продукции. Работа с товаром (приём товара, выкладка, контроль наличия актуальных ценников, участие в инвентаризации). Поддержание чистоты и порядка в торговом зале. Работа на кассе.',
    conditions:
      'Работа в стабильной, динамично развивающейся компании. Бесплатное обучение с нуля, тренинги. Плавающий график 4/2 с 10:00 до 20:00. Корпоративные скидки. Карьерный рост. Дружный коллектив.',
  },
]

const reasons = [
  'Работа в стабильной компании',
  'Бесплатное обучение',
  'Быть в курсе всех новинок и инноваций парфюмерно-косметического рынка',
  'Дружный коллектив',
  'Возможность работать рядом с домом',
]

</script>

<template>
  <div class="career">
    <section class="hero">
      <div class="hero__content">
        <p class="hero__label">Работа в e'llipse</p>

        <h1>Растите вместе с нами</h1>

        <p class="hero__text">
          Компания «Эллипс» заинтересована в привлечении профессиональных и талантливых
          специалистов. У любого сотрудника, пришедшего в компанию, есть возможность
          профессионального, личностного и карьерного роста.
        </p>

        <p class="hero__contacts">
          Заполните анкету на сайте, отправьте резюме на
          <a href="mailto:nb@ellips.biz">nb@ellips.biz</a>
          или позвоните по телефону
          <a href="tel:+79234293818">+7 923 429-38-18</a>
        </p>
      </div>
    </section>

    <section class="vacancies">
      <div class="section-header">
        <p class="section-label">Открытые позиции</p>
        <h2>Доступные вакансии</h2>
      </div>

      <div class="vacancies-grid">
        <div v-for="vacancy in vacancies" :key="vacancy.title" class="vacancy-card">
          <div class="vacancy-card__header">
            <h3>{{ vacancy.title }}</h3>
            <span class="vacancy-card__salary">{{ vacancy.salary }}</span>
          </div>

          <div class="vacancy-card__block">
            <p class="vacancy-card__block-title">Требования</p>
            <p>{{ vacancy.requirements }}</p>
          </div>

          <div class="vacancy-card__block">
            <p class="vacancy-card__block-title">Обязанности</p>
            <p>{{ vacancy.duties }}</p>
          </div>

          <div v-if="vacancy.conditions" class="vacancy-card__block">
            <p class="vacancy-card__block-title">Условия</p>
            <p>{{ vacancy.conditions }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="reasons">
      <div class="section-header">
        <p class="section-label">Почему выбирают нас</p>
        <h2>10 причин работать в e'llipse</h2>
      </div>

      <div class="reasons-grid">
        <div v-for="(reason, index) in reasons" :key="reason" class="reason-card">
          <span class="reason-card__number">{{ index + 1 }}</span>
          <p>{{ reason }}</p>
        </div>
      </div>
    </section>

    <section class="cta">
      <div class="cta-content">
        <h2>Готовы присоединиться к e'llipse?</h2>

        <p>
          Отправьте резюме на <a href="mailto:nb@ellips.biz">nb@ellips.biz</a> или позвоните по
          телефону <a href="tel:+79234293818">+7 923 429-38-18</a> — расскажем подробнее о
          вакансиях и ответим на вопросы. Либо оставьте контакты здесь, и мы свяжемся сами:
        </p>

        <FeedbackForm submit-label="Отправить резюме" success-message="Спасибо! Мы получили вашу заявку и скоро свяжемся с вами." />
      </div>
    </section>
  </div>
</template>

<style scoped>
.career {
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
  min-height: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: linear-gradient(160deg, var(--color-header-footer-bg), #1a1a1a);
}

.hero__content {
  max-width: 850px;
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
  font-size: 56px;
  line-height: 1.1;
  margin-bottom: 24px;
}

.hero__text {
  color: rgba(255, 255, 255, 0.85);
  font-size: 18px;
  line-height: 1.8;
  margin-bottom: 20px;
}

.hero__contacts {
  color: rgba(255, 255, 255, 0.7);
  font-size: 15px;
  line-height: 1.8;
}

.hero__contacts a,
.cta-content a {
  color: var(--color-header-footer-accent);
  text-decoration: none;
}

.hero__contacts a:hover,
.cta-content a:hover {
  text-decoration: underline;
}

/* ---------- Vacancies ---------- */

.vacancies-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
  max-width: 1200px;
  margin: auto;
}

.vacancy-card {
  background: white;
  color: #222;
  padding: 40px;
  border-radius: 18px;
  transition: 0.3s;
}

.vacancy-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
}

.vacancy-card__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.vacancy-card__header h3 {
  font-size: 22px;
}

.vacancy-card__salary {
  flex-shrink: 0;
  color: var(--color-main-accent);
  font-weight: 700;
  font-size: 16px;
}

.vacancy-card__block {
  margin-bottom: 16px;
}

.vacancy-card__block:last-child {
  margin-bottom: 0;
}

.vacancy-card__block-title {
  font-weight: 600;
  margin-bottom: 6px;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #888;
}

.vacancy-card__block p {
  line-height: 1.7;
  font-size: 15px;
}

/* ---------- Reasons ---------- */

.reasons-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: auto;
}

.reason-card {
  border: 2px solid var(--color-main-accent);
  border-radius: 14px;
  padding: 30px 20px;
  text-align: center;
  transition: 0.25s;
}

.reason-card:hover {
  background: var(--color-main-accent);
  color: white;
}

.reason-card__number {
  display: block;
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 12px;
}

.reason-card p {
  font-size: 14px;
  line-height: 1.5;
}

/* ---------- Growth path ---------- */


.growth .section-label {
  color: var(--color-header-footer-accent);
}

.growth .section-header h2 {
  color: white;
}

.growth-path {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 16px;
  max-width: 1200px;
  margin: auto;
}

.growth-step {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--color-header-footer-accent);
  color: white;
  border-radius: 999px;
  padding: 14px 26px;
  font-size: 15px;
  white-space: nowrap;
}

.growth-arrow {
  color: var(--color-header-footer-accent);
  font-size: 20px;
}

/* ---------- CTA ---------- */

.cta {
  background: linear-gradient(160deg, var(--color-header-footer-bg), #1a1a1a);
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
  font-size: 18px;
  line-height: 1.8;
  margin-bottom: 40px;
}

/* ---------- Адаптив ---------- */

@media (max-width: 900px) {
  .vacancies-grid,
  .growth-path {
    grid-template-columns: 1fr;
  }

  .reasons-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero h1 {
    font-size: 38px;
  }

  .section-header h2 {
    font-size: 34px;
  }

  .cta h2 {
    font-size: 34px;
  }

  .vacancy-card__header {
    flex-direction: column;
    gap: 4px;
  }
}

@media (max-width: 560px) {
  .reasons-grid {
    grid-template-columns: 1fr;
  }
}
</style>