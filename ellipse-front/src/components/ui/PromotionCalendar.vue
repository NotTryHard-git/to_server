<script setup>
import { computed } from 'vue'

const props = defineProps({
  promotions: {
    type: Array,
    required: true,
  },
  modelValue: {
    type: Date,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue'])

const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

const currentMonth = computed(() => {
  const today = new Date()

  return new Date(
    today.getFullYear(),
    today.getMonth(),
    1,
  )
})

const monthName = computed(() =>
  currentMonth.value.toLocaleDateString('ru-RU', {
    month: 'long',
    year: 'numeric',
  }),
)

function formatDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

function promotionCount(date) {
  const current = formatDate(date)

  return props.promotions.filter((promotion) => {
    if (
      promotion.type === 'permanent' ||
      !promotion.startDate ||
      !promotion.endDate
    ) {
      return false
    }

    return (
      promotion.startDate <= current &&
      promotion.endDate >= current
    )
  }).length
}

const days = computed(() => {
  const year = currentMonth.value.getFullYear()
  const month = currentMonth.value.getMonth()

  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  let firstWeekDay = firstDay.getDay()

  // Делаем понедельник первым днём недели
  firstWeekDay = firstWeekDay === 0
    ? 6
    : firstWeekDay - 1

  const result = []

  // Пустые ячейки перед первым днём месяца
  for (let i = 0; i < firstWeekDay; i++) {
    result.push(null)
  }

  // Дни текущего месяца
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const date = new Date(year, month, day)

    result.push({
      day,
      date,
      promotions: promotionCount(date),
    })
  }

  return result
})

function selectDay(day) {
  emit('update:modelValue', day.date)
}

function isSelected(day) {
  if (!day) return false

  return (
    day.date.toDateString() ===
    props.modelValue.toDateString()
  )
}

function isToday(day) {
  if (!day) return false

  return (
    day.date.toDateString() ===
    new Date().toDateString()
  )
}
</script>

<template>
  <div class="calendar">
    <div class="calendar__header">
      <h2 class="calendar__title">
        {{ monthName }}
      </h2>
    </div>

    <div class="calendar__weekdays">
      <div
        v-for="day in weekDays"
        :key="day"
        class="calendar__weekday"
      >
        {{ day }}
      </div>
    </div>

    <div class="calendar__grid">
      <template
        v-for="(day, index) in days"
        :key="index"
      >
        <div
          v-if="!day"
          class="calendar__empty"
        />

        <button
          v-else
          class="calendar__day"
          :class="{
            'calendar__day--selected': isSelected(day),
            'calendar__day--today': isToday(day),
          }"
          @click="selectDay(day)"
        >
          <span class="calendar__number">
            {{ day.day }}
          </span>

          <span
            v-if="day.promotions"
            class="calendar__badge"
          >
            {{ day.promotions }}
          </span>
        </button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.calendar {
  width: 100%;
  max-width: 1200px;

  margin: 0 auto;

  padding: 48px;

  background: var(--color-header-footer-bg);

  border-radius: 24px;
}

.calendar__header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 48px;

  margin-bottom: 40px;
}

.calendar__title {
  margin: 0;

  font-size: var(--text-title);
  font-weight: var(--font-weight-bold);
}

.calendar__nav {
  background: none;
  border: none;

  color: var(--color-main-accent);

  cursor: pointer;

  font-size: 36px;

  transition: .2s;
}

.calendar__nav:hover {
  transform: scale(1.15);
}

.calendar__weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);

  gap: 16px;

  margin-bottom: 16px;
}

.calendar__weekday {
  text-align: center;

  color: rgba(255,255,255,.75);

  font-size: 20px;
  font-weight: 600;
}

.calendar__grid {
  display: grid;

  grid-template-columns: repeat(7, 1fr);

  gap: 16px;
}

.calendar__empty {
  aspect-ratio: 1;
}

.calendar__day {
  position: relative;

  aspect-ratio: 1;

  border-radius: 18px;

  border: 1px solid rgba(255,255,255,.08);

  background: transparent;

  color: white;

  cursor: pointer;

  transition: .25s;

  display: flex;
  justify-content: center;
  align-items: flex-start;

  padding-top: 18px;
}

.calendar__day:hover {
  border-color: var(--color-main-accent);

  transform: translateY(-4px);
}

.calendar__number {
  font-size: 38px;
  font-weight: 600;
}

.calendar__badge {
  position: absolute;

  bottom: 16px;
  left: 50%;

  transform: translateX(-50%);

  width: 34px;
  height: 34px;

  border-radius: 50%;

  background: var(--color-main-accent);
  color: black;

  display: flex;
  justify-content: center;
  align-items: center;

  font-weight: 700;
}

.calendar__day--selected {
  background: rgba(214, 174, 64, .15);

  border: 2px solid var(--color-main-accent);
}

.calendar__day--today {
  box-shadow: inset 0 0 0 2px var(--color-main-accent);
}

@media (max-width:900px){

.calendar{
    padding:24px;
}

.calendar__grid{
    gap:10px;
}

.calendar__weekdays{
    gap:10px;
}

.calendar__number{
    font-size:26px;
}

.calendar__badge{
    width:26px;
    height:26px;
    font-size:13px;
}

}
</style>