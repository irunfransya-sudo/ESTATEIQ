import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './views/Home.vue'
import Catalog from './views/Catalog.vue'
import Detail from './views/Detail.vue'
import Analytics from './views/Analytics.vue'
import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import './style.css'

const routes = [
  { path: '/', component: Home },
  { path: '/catalog', component: Catalog },
  { path: '/property/:id', component: Detail },
  { path: '/analytics', component: Analytics },
  { path: '/login', component: Login },
  { path: '/dashboard', component: Dashboard },
]
const router = createRouter({ history: createWebHistory(), routes })
createApp(App).use(router).mount('#app')
