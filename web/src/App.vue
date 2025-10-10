globalThis.wsManager = wsManager
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
const currentView = ref('Endgame')
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
 * Changes the current view/page.
 * @param {string} view - The view name to show.
 */
function handleShow(view) {
  currentView.value = view
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
 * Triggers exit animation for the leaving component.
 * @param {HTMLElement} el
 */
function handleBeforeLeave(el) {
  const exitEvent = new CustomEvent('triggerExit')
  el.dispatchEvent(exitEvent)
}

/**
 * Placeholder for enter animation logic (handled in child components).
 * @param {HTMLElement} el
 */
function handleEnter(el) {
  // The enter animation is handled by each component's onMounted
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
    <!-- Page transition wrapper for animated navigation between views -->
    <Transition name="page" mode="out-in" @before-leave="handleBeforeLeave" @enter="handleEnter">
      <component :is="currentView === 'Introduction' ? Introduction :
          currentView === 'Preparation' ? Preparation :
            currentView === 'Between' ? Between :
              currentView === 'Endgame' ? Endgame :
                Game
        " :key="currentView" @navigateTo="handleShow" />
    </Transition>
  </div>
</template>

<style scoped>
/*
  Page transition styles for fade-in/fade-out between views.
*/
.page-enter-active {
  transition: opacity 0.1s ease;
}

.page-leave-active {
  transition: opacity 0.3s ease 0.5s;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
