<template>
  <main class="page" v-if="property">
    <section class="detail">
      <img
        :src="property.image_url || fallback"
        alt="Фото об’єкта"
        class="detail-image"
      >

      <div class="card">
        <span class="badge">
          Smart Score: {{ property.smart_score }}/100
        </span>

        <h1>{{ property.title }}</h1>
        <h2>{{ property.price.toLocaleString() }} $</h2>
        <p>{{ property.description }}</p>

        <table class="table">
          <tbody>
            <tr>
              <td>Тип</td>
              <td>{{ property.property_type }}</td>
            </tr>
            <tr>
              <td>Район</td>
              <td>{{ property.district }}</td>
            </tr>
            <tr>
              <td>Адреса</td>
              <td>{{ property.address }}</td>
            </tr>
            <tr>
              <td>Площа</td>
              <td>{{ property.area }} м²</td>
            </tr>
            <tr>
              <td>Ціна за м²</td>
              <td>{{ property.price_per_m2 }} $</td>
            </tr>
            <tr>
              <td>Кімнат</td>
              <td>{{ property.rooms }}</td>
            </tr>
            <tr>
              <td>Поверх</td>
              <td>{{ property.floor }} / {{ property.total_floors }}</td>
            </tr>
            <tr>
              <td>Стан</td>
              <td>{{ property.condition }}</td>
            </tr>
            <tr>
              <td>Прогнозована ціна</td>
              <td>{{ property.predicted_price.toLocaleString() }} $</td>
            </tr>
          </tbody>
        </table>

        <div class="request-box">
          <input
            v-model="phone"
            placeholder="Ваш номер телефону"
            class="input"
          >

          <textarea
            v-model="comment"
            placeholder="Коментар до заявки"
          ></textarea>

          <button class="btn" @click="createRequest">
            Подати заявку
          </button>

          <p v-if="message" class="success">
            {{ message }}
          </p>
        </div>
      </div>
    </section>
  </main>

  <main class="page" v-else>
    <h2>Завантаження...</h2>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()

const property = ref(null)
const comment = ref('')
const phone = ref('')
const message = ref('')

const fallback = 'https://images.unsplash.com/photo-1560518883-ce09059eeffa'

async function load() {
  try {
    const { data } = await api.get(`/properties/${route.params.id}`)
    property.value = data
  } catch (e) {
    console.log(e)
    message.value = 'Помилка завантаження об’єкта'
  }
}

async function createRequest() {
  const token = localStorage.getItem('token')

  if (!token) {
    message.value = 'Спочатку увійдіть у систему як покупець'
    return
  }

  try {
    await api.post(
      '/requests/',
      {
        property_id: property.value.id,
        comment: comment.value,
        phone: phone.value
      },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    message.value = 'Заявку успішно створено'
    comment.value = ''
    phone.value = ''

  } catch (e) {
    console.log(e.response?.data || e)
    message.value = e.response?.data?.detail || 'Помилка створення заявки'
  }
}

onMounted(load)
</script>

<style scoped>
.detail {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  align-items: start;
}

.detail-image {
  width: 100%;
  border-radius: 24px;
  object-fit: cover;
}

.card {
  background: white;
  padding: 28px;
  border-radius: 24px;
}

.badge {
  display: inline-block;
  background: #32eb25;
  color: white;
  padding: 8px 14px;
  border-radius: 12px;
  margin-bottom: 16px;
  font-weight: 700;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 18px;
}

.table td {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.request-box {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input,
textarea {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid #cbd5e1;
  font-size: 16px;
}

textarea {
  min-height: 120px;
}

.btn {
  width: 240px;
  background: #1e8c4a;
  color: white;
  border: none;
  padding: 18px;
  border-radius: 18px;
  font-size: 20px;
  font-weight: 700;
  cursor: pointer;
}

.success {
  background: #dcfce7;
  border: 1px solid #86efac;
  padding: 18px;
  border-radius: 18px;
  font-size: 18px;
}

@media(max-width:900px) {
  .detail {
    grid-template-columns: 1fr;
  }
}
</style>
