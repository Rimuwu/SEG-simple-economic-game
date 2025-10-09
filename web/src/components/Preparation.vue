<script setup>
import './mapScripts.js'
import Map from './Map.vue'
import { onMounted, onUnmounted, ref, inject, reactive } from 'vue'
import { gsap } from 'gsap'
import { animationConfig, getDuration, getDelay, logTimelineDuration } from '../animationConfig.js'

/**
 * Ref to the root page container for animation and event handling.
 * @type {import('vue').Ref<HTMLElement>}
 */
const pageRef = ref(null)
/**
 * Injected WebSocketManager instance for session and company data.
 * @type {WebSocketManager}
 */
const wsManager = inject('wsManager', null)

/**
 * Reactive state for the list of companies displayed in the columns.
 */
const companiesState = reactive({ list: [] })

/**
 * Handles updates to the companies list from polling events.
 * @param {CustomEvent} e
 */
function handleCompaniesUpdated(e) {
  if (e && e.detail && Array.isArray(e.detail.companies)) {
    companiesState.list = e.detail.companies
  }
}

/**
 * Returns the company object for a given slot in the left/right columns.
 * @param {number} index - 1-based slot number in the column
 * @param {boolean} isLeft - True for left column, false for right
 * @returns {Object|null} Company object or null if no company
 */
function getCompanyForSlot(index, isLeft) {
  const companies = companiesState.list
  const globalIdx = (index - 1) * 2 + (isLeft ? 0 : 1)
  if (globalIdx < companies.length) return companies[globalIdx]
  return null
}

/**
 * Plays the entrance animation for the preparation page using GSAP.
 */
function playEntranceAnimation() {
  gsap.set('#start-btn', { y: -100, opacity: 0 })
  gsap.set('#session-key', { y: 100, opacity: 0 })
  gsap.set('#column-right .column:first-child', { x: -200, opacity: 0 })
  gsap.set('#column-right .column:last-child', { x: 200, opacity: 0 })
  gsap.set('#map', { scale: 0.5, opacity: 0 })

  const tl = gsap.timeline({ delay: getDelay(animationConfig.durations.delay) })
  tl.to('#start-btn', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.bounce })
    .to('#map', { scale: 1, opacity: 1, duration: getDuration(animationConfig.durations.map), ease: animationConfig.ease.mapBounce }, '-=0.4')
    .to('#session-key', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.bounce }, '-=0.6')
    .to('#column-right .column:first-child', { x: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.5')
    .to('#column-right .column:last-child', { x: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.6')
    .to('.list-item', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.listItem), ease: animationConfig.ease.smooth, stagger: getDuration(animationConfig.durations.stagger) }, '-=0.3')
  logTimelineDuration(tl, 'Preparation', 'entrance')
}

/**
 * Plays the exit animation for the preparation page using GSAP.
 */
function playExitAnimation() {
  const tl = gsap.timeline()
  tl.to('.list-item', { y: 20, opacity: 0, duration: getDuration(animationConfig.durations.listItemExit), ease: animationConfig.ease.exitSmooth, stagger: getDuration(0.02) })
    .to('#column-right .column:first-child', { x: -100, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.1')
    .to('#column-right .column:last-child', { x: 100, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.4')
    .to('#start-btn', { y: -50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')
    .to('#session-key', { y: 50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.4')
    .to('#map', { scale: 0.8, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')
  logTimelineDuration(tl, 'Preparation', 'exit')
}

/**
 * Lifecycle hook: runs on component mount.
 * Sets up entrance animation, exit event listener, and starts company polling.
 */
onMounted(() => {
  playEntranceAnimation()
  pageRef.value?.addEventListener('triggerExit', playExitAnimation)
  if (wsManager) {
    window.addEventListener('companies-updated', handleCompaniesUpdated)
    wsManager.startCompaniesPolling(5000)
  }
})

/**
 * Lifecycle hook: runs on component unmount.
 * Cleans up event listeners and stops company polling.
 */
onUnmounted(() => {
  pageRef.value?.removeEventListener('triggerExit', playExitAnimation)
  if (wsManager) {
    wsManager.stopCompaniesPolling()
    window.removeEventListener('companies-updated', handleCompaniesUpdated)
  }
})

wsManager.session_id = "AFRIKA";
</script>

<template>
  <!--
    Preparation page layout.
    Left column: title, map, session key.
    Right columns: alternating company slots (left/right).
  -->
  <div id="page" ref="pageRef">
    <div class="left">
      <Map class="map" />
      <div class="footer">
        <span>@sneg_gamebot</span>
        <span>/</span>
        <span>{{ wsManager.session_id }}</span>
      </div>
    </div>
    <div class="right">
      <div class="grid">
        <div v-for="n in 10" :key="'item-' + n" class="item" :id="'item-' + n">
          <p class="title">Название крутой компании с длинным названием</p>  
          <p class="users">лягушка лягушка лягушка лягушка лягушка</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
#page {
  display: flex;
  height: 100vh;
  background-color: #C67D1D;
  font-family: "Inter", sans-serif;
  padding: 0;
  margin: 0;
}

.left,
.right {
  width: 50%;
  padding: 40px;
}


.left {
  background-color: #12488E;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.right {
  background-color: #C67D1D;

  color: black;
  padding: 90px 50px;
}

.grid {
  margin: auto;
  display: grid;
  padding: 0; margin: 0;

  width: 100%;
  height: 100%;

  justify-items: stretch;
  align-items: center;
  align-content: space-between;
  justify-content: space-between;

  grid-template-columns: 47.5% 47.5%;
}

.item {
  background: white;
  padding: 10px;

  font-family: "Ubuntu Mono", monospace;

  text-align: center;
}

.title {
  font-size: 2.5rem;
  margin: 0;
  text-transform: uppercase;
  margin-bottom: 20px;
}

.users {
  text-transform: lowercase;
  font-size: 2rem;
  margin: 0;
  opacity: 0.75;
}

.footer {
  width: 90%;

  background: #C67D1D;
  padding: 25px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;

  font-family: "Ubuntu Mono", monospace;
  font-weight: normal;
  font-size: 4rem;

  color: white;
}

.map {
  width: 90%;
  margin: 0; padding: 0;
}
</style>
