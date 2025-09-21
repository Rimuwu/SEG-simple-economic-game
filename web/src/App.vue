<script setup>
import { ref } from 'vue'
import Preparation from './components/Preparation.vue'
import Game from './components/Game.vue'
import Between from './components/Between.vue'
import AdminPanel from './components/AdminPanel.vue'

const currentView = ref('Game')
const showAdmin = ref(false)

function handleShow(view) {
  currentView.value = view
}

function handleMouseMove(e) {
  if (e.clientX < 32 && e.clientY < 32) {
    showAdmin.value = true
  }
}

function handleAdminLeave() {
  showAdmin.value = false
}
</script>

<template>
  <div @mousemove="handleMouseMove" style="position: relative; min-height: 100vh;">
    <AdminPanel
      v-if="showAdmin"
      @show="handleShow"
      @mouseleave="handleAdminLeave"
      style="position: fixed; left: 0; top: 0; width: 320px; z-index: 1000;"/>
    <component :is="currentView === 'Preparation' ? Preparation : currentView === 'Between' ? Between : Game" />
  </div>
</template>

<style scoped>
</style>
