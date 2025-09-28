<script setup>
import { ref, reactive, provide} from 'vue'

// Shared map state for singleton Map
const mapState = reactive({
  tiles: Array.from({ length: 49 }, (_, i) => ({
    id: `t-${i}`,
    label: String.fromCharCode(65 + (i % 7)) + (Math.floor(i / 7) + 1)
  }))
})
provide('mapState', mapState)

import Introduction from './components/Introduction.vue'
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

function handleBeforeLeave(el) {
  // Trigger exit animation for the leaving component
  const exitEvent = new CustomEvent('triggerExit')
  el.dispatchEvent(exitEvent)
}

function handleEnter(el) {
  // The enter animation is handled by each component's onMounted
}
</script>

<template>
  <div @mousemove="handleMouseMove" style="position: relative; min-height: 100vh; overflow: hidden;">
    <AdminPanel
      v-if="showAdmin"
      @show="handleShow"
      @mouseleave="handleAdminLeave"
      style="position: fixed; left: 0; top: 0; width: 320px; z-index: 1000;"/>
    <Transition 
      name="page" 
      mode="out-in"
      @before-leave="handleBeforeLeave"
      @enter="handleEnter"
    >
      <component
        :is="
          currentView === 'Introduction' ? Introduction :
          currentView === 'Preparation' ? Preparation :
          currentView === 'Between' ? Between :
          currentView === 'Endgame' ? Endgame :
          Game
        "
        :key="currentView"
      />
    </Transition>
  </div>
</template>

<style scoped>
.page-enter-active {
  transition: opacity 0.1s ease;
}

.page-leave-active {
  transition: opacity 0.3s ease;
}

.page-enter-from, .page-leave-to {
  opacity: 0;
}
</style>
