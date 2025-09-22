<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { gsap } from 'gsap'
import { animationConfig, getDuration, getDelay, logTimelineDuration } from '../animationConfig.js'

const pageRef = ref(null)

function playEntranceAnimation() {
  // Set initial positions (elements start off-screen)
  gsap.set('#graphs', { x: -300, opacity: 0 })
  gsap.set('#by-money', { x: 200, y: -100, opacity: 0 })
  gsap.set('#by-rep', { x: 200, opacity: 0 })
  gsap.set('#by-level', { x: 200, y: 100, opacity: 0 })

  // Create entrance animation timeline
  const tl = gsap.timeline({ delay: getDelay(animationConfig.durations.delay) })
  
  tl.to('#graphs', { x: 0, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.smooth })
    .to('#by-money', { x: 0, y: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.mapBounce }, '-=0.4')
    .to('#by-rep', { x: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.mapBounce }, '-=0.5')
    .to('#by-level', { x: 0, y: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.mapBounce }, '-=0.5')

  logTimelineDuration(tl, 'Endgame', 'entrance')
}

function playExitAnimation() {
  const tl = gsap.timeline()
  
  tl.to('#by-level', { x: 150, y: 50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth })
    .to('#by-rep', { x: 150, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')
    .to('#by-money', { x: 150, y: -50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')
    .to('#graphs', { x: -200, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.2')

  logTimelineDuration(tl, 'Endgame', 'exit')
}

onMounted(() => {
  playEntranceAnimation()
  
  // Listen for exit animation trigger
  pageRef.value?.addEventListener('triggerExit', playExitAnimation)
})

onUnmounted(() => {
  pageRef.value?.removeEventListener('triggerExit', playExitAnimation)
})
</script>

<template>
  <div id="page" ref="pageRef">
    <div id="column-left">
      <div id="graphs">

      </div>
    </div>

    <div id="column-right">
      <div id="by-money" class="element">
      </div>
      <div id="by-rep" class="element">
      </div>
      <div id="by-level" class="element">
      </div>
    </div>
  </div>

</template>

<style scoped>
#page {
  display: flex;
  align-items: stretch;

  margin: 0;
  padding: var(--spacing-sm);

  gap: var(--spacing-lg);
  width: calc(100vw - var(--spacing-sm) * 2);
  height: calc(100vh - var(--spacing-sm) * 2);
}

#column-left {
  flex: 3;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

#column-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--spacing-sm);
}


#column-right-header {
  display: flex;
  flex-direction: row;
}

#graphs {
  flex: 1;
  background: lightgray;
  border-radius: var(--border-radius);
  border: var(--border-width) solid gray;
}


.element {
  flex: 1;
  padding: var(--spacing-sm);
  background: lightgray;
  border-radius: var(--border-radius);
  border: var(--border-width) solid gray;
}

.column {
  flex: 1;
  padding: var(--spacing-sm);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.list-item {
  background-color: lightgray;
  color: black;
  border: var(--border-width) solid gray;
  border-radius: var(--border-radius);
  padding: var(--spacing-sm) 0;
  font-size: var(--text-md);

  text-align: center;
  flex: 1;
}

#map-title {
  font-size: var(--text-xl);
  font-weight: 600;
  text-align: center;
  margin: var(--spacing-sm) 0;
  padding: var(--spacing-sm) 0;
  width: 90%;
}

#timer {
  font-size: var(--text-lg);
  text-align: center;
  margin: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
  width: 90%;
  background: lightgray;
  border-radius: var(--border-radius);
  border: var(--border-width) solid gray;
}
</style>
