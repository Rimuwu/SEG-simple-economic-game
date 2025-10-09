<script setup>
import Map from './Map.vue'
import { onMounted, onUnmounted, ref } from 'vue'
import { gsap } from 'gsap'
import { animationConfig, getDuration, getDelay, logTimelineDuration } from '../animationConfig.js'

const pageRef = ref(null)

function playEntranceAnimation() {
  // Set initial positions (elements start off-screen)
  gsap.set('#map-title', { y: -100, opacity: 0 })
  gsap.set('#timer', { y: 100, opacity: 0 })
  gsap.set('#column-right-header', { y: -80, opacity: 0 })
  gsap.set('#column-right-content .column:first-child', { x: -200, opacity: 0 })
  gsap.set('#column-right-content .column:last-child', { x: 200, opacity: 0 })

  gsap.set('#map', { scale: 0.5, opacity: 0 })


  // Create entrance animation timeline
  const tl = gsap.timeline({ delay: getDelay(animationConfig.durations.delay) })

  tl.to('#map-title', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.bounce })
    .to('#map', { scale: 1, opacity: 1, duration: getDuration(animationConfig.durations.map), ease: animationConfig.ease.mapBounce }, '-=0.4')
    .to('#timer', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.bounce }, '-=0.6')
    .to('#column-right-header', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.5')
    .to('#column-right-content .column:first-child', { x: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.4')
    .to('#column-right-content .column:last-child', { x: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.6')
    .to('.list-item', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.listItem), ease: animationConfig.ease.smooth, stagger: getDuration(animationConfig.durations.stagger) }, '-=0.3')
  
  // Log total duration
  logTimelineDuration(tl, 'Game', 'entrance')
}

function playExitAnimation() {
  const tl = gsap.timeline()

  tl.to('.list-item', { y: 20, opacity: 0, duration: getDuration(animationConfig.durations.listItemExit), ease: animationConfig.ease.exitSmooth, stagger: getDuration(0.02) })
    .to('#column-right-content .column:first-child', { x: -100, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.1')
    .to('#column-right-content .column:last-child', { x: 100, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.4')
    .to('#column-right-header', { y: -40, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')
    .to('#map-title', { y: -50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.4')
    .to('#timer', { y: 50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.4')
    .to('#map', { scale: 0.8, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')

  logTimelineDuration(tl, 'Game', 'exit')
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
  <!--
    Preparation page layout.
    Left column: title, map, session key.
    Right columns: alternating company slots (left/right).
  -->
  <div id="page" ref="pageRef">
    <div class="left">
      <Map class="map" />
      <div class="footer">
        <div>До конца этапа 02:53</div>
        <div>4/5</div>
      </div>
    </div>
    <div class="right">
      <div class="grid">
        
        <div class="cities grid-item">
          <p class="title">ГОРОДА</p>
          <div class="content">
          <span>
Город А (ЛВ)<br/>
&nbsp;&nbsp;• Генератор<br/>
&nbsp;&nbsp;• Медикаменты<br/>
<br/>
Город Б (НЛ)<br/>
&nbsp;&nbsp;• Генератор<br/>
&nbsp;&nbsp;• Медикаменты<br/>
          </span>

          <span>
Город В (ПВ)<br/>
&nbsp;&nbsp;• Генератор<br/>
&nbsp;&nbsp;• Медикаменты<br/>
<br/>
Город Г (НП)<br/>
&nbsp;&nbsp;• Генератор<br/>
&nbsp;&nbsp;• Медикаменты<br/>
          </span>
          </div>
        </div>

        <div class="stock grid-item">
          <p class="title">БИРЖА</p>
          <div class="content">
            <span>Компания А выставила на продажу продукт Б</span>
            <span>Компания Б выкупила Х товара у компании С</span>
            <span>Компания А выставила на продажу продукт Б</span>
            <span>Компания А выставила на продажу продукт Б</span>
          </div>
        </div>
        <div class="upgrades grid-item">
          <p class="title">УЛУЧШЕНИЯ</p>
          <div class="content">
            <span>Компания А улучшила своё хранилище до уровня 2</span>
            <span>Компания А улучшила своё хранилище до уровня 2</span>
            <span>Компания А улучшила своё хранилище до уровня 2</span>
            <span>Компания А улучшила своё хранилище до уровня 2</span>
          </div>
        </div>
        <div class="contracts grid-item">
          <p class="title">КОНТРАКТЫ</p>
          <div class="content">
            <span>Компания А создала свободный контракт на Х продукта Б на С ходов</span>
            <span>Компания А создала свободный контракт на Х продукта Б на С ходов</span>
          </div>
        </div>


      </div>
    </div>
  </div>
</template>

<style scoped>
#page {
  display: flex;
  height: 100vh;
  background-color: #3D8C00;
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
  background-color: #3D8C00;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.right {
  background-color: #0C6892;

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
  grid-template-rows: 47.5% 47.5%;
}

.grid-item {
  width: 100%; height: 100%;
  /* background: #0f0; */
}

.content {
  font-size: 2.25rem;
  color: white;
  font-weight: 400;
}

.title {
  font-size: 4rem;
  margin: 0;
  margin-bottom: 10px;
  text-transform: uppercase;
  margin-bottom: 20px;
  color: white;
  text-align: center;
}

.cities .content {
  padding: 5px 10px;

  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  text-align: left;
  line-height: 1.5;
  background: #3D8C00;
}

.stock .content, .upgrades .content, .contracts .content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.stock span, .upgrades span, .contracts span {
  background: #3D8C00;
  padding: 5px 10px;
}

.footer {
  width: 90%;

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;

  font-weight: normal;
  font-size: 4rem;

  gap: 5%;

  color: white;
}

.footer div {
  background: #0C6792;
  padding: 25px 50px;
}

.map {
  width: 90%;
  margin: 0; padding: 0;
}
</style>
