<script setup>
import { ref } from 'vue'

import giftCard1 from '@/assets/images/gift_card1.png'
import giftCard2 from '@/assets/images/gift_card2.png'
import giftCard3 from '@/assets/images/gift_card3.png'

import BaseButton from '@/components/ui/BaseButton.vue'
import ImageSlider from '@/components/ui/ImageSlider.vue'

const giftCardImages = [giftCard1, giftCard2, giftCard3]

const denominations = ['500 ₽', '1000 ₽', '2000 ₽', '3000 ₽', '5000 ₽']

const conditions = [
  'Подарочной картой можно оплатить только одну покупку.',
  'При покупке Подарочной карты скидки не предоставляются.',
  'При оплате покупки Подарочной картой действуют все скидки магазинов Эллипс E\'llipse, Эллипс E\'llipse Beauty, в том числе скидка по дисконтной карте, и сумма покупки зачисляется на баланс дисконтной карты.',
  'Подарочная карта возврату, обмену не подлежит.',
]

const advantages = [
  'Экономия времени и сил на поиск чего-то оригинального, но не всегда нужного.',
  'Карты можно дарить всем — руководителям, рядовым сотрудникам, коллегам, партнёрам.',
]

const isRulesOpen = ref(false)

function toggleRules() {
  isRulesOpen.value = !isRulesOpen.value
}
</script>

