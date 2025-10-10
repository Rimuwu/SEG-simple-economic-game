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

const AUTHORS = import.meta.env.VITE_AUTHORS;

onMounted(() => {
  playEntranceAnimation()
  
  // Listen for exit animation trigger
  pageRef.value?.addEventListener('triggerExit', playExitAnimation)

  document.getElementById("authors").innerHTML = AUTHORS.split("/").join("<br/>");
})

onUnmounted(() => {
  pageRef.value?.removeEventListener('triggerExit', playExitAnimation)
})

</script>

<template>
  <div id="page" ref="pageRef">
    
    <div id="column-left">
      <p id="title">Победители</p>
      <div id="by-money" class="element">
        <p class="title">по капиталу</p>
        <p class="name">супер крутая компания номер 1</p>
      </div>
      <div id="by-rep" class="element">
        <p class="title">по репутации</p>
        <p class="name">супер крутая компания номер 1</p>
      </div>
      <div id="by-level" class="element">
        <p class="title">по экономическому уровню</p>
        <p class="name">супер крутая компания номер 1</p>
      </div>
    </div>

    <div id="column-right">
      <p>
        Спасибо за игру в SEG.<br/><br/>
        Игра создана и разработана по авторской идеи и без использования потусторонних сил.<br/><br/>
        Создатели:<br/>
        <span id="authors"></span>
      </p>
    </div>
  </div>

</template>

<style scoped>
#page {
  display: flex;
  align-items: stretch;

  margin: 0;
  padding: 0;

  width: 100%;
  height: 100vh;

  background: #0C9273;
}

#column-left {
  flex: 3;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #0C9273;
  gap: 36px;
}

#column-right {
  flex: 1;
  display: flex;
  flex-direction: column;

  background: #0C6892;

  font-size: 4rem;
  color: white;
  text-align: center;
  justify-content: center;
  line-height: 1.5;
}

#title {
  color: white;
  font-size: 6rem;
  margin: 0;
}

.element {
  margin: 0;
  padding: 10px;
  color: white;
  text-align: center;
  background: #0C6892;
  width: 90%;
}

.title {
  font-family: "Ubuntu Mono", monospace;
  font-size: 4rem;
  text-transform: uppercase;
}
.name {
  font-size: 5rem;
}
</style>
