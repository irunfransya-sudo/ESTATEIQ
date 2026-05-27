<template>
  <main class="page">
    <div class="card" style="max-width:520px;margin:auto">
      <h1>Вхід до системи</h1>
      <p class="muted">Тестові акаунти: buyer@example.com / buyer123 або analyst@example.com / analyst123</p>
      <input class="input" v-model="email" placeholder="Email"><br><br>
      <input class="input" v-model="password" type="password" placeholder="Пароль"><br><br>
      <button class="btn" @click="login">Увійти</button>
      <p v-if="message" class="success">{{ message }}</p>
    </div>
  </main>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
const router = useRouter(); const email=ref('buyer@example.com'); const password=ref('buyer123'); const message=ref('')
async function login(){
  try { const {data}=await api.post('/auth/login',{email:email.value,password:password.value}); localStorage.setItem('token',data.access_token); localStorage.setItem('user',JSON.stringify(data.user)); message.value='Вхід виконано'; router.push('/dashboard') }
  catch(e){ message.value='Помилка входу' }
}
</script>