<template>
  <div class="gift-cards">
    <section class="hero">
      <div class="hero__content">
        <p class="hero__label">Подарок без раздумий</p>
        <h1>Подарочные карты e'llipse</h1>
        <p class="hero__text">
          Позвольте близким выбрать любимые ароматы и косметику самостоятельно.
        </p>
      </div>
    </section>

    <section class="gallery">
      <ImageSlider :images="giftCardImages" height="500px" />
    </section>

    <section class="info">
      <div class="section-header">
        <p class="section-label">Условия</p>
        <h2>Подарочные карты</h2>
      </div>

      <div class="info-content">
        <div class="denominations">
          <span v-for="denomination in denominations" :key="denomination" class="denomination-chip">
            {{ denomination }}
          </span>
        </div>

        <p>
          На сумму Подарочной карты сети Эллипс E'llipse её владелец подберёт для себя или в
          подарок любимые ароматы, средства для макияжа и ухода за кожей, подарочные наборы и
          огромный ассортимент товаров из Кореи, Японии, Таиланда.
        </p>

        <p>Подарочная карта действительна только при предъявлении чека.</p>

        <ul class="conditions-list">
          <li v-for="condition in conditions" :key="condition">{{ condition }}</li>
        </ul>
      </div>
    </section>

    <section class="business">
      <div class="section-header">
        <p class="section-label">Для компаний</p>
        <h2>Приобретение подарочных карт для юридических лиц</h2>
      </div>

      <div class="advantages-grid">
        <div v-for="advantage in advantages" :key="advantage" class="advantage-card">
          <p>{{ advantage }}</p>
        </div>
      </div>

      <p class="business__text">
        Подарочные карты любого номинала по вашему выбору можно приобрести в каждом магазине
        Эллипс E'llipse.
      </p>
      <p class="business__text">
        По оптовому приобретению карт по безналичному расчёту пишите:
        <a href="mailto:info@ellips.biz">info@ellips.biz</a>
      </p>

      <p class="business__contacts">
        Тел. <a href="tel:+73822469966">8 (3822) 46-99-66</a>
        <br />
        <a href="https://www.ellips.biz" target="_blank" rel="noopener">www.ellips.biz</a>
      </p>
    </section>

    <section class="rules">
      <div class="section-header">
        <p class="section-label">Дополнительная информация</p>
        <h2>Правила розничной продажи сертификатов</h2>
      </div>

      <div class="rules__toggle">
        <BaseButton color="accent" size="lg" shape="pill" @click="toggleRules">
          {{ isRulesOpen ? 'Скрыть правила' : 'Показать правила' }}
        </BaseButton>
      </div>

      <div v-if="isRulesOpen" class="rules__content">
        <p>
          Подарочный сертификат торговой сети Эллипс E'llipse (далее — «ПС», «Подарочный
          сертификат», «Подарочные сертификаты») — это материальный носитель информации на
          пластиковой карточке, удостоверяющий имущественное право Предъявителя приобрести Товар
          в любом из магазинов торговой сети Эллипс E'llipse на сумму, эквивалентную Номиналу ПС.
        </p>
        <p>
          ПС свидетельствуют о том, что Предъявитель не обязан при покупке Товара в Месте
          приобретения Товара вносить в кассу (на счёт) Продавца денежные средства в оплату
          стоимости Товара в части, равной Номиналу подарочного сертификата. Подарочный
          сертификат подтверждает встречное обязательство Продавца в течение срока действия
          Подарочного сертификата принять его у Предъявителя в оплату Товара в Месте приобретения
          Товара в размере его Номинала, эквивалентного сумме, перечисленной Покупателем Продавцу
          за такой Подарочный сертификат. Подарочный сертификат является публичной офертой и
          подтверждает право Предъявителя на заключение с Продавцом договора розничной
          купли-продажи Товара путём использования Предъявителем в Месте приобретения Товара
          Подарочного сертификата определённого Номинала.
        </p>
        <p>
          Номинал подарочного сертификата — максимальный размер суммы в рублях, на которую
          Предъявитель Подарочного сертификата может приобрести Товар Продавца при предъявлении
          Подарочного сертификата в Месте приобретения Товара.
        </p>
        <p>Покупатель — лицо, которое приобретает у Продавца ПС по настоящему Договору.</p>
        <p>
          Предъявитель — физическое лицо, правомерно владеющее и распоряжающееся подарочным
          сертификатом в результате получения такого сертификата от Покупателя, обладающее правом
          приобретения Товара в розницу для личного, семейного и иного использования, не
          связанного с предпринимательской деятельностью, в Месте приобретения Товара за счёт
          использования Предъявителем Подарочного сертификата в пределах Номинала Подарочного
          сертификата или в пределах суммы остатка денежных средств на Подарочном сертификате.
        </p>
        <p>
          Товар — парфюмерно-косметическая продукция и иные товары, представленные для продажи в
          сети розничных магазинов Эллипс E'llipse.
        </p>
        <p>
          Место приобретения Товара — розничные магазины парфюмерии и косметики сети Эллипс
          E'llipse в г. Томске и г. Кемерово.
        </p>

        <h3>2. Продавец обязан</h3>
        <p>
          2.1. Передать Покупателю Подарочные сертификаты после их оплаты. Факт передачи
          Подарочных сертификатов подтверждается кассовым чеком.
        </p>
        <p>
          2.2. Принять в оплату Товара, приобретаемого Предъявителем в Месте приобретения Товара,
          Подарочные сертификаты в размере их Номинала и передать Предъявителю Товар надлежащего
          качества, цена которого соответствует Номиналу Подарочных сертификатов.
        </p>

        <h3>3. Продавец имеет право</h3>
        <p>
          3.1. Самостоятельно устанавливать и регламентировать условия приобретения и
          использования Подарочных сертификатов Эллипс E'llipse, отражая часть из них на
          наружной поверхности Подарочного сертификата.
        </p>
        <p>
          3.2. Отказать в приёме к оплате сертификаты, срок действия которых истёк, если на
          оборот сертификатов установлен срок действия; в случае выявления недействительности
          сертификата (подделке, повторности предъявления к оплате).
        </p>
        <p>
          3.3. Запросить у Покупателя кассовый чек на приобретение сертификата в случае подозрения
          на недействительность сертификата.
        </p>

        <h3>4. Общие правила оплаты товара подарочным сертификатом</h3>
        <p>
          4.1. Подарочный сертификат подтверждает право Предъявителя на заключение с Продавцом
          договора розничной купли-продажи Товара путём предъявления к его оплате Подарочного
          сертификата определённого Номинала.
        </p>
        <p>
          4.2. Срок действия каждого Подарочного сертификата (если он установлен) указан на
          сертификате и начинает исчисляться с момента приобретения Подарочного сертификата,
          подтверждённого кассовым чеком. По истечении данного срока Продавец вправе отказать
          Предъявителю такого Подарочного сертификата в принятии его в качестве оплаты в счёт
          розничной продажи Товара.
        </p>
        <p>
          4.3. В случае если сумма приобретаемого Предъявителем Товара превышает размер Номинала
          подарочного сертификата, Предъявитель обязан оплатить Продавцу сумму превышения размера
          Номинала дополнительно.
        </p>
        <p>
          4.4. В случае если сумма приобретаемого Предъявителем Товара меньше размера Номинала
          подарочного сертификата, то остаток денежных средств наличными Предъявителю выплате не
          подлежит. Предъявление сертификата в магазин возможно только один раз, при этом
          использованный сертификат подлежит сдаче кассиру розничной точки в обмен на товар.
        </p>
        <p>
          4.5. Переданные Покупателю и/или Предъявителю Подарочные сертификаты не являются товаром
          и обмену, размену и/или возврату Покупателем Продавцу не подлежат. Покупатель или
          Предъявитель сертификата не вправе требовать от Продавца возврата денежных средств в
          размере номинала подарочного сертификата вместо обмена его на товар.
        </p>
        <p>
          4.6. Утраченный сертификат восстановлению не подлежит. Предъявление к оплате за товар
          вместо подарочного сертификата чека на его приобретение не допускается.
        </p>

        <h3>5. Рекламации</h3>
        <p>
          5.6. Основные правила оборота сертификатов размещаются на наружной поверхности
          сертификата. Иные условия Покупатель может уточнить у Продавцов в торговых точках, либо
          ознакомиться на сайте
          <a href="https://www.ellips.biz" target="_blank" rel="noopener">www.ellips.biz</a>.
        </p>
        <p>
          5.7. Претензии Покупателя, касающиеся оборота сертификатов, принимаются в письменном
          виде через торговую точку по месту приобретения сертификата или предъявления его к
          оплате за товар.
        </p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.gift-cards {
  background: var(--color-main-bg);
  color: var(--color-main-text);
  font-family: var(--font-family-base);
}

