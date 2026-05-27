<template>
  <main class="page">
    <h1>Аналітичний дашборд ринку нерухомості</h1>
    <div class="stats" v-if="summary">
      <div class="stat"><span>Кількість об’єктів</span><br><strong>{{ summary.total_properties }}</strong></div>
      <div class="stat"><span>Середня ціна</span><br><strong>{{ summary.average_price.toLocaleString() }} $</strong></div>
      <div class="stat"><span>Середня ціна за м²</span><br><strong>{{ summary.average_price_per_m2 }} $</strong></div>
    </div>
    <section class="grid" v-if="summary">
      <div class="card">
        <h2>Середня ціна за м² по районах</h2>
        <table class="table"><thead><tr><th>Район</th><th>К-сть</th><th>$/м²</th></tr></thead><tbody><tr v-for="d in summary.districts"><td>{{d.district}}</td><td>{{d.count}}</td><td>{{d.avg_price_per_m2}}</td></tr></tbody></table>
      </div>
      <div class="card">
        <h2>Структура за типами</h2>
        <table class="table"><thead><tr><th>Тип</th><th>К-сть</th><th>Сер. ціна</th></tr></thead><tbody><tr v-for="t in summary.types"><td>{{t.type}}</td><td>{{t.count}}</td><td>{{t.avg_price.toLocaleString()}} $</td></tr></tbody></table>
      </div>
      <div class="card">
        <h2>ТОП інвестиційно привабливих об’єктів</h2>
        <table class="table"><thead><tr><th>Об’єкт</th><th>Район</th><th>Індекс</th></tr></thead><tbody><tr v-for="p in summary.top_investment"><td>{{p.title}}</td><td>{{p.district}}</td><td>{{p.investment_index}}</td></tr></tbody></table>
      </div>
    </section>
  </main>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
const summary = ref(null)
onMounted(async()=>{ const {data}=await api.get('/analytics/summary'); summary.value=data })
</script>
