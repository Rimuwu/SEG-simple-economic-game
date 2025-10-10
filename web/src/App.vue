<script setup>
import { ref, reactive, provide } from 'vue'

/**
 * Shared map state for singleton Map component.
 * Provided to child components for tile data access.
 */
const mapState = reactive({
  tiles: Array.from({ length: 49 }, (_, i) => ({
    id: `t-${i}`,
    label: String.fromCharCode(65 + (i % 7)) + (Math.floor(i / 7) + 1)
  }))
})
provide('mapState', mapState)

// Import all main page components
import Introduction from './components/Introduction.vue'
import Preparation from './components/Preparation.vue'
import Game from './components/Game.vue'
import Between from './components/Between.vue'
import Endgame from './components/Endgame.vue'
import AdminPanel from './components/AdminPanel.vue'
import OutputConsole from './components/OutputConsole.vue'

import { WebSocketManager } from './ws'

/**
 * Tracks the current view/page being displayed.
 * @type {import('vue').Ref<string>}
 */
const currentView = ref('Introduction')
/**
 * Controls visibility of the admin panel overlay.
 * @type {import('vue').Ref<boolean>}
 */
const showAdmin = ref(false)
/**
 * Ref to the OutputConsole component instance.
 * @type {import('vue').Ref<InstanceType<typeof OutputConsole>>}
 */
const outputConsole = ref(null)

/**
 * Controls the transition animation state
 * @type {import('vue').Ref<boolean>}
 */
const isTransitioning = ref(false)

/**
 * Changes the current view/page with transition animation.
 * @param {string} view - The view name to show.
 */
function handleShow(view) {
  isTransitioning.value = true
  
  // Wait for animation to reach middle (screen covered), then change view
  setTimeout(() => {
    currentView.value = view
  }, 400) // Half of the 800ms animation
  
  // Reset transitioning state after animation completes
  setTimeout(() => {
    isTransitioning.value = false
  }, 800)
}

/**
 * Shows the admin panel when mouse is in the top-left corner.
 * @param {MouseEvent} e
 */
function handleMouseMove(e) {
  if (e.clientX < 32 && e.clientY < 32) {
    showAdmin.value = true
  }
}

/**
 * Hides the admin panel overlay.
 */
function handleAdminLeave() {
  showAdmin.value = false
}

/**
 * WebSocketManager instance for global WebSocket communication.
 * Provided to child components and exposed globally.
 * @type {WebSocketManager}
 */
let wsManager = null
wsManager = new WebSocketManager('ws://localhost:8000/ws/connect', globalThis.console)
wsManager.connect()
globalThis.wsManager = wsManager

/**
 * Globally available function to refresh the map from session data.
 */
globalThis.refreshMap = () => {
  if (wsManager && wsManager.map) {
    wsManager.refreshMap()
    if (typeof window.log === 'function') {
      window.log('Global map refresh called')
    }
  } else {
    if (typeof window.error === 'function') {
      window.error('No map data available for global refresh')
    }
  }
}

provide('wsManager', wsManager)
provide('outputConsole', outputConsole)
</script>

<template>
  <!--
    Root application container.
    Handles mouse movement for admin panel reveal and hosts all main page components.
  -->
  <div @mousemove="handleMouseMove" style="position: relative; min-height: 100vh; overflow: hidden;">
    <!-- Admin panel overlay, shown when mouse is in top-left corner -->
    <AdminPanel v-if="showAdmin" @show="handleShow" @mouseleave="handleAdminLeave"
      style="position: fixed; left: 0; top: 0; width: 320px; z-index: 1000;" />
    <!-- Floating output console for logs and errors -->
    <OutputConsole ref="outputConsole" />

      <component :is="currentView === 'Introduction' ? Introduction :
          currentView === 'Preparation' ? Preparation :
            currentView === 'Between' ? Between :
              currentView === 'Endgame' ? Endgame :
                Game
        " :key="currentView" @navigateTo="handleShow" />

    <!-- Black transition overlay -->
    <div class="transition-overlay" :class="{ 'transitioning': isTransitioning }"></div>
  </div>
</template>

<style scoped>
/*
  Black rectangle sliding transition overlay.
*/
.transition-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #1E1E1E;
  z-index: 999;
  transform: translateY(-100%);
  pointer-events: none;
}

/*
  Page transition styles with sliding black rectangle effect.
  The overlay slides down from top, covers the screen, then slides down to bottom.
*/
.page-leave-active {
  transition-delay: 0s;
}

.page-enter-active {
  transition-delay: 0.4s;
}

/* Animation for the black overlay */
@keyframes slideDown {
  0% {
    transform: translateY(-100%);
  }
  50% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(100%);
  }
}

.transitioning {
  animation: slideDown 0.8s ease-in-out;
}
</style>