section {
  padding: 70px 20px;
}

.section-header {
  max-width: 700px;
  margin: 0 auto 48px;
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
  font-size: 36px;
  line-height: 1.2;
}

/* ---------- Hero ---------- */

.hero {
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background: linear-gradient(160deg, var(--color-header-footer-bg), #1a1a1a);
}

.hero__content {
  max-width: 700px;
  padding: 0 20px;
}

.hero__label {
  color: var(--color-header-footer-accent);
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 16px;
}

.hero h1 {
  color: white;
  font-size: 44px;
  line-height: 1.15;
  margin-bottom: 16px;
}

.hero__text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 17px;
}

/* ---------- Gallery ---------- */

.gallery {
  max-width: 900px;
  margin: 0 auto;
  padding-bottom: 0;
}

/* ---------- Info ---------- */

.info-content {
  max-width: 800px;
  margin: 0 auto;
}

.info-content p {
  font-size: 16px;
  line-height: 1.7;
  margin-bottom: 16px;
}

.denominations {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-bottom: 28px;
}

.denomination-chip {
  border: 1px solid var(--color-main-accent);
  color: var(--color-main-accent);
  border-radius: 999px;
  padding: 8px 20px;
  font-weight: 600;
  font-size: 15px;
}

.conditions-list {
  margin: 24px 0 0;
  padding-left: 20px;
}

.conditions-list li {
  font-size: 15px;
  line-height: 1.7;
  margin-bottom: 10px;
}

/* ---------- Business ---------- */

.business {
  background: white;
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  max-width: 800px;
  margin: 0 auto 32px;
}

.advantage-card {
  border: 2px solid var(--color-main-accent);
  border-radius: 14px;
  padding: 24px;
  text-align: center;
  transition: 0.25s;
}

.advantage-card:hover {
  background: var(--color-main-accent);
  color: white;
}

.advantage-card p {
  font-size: 15px;
  line-height: 1.6;
  margin: 0;
}

.business__text {
  max-width: 700px;
  margin: 0 auto 12px;
  text-align: center;
  font-size: 16px;
  line-height: 1.7;
}

.business__text a,
.business__contacts a {
  color: var(--color-main-accent);
  text-decoration: none;
}

.business__text a:hover,
.business__contacts a:hover {
  text-decoration: underline;
}

.business__contacts {
  margin-top: 24px;
  text-align: center;
  font-size: 16px;
  line-height: 1.9;
}

/* ---------- Rules ---------- */

.rules {
  background: var(--color-header-footer-bg);
}

.rules .section-label {
  color: var(--color-header-footer-accent);
}

.rules .section-header h2 {
  color: white;
}

.rules__toggle {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}

.rules__content {
  max-width: 800px;
  margin: 0 auto;
  color: rgba(255, 255, 255, 0.8);
}

.rules__content h3 {
  color: white;
  font-size: 18px;
  margin: 28px 0 12px;
}

.rules__content p {
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 14px;
}

.rules__content a {
  color: var(--color-header-footer-accent);
}

/* ---------- Адаптив ---------- */

@media (max-width: 700px) {
  .advantages-grid {
    grid-template-columns: 1fr;
  }

  .hero h1 {
    font-size: 32px;
  }

  .section-header h2 {
    font-size: 28px;
  }
}
</style>