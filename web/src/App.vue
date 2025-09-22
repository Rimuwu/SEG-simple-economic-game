<script setup>
import { ref, reactive, provide } from 'vue'
// Shared map state for singleton Map
const mapState = reactive({
  tiles: Array.from({ length: 49 }, (_, i) => ({
    id: `t-${i}`,
    label: String.fromCharCode(65 + (i % 7)) + (Math.floor(i / 7) + 1)
  }))
})
provide('mapState', mapState)
import Preparation from './components/Preparation.vue'
import Game from './components/Game.vue'
import Between from './components/Between.vue'
import Endgame from './components/Endgame.vue'
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
    <component
      :is="
        currentView === 'Preparation' ? Preparation :
        currentView === 'Between' ? Between :
        currentView === 'Endgame' ? Endgame :
        Game
      "
    />
  </div>
</template>

<style scoped>
</style>
