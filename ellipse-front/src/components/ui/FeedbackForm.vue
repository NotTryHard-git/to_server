<script setup>
import { ref } from 'vue'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

defineProps({
  submitLabel: {
    type: String,
    default: 'Отправить сообщение',
  },
  successMessage: {
    type: String,
    default: 'Спасибо! Ваше сообщение отправлено, мы скоро свяжемся с вами.',
  },
})

const emit = defineEmits(['submit'])

const form = ref({
  name: '',
  contact: '',
  message: '',
})

const isConsentGiven = ref(false)
const isSubmitted = ref(false)

// TODO: подключить реальную отправку формы на backend, когда он появится
function handleSubmit() {
  if (!isConsentGiven.value) return

  emit('submit', { ...form.value })
  isSubmitted.value = true
}
</script>

<template>
  <form class="feedback-form" @submit.prevent="handleSubmit">
    <BaseInput v-model="form.name" color="pink" size="md" placeholder="Ваше имя" />
    <BaseInput v-model="form.contact" color="pink" size="md" placeholder="Телефон или email" />
    <textarea
      v-model="form.message"
      class="feedback-form__textarea"
      placeholder="Ваше сообщение"
      rows="5"
    />

    <label class="feedback-form__consent">
      <input v-model="isConsentGiven" type="checkbox" required />
      <!-- TODO: заменить на реальную страницу политики обработки данных, когда она появится -->
      Я согласен(на) на <RouterLink to="/about">обработку персональных данных</RouterLink>
    </label>

    <BaseButton
      type="submit"
      color="accent"
      size="lg"
      shape="pill"
      class="feedback-form__submit"
      :disabled="!isConsentGiven"
    >
      {{ submitLabel }}
    </BaseButton>

    <p v-if="isSubmitted" class="feedback-form__status">
      {{ successMessage }}
    </p>
  </form>
</template>

<style scoped>
.feedback-form {
  max-width: 560px;
  margin: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.feedback-form__textarea {
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
  background-color: var(--color-main-bg);
  color: var(--color-main-text);
  border: 1px solid var(--color-main-accent);
  border-radius: 4px;
  padding: 10px 14px;
  font-family: inherit;
  font-size: 16px;
}

.feedback-form__consent {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.75);
  cursor: pointer;
}

.feedback-form__consent input {
  margin-top: 3px;
  flex-shrink: 0;
  accent-color: var(--color-main-accent);
}

.feedback-form__consent a {
  color: var(--color-header-footer-accent);
}

.feedback-form__submit {
  align-self: center;
  margin-top: 8px;
}

.feedback-form__status {
  text-align: center;
  color: var(--color-header-footer-accent);
  font-size: 15px;
}
</style>