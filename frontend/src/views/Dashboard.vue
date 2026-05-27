<template>
  <main class="page">
    <h1>Особистий кабінет</h1>

    <div v-if="!user" class="warning">
      Увійдіть у систему, щоб бачити заявки та керувати об’єктами.
    </div>

    <div v-else>
      <p class="card">
        <b>{{ user.full_name }}</b>
        · роль: {{ user.role }}
      </p>

      <section class="card">
        <h2>Заявки</h2>

        <table class="table">
          <thead>
            <tr>
              <th>Об’єкт</th>
              <th>Телефон</th>
              <th>Статус</th>
              <th>Коментар</th>
              <th>Дія</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="r in requests" :key="r.id">
              <td>{{ r.property.title }}</td>
              <td>{{ r.phone || 'не вказано' }}</td>
              <td>{{ r.status }}</td>
              <td>{{ r.comment || '—' }}</td>
              <td>
                <button class="delete-btn" @click="deleteRequest(r.id)">
                  Видалити
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-if="requests.length === 0" class="empty">
          Заявок поки немає.
        </p>
      </section>

      <section
        class="card"
        v-if="user.role !== 'buyer'"
        style="margin-top:20px"
      >
        <h2>Додати об’єкт нерухомості</h2>

        <div class="filters">
          <input class="input" v-model="form.title" placeholder="Назва">

          <select v-model="form.property_type">
            <option>квартира</option>
            <option>будинок</option>
            <option>комерційна</option>
          </select>

          <input class="input" v-model="form.district" placeholder="Район">
          <input class="input" v-model="form.address" placeholder="Адреса">
          <input class="input" v-model.number="form.price" placeholder="Ціна">
          <input class="input" v-model.number="form.area" placeholder="Площа">
          <input class="input" v-model.number="form.rooms" placeholder="Кімнат">
          <input class="input" v-model.number="form.floor" placeholder="Поверх">
          <input class="input" v-model.number="form.total_floors" placeholder="Усього поверхів">
          <input class="input" v-model.number="form.year_built" placeholder="Рік побудови">
          <input class="input" v-model="form.condition" placeholder="Стан">
          <input class="input" v-model="form.image_url" placeholder="Посилання на фото">
        </div>

        <textarea v-model="form.description" placeholder="Опис"></textarea>

        <br><br>

        <button class="btn" @click="addProperty">
          Додати
        </button>
      </section>

      <section
        class="card"
        v-if="user.role !== 'buyer'"
        style="margin-top:20px"
      >
        <h2>Наявні об’єкти нерухомості</h2>

        <table class="table">
          <thead>
            <tr>
              <th>Назва</th>
              <th>Тип</th>
              <th>Район</th>
              <th>Ціна</th>
              <th>Дія</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="p in properties" :key="p.id">
              <td>{{ p.title }}</td>
              <td>{{ p.property_type }}</td>
              <td>{{ p.district }}</td>
              <td>{{ p.price.toLocaleString() }} $</td>
              <td>
                <button class="delete-btn" @click="deleteProperty(p.id)">
                  Видалити
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <p v-if="properties.length === 0" class="empty">
          Об’єктів поки немає.
        </p>
      </section>

      <p v-if="msg" class="success">
        {{ msg }}
      </p>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

const requests = ref([])
const properties = ref([])
const msg = ref('')

const emptyForm = () => ({
  title: '',
  property_type: 'квартира',
  district: '',
  address: '',
  price: 0,
  area: 0,
  rooms: 1,
  floor: 1,
  total_floors: 1,
  year_built: 2020,
  condition: 'житловий стан',
  infrastructure_score: 7,
  demand_score: 7,
  latitude: 50.45,
  longitude: 30.52,
  image_url: '',
  description: ''
})

const form = ref(emptyForm())

function authHeaders() {
  const token = localStorage.getItem('token')

  return {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }
}

async function loadRequests() {
  const { data } = await api.get('/requests/', authHeaders())
  requests.value = data
}

async function loadProperties() {
  const { data } = await api.get('/properties/')
  properties.value = data
}

async function load() {
  if (!user.value) return

  try {
    await loadRequests()

    if (user.value.role !== 'buyer') {
      await loadProperties()
    }
  } catch (e) {
    console.log(e.response?.data || e)
    msg.value = 'Помилка завантаження даних'
  }
}

async function deleteRequest(id) {
  try {
    await api.delete(`/requests/${id}`, authHeaders())

    requests.value = requests.value.filter(r => r.id !== id)
    msg.value = 'Заявку видалено'
  } catch (e) {
    console.log(e.response?.data || e)
    msg.value = e.response?.data?.detail || 'Помилка видалення заявки'
  }
}

async function addProperty() {
  try {
    await api.post('/properties/', form.value, authHeaders())

    msg.value = 'Об’єкт додано'
    form.value = emptyForm()

    await loadProperties()
  } catch (e) {
    console.log(e.response?.data || e)
    msg.value = e.response?.data?.detail || 'Помилка додавання об’єкта'
  }
}

async function deleteProperty(id) {
  try {
    await api.delete(`/properties/${id}`, authHeaders())

    properties.value = properties.value.filter(p => p.id !== id)
    msg.value = 'Об’єкт видалено'
  } catch (e) {
    console.log(e.response?.data || e)
    msg.value = e.response?.data?.detail || 'Помилка видалення об’єкта'
  }
}

onMounted(load)
</script>

<style scoped>
.warning {
  background: #fef3c7;
  padding: 18px;
  border-radius: 18px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.table th,
.table td {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}

.delete-btn {
  background: #dc2626;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 12px;
  cursor: pointer;
}

.filters {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.input,
textarea,
select {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid #cbd5e1;
}

textarea {
  width: 100%;
  min-height: 120px;
  margin-top: 16px;
}

.btn {
  background: #1e8c4a;
  color: white;
  border: none;
  padding: 16px 22px;
  border-radius: 16px;
  cursor: pointer;
  font-weight: 700;
}

.success {
  margin-top: 16px;
  background: #dcfce7;
  padding: 16px;
  border-radius: 16px;
}

.card {
  background: white;
  padding: 24px;
  border-radius: 24px;
  margin-top: 20px;
}

.empty {
  color: #64748b;
  margin-top: 16px;
}
</style>