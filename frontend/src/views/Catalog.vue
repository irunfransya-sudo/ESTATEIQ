<template>
  <main class="page">
    <h1>Каталог об’єктів нерухомості</h1>
    <div class="filters card">
      <select v-model="filters.type"><option value="">Тип</option><option>квартира</option><option>будинок</option><option>комерційна</option></select>
      <input class="input" v-model="filters.district" placeholder="Район">
      <input class="input" v-model="filters.min_price" placeholder="Ціна від">
      <input class="input" v-model="filters.max_price" placeholder="Ціна до">
      <input class="input" v-model="filters.rooms" placeholder="Кімнат">
      <button class="btn" @click="load">Застосувати</button>
    </div>
    <div class="grid">
      <article class="card property-card" v-for="p in properties" :key="p.id">
        <img :src="p.image_url || fallback" alt="Нерухомість">
        <div class="inside">
          <span class="badge">Smart Score: {{ p.smart_score }}/100</span>
          <h2>{{ p.title }}</h2>
          <p class="muted">{{ p.district }} · {{ p.area }} м² · {{ p.rooms }} кімн.</p>
          <h2>{{ Number(p.price).toLocaleString() }} $</h2>
          <p>{{ p.price_per_m2 }} $/м² · індекс інвестиційності {{ p.investment_index }}</p>
          <label><input type="checkbox" :value="p" v-model="selected"> Додати до порівняння</label><br><br>
          <router-link class="btn" :to="`/property/${p.id}`">Детальніше</router-link>
        </div>
      </article>
    </div>
    <section class="card compare" v-if="selected.length">
      <h2>Порівняння об’єктів</h2>
      <div class="compare-grid">
        <div class="warning" v-for="p in selected" :key="p.id">
          <b>{{ p.title }}</b><br>{{ p.price.toLocaleString() }} $<br>{{ p.area }} м²<br>Smart Score {{ p.smart_score }}<br>Прогноз {{ p.predicted_price.toLocaleString() }} $
        </div>
      </div>
    </section>
  </main>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
const fallback = 'https://images.unsplash.com/photo-1560518883-ce09059eeffa'
const properties = ref([])
const selected = ref([])
const filters = ref({ type:'', district:'', min_price:'', max_price:'', rooms:'' })
async function load(){
  const params = {}
  Object.entries(filters.value).forEach(([k,v]) => { if(v) params[k]=v })
  const {data} = await api.get('/properties/', { params })
  properties.value = data
}
onMounted(load)
</script>
