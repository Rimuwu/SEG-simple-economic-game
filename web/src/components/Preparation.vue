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
    wsManager.startPolling(5000)
  }
})

/**
 * Lifecycle hook: runs on component unmount.
 * Cleans up event listeners and stops company polling.
 */
onUnmounted(() => {
  pageRef.value?.removeEventListener('triggerExit', playExitAnimation)
  if (wsManager) {
    wsManager.stopPolling()
    window.removeEventListener('companies-updated', handleCompaniesUpdated)
  }
})
</script>

<template>
  <!--
    Preparation page layout.
    Left column: title, map, session key.
    Right columns: alternating company slots (left/right).
  -->
  <div id="page" ref="pageRef">
    <div id="column-left">
      <div id="title">
        Этап подготовки
      </div>
      <!-- Game map grid -->
      <Map />
      <div id="session-key">
        {{ wsManager.session_id }}
      </div>
    </div>
    <div id="column-right">
      <!-- Left company column -->
      <div id="list-col-left" class="column">
        <div v-for="n in 7" :key="'left-' + n" class="list-item" :id="'item-left-' + n">
          <template v-if="getCompanyForSlot(n, true)">
            <strong>{{ getCompanyForSlot(n, true).name }}</strong><br/>
            Баланс: {{ getCompanyForSlot(n, true).balance }} | Реп: {{ getCompanyForSlot(n, true).reputation }}
          </template>
          <template v-else>
            —
          </template>
        </div>
      </div>
      <!-- Right company column -->
      <div id="list-col-right" class="column">
        <div v-for="n in 7" :key="'right-' + n" class="list-item" :id="'item-right-' + n">
          <template v-if="getCompanyForSlot(n, false)">
            <strong>{{ getCompanyForSlot(n, false).name }}</strong><br/>
            Баланс: {{ getCompanyForSlot(n, false).balance }} | Реп: {{ getCompanyForSlot(n, false).reputation }}
          </template>
          <template v-else>
            —
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/*
  Preparation page layout and animation styles.
  Includes flexbox columns, company slot styling, and animated transitions.
*/
#page {
  display: flex;
  margin: 0;
  padding: var(--spacing-sm);
  gap: var(--spacing-lg);
  width: calc(100vw - var(--spacing-sm) * 2);
  height: calc(100vh - var(--spacing-sm) * 2);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

#column-left {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
}

#column-right {
  flex: 1;
  display: flex;
}

.column {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin: var(--spacing-sm);
}

.list-item {
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  border: var(--border-width) solid rgba(255, 255, 255, 0.3);
  border-radius: var(--border-radius);
  padding: var(--spacing-sm);
  font-size: var(--text-md);
  text-align: center;
  flex: 1;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
  /* Initial state for animation */
  transform: translateY(20px);
  opacity: 0;
}

.list-item:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
}

#title,
#session-key {
  font-size: var(--text-xl);
  font-weight: 700;
  text-align: center;
  margin: var(--spacing-sm) 0;
  padding: var(--spacing-sm) 0;
  width: 90%;
  color: white;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

#start-btn:hover,
#session-key:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
