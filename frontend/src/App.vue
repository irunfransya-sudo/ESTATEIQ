<template>
  <nav class="topbar">
    <router-link class="logo" to="/"><svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="4" y="8" width="10" height="22" rx="2" fill="#1e8c4a"/>
  <rect x="18" y="2" width="10" height="28" rx="2" fill="#16325c"/>
  <rect x="7" y="12" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="7" y="17" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="7" y="22" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="21" y="6" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="21" y="11" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="21" y="16" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="21" y="21" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="25" y="6" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="25" y="11" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="25" y="16" width="2" height="2" rx="0.5" fill="white"/>
  <rect x="25" y="21" width="2" height="2" rx="0.5" fill="white"/>
</svg> EstateIQ</router-link>
    <div class="links">
      <router-link to="/catalog">Каталог</router-link>
      <router-link to="/analytics">Аналітика</router-link>
      <router-link to="/dashboard">Кабінет</router-link>
      <router-link to="/login">Вхід</router-link>
    </div>
  </nav>
  <router-view />
</template>
