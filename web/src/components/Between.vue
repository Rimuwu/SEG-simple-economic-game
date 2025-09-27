<script setup>
import Map from './Map.vue'
import { onMounted, onUnmounted, ref } from 'vue'
import { gsap } from 'gsap'
import { animationConfig, getDuration, getDelay } from '../animationConfig.js'

const pageRef = ref(null)

function playEntranceAnimation() {
  // Set initial positions (elements start off-screen)
  gsap.set('#map-title', { y: -100, opacity: 0 })
  gsap.set('#round-info', { y: 100, opacity: 0 })
  gsap.set('#column-right-header', { y: -80, opacity: 0 })
  gsap.set('#column-right-content-top .column:first-child', { x: -200, opacity: 0 })
  gsap.set('#column-right-content-top .column:last-child', { x: 200, opacity: 0 })
  gsap.set('#column-right-content-bottom', { y: 150, opacity: 0 })

  gsap.set('#map', { scale: 0.5, opacity: 0 })


  // Create entrance animation timeline
  const tl = gsap.timeline({ delay: getDelay(animationConfig.durations.delay) })

  tl.to('#map-title', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.bounce })
    .to('#map', { scale: 1, opacity: 1, duration: getDuration(animationConfig.durations.map), ease: animationConfig.ease.mapBounce }, '-=0.4')
    .to('#round-info', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.bounce }, '-=0.6')
    .to('#column-right-header', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.5')
    .to('#column-right-content-top .column:first-child', { x: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.4')
    .to('#column-right-content-top .column:last-child', { x: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.6')
    .to('#column-right-content-bottom', { y: 0, opacity: 1, duration: getDuration(0.6), ease: animationConfig.ease.smooth }, '-=0.4')
    .to('.list-item', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.listItem), ease: animationConfig.ease.smooth, stagger: getDuration(animationConfig.durations.stagger) }, '-=0.3')
}

function playExitAnimation() {
  const tl = gsap.timeline()

  tl.to('.list-item', { y: 20, opacity: 0, duration: getDuration(animationConfig.durations.listItemExit), ease: animationConfig.ease.exitSmooth, stagger: getDuration(0.02) })
    .to('#column-right-content-bottom', { y: 75, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.1')
    .to('#column-right-content-top .column:first-child', { x: -100, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')
    .to('#column-right-content-top .column:last-child', { x: 100, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.4')
    .to('#column-right-header', { y: -40, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')
    .to('#map-title', { y: -50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.4')
    .to('#round-info', { y: 50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.4')
    .to('#map', { scale: 0.8, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')
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
      <div id="map-title">
        Карта мира
      </div>

      <Map />

      <div id="round-info">
        <div id="timer">
          Время до конца этапа: 00:00
        </div>
        <div id="teams-ready">
          4/10
        </div>
      </div>

    </div>

    <div id="column-right">
      <div id="column-right-header">
        <p class="column-title"> Лучшие Результаты </p>
        <p class="column-title"> Топ компании </p>
      </div>
      <div id="column-right-content-top">
        <div id="list-col-left" class="column">
          <div v-for="n in 3" :key="n" class="list-item" :id="'demand-' + n">
            Результат {{ n }}
          </div>
        </div>
        <div id="list-col-right" class="column">
          <div v-for="n in 3" :key="n" class="list-item" :id="'stock-' + n">
            Топовая компания {{ n }}
          </div>
        </div>
      </div>
      <div id="column-right-content-bottom">
        Информация о событии
      </div>
    </div>
  </div>

</template>

<style scoped>
#page {
  display: flex;
  margin: 0;
  padding: var(--spacing-sm);

  gap: var(--spacing-lg);
  width: calc(100vw - var(--spacing-sm) * 2);
  height: calc(100vh - var(--spacing-sm) * 2);
}

#column-left {
  flex: 1;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
}

#column-right {
  flex: 1;
  display: flex;
  flex-direction: column;
}

#column-right-content-top {
  flex: 1;
  display: flex;
  gap: var(--spacing-sm);
}

#column-right-content-bottom {
  min-height: 100px;
  background-color: lightgray;
  color: black;
  border: var(--border-width) solid gray;
  border-radius: var(--border-radius);
  padding: var(--spacing-sm) 0;
  font-size: var(--text-md);

  text-align: center;
  margin-top: var(--spacing-sm);
}

#column-right-header {
  display: flex;
  flex-direction: row;
}

.column-title {
  flex: 1;
  font-size: var(--text-xl);
  font-weight: 600;
  text-align: center;
  margin-bottom: var(--spacing-sm);
}

.column {
  flex: 1;
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
  /* Initial state for animation */
  transform: translateY(20px);
  opacity: 0;
}

#map-title {
  font-size: var(--text-xl);
  font-weight: 600;
  text-align: center;
  margin: var(--spacing-sm) 0;
  padding: var(--spacing-sm) 0;
  width: 90%;
}

#round-info {
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  gap: var(--spacing-sm);
}

#timer,
#teams-ready {
  font-size: var(--text-lg);
  text-align: center;
  justify-content: center;

  padding: var(--spacing-sm) var(--spacing-sm);
  background: lightgray;
  border-radius: var(--border-radius);
  border: var(--border-width) solid gray;
}


Map {
  margin: 0;
}
</style>
