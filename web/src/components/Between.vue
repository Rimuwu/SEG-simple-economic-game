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

        <div class="achievements grid-item">
          <p class="title">ДОСТИЖЕНИЯ</p>
          <div class="content">
            <section>
              <p class="name">Название крутой компании с длинным названием</p>
              <p class="desc">Заработано 100.000 монет за этап</p>
            </section>
            <section>
              <p class="name">Название крутой компании с длинным названием</p>
              <p class="desc">Заработано 100.000 монет за этап</p>
            </section>
            <section>
              <p class="name">Название крутой компании с длинным названием</p>
              <p class="desc">Заработано 100.000 монет за этап</p>
            </section>
          </div>
        </div>

        <div class="leaders grid-item">
          <p class="title">ЛИДЕРЫ</p>
          <div class="content">
            <section>
              <p class="name">ПО КАПИТАЛУ</p>
              <p class="desc">супер крутая компания номер 1</p>
            </section>
            <section>
              <p class="name">ПО РЕПУТАЦИИ</p>
              <p class="desc">супер крутая компания номер 1</p>
            </section>
            <section>
              <p class="name">ПО ЭКОНОМИЧЕСКОМУ УРОВНЮ</p>
              <p class="desc">супер крутая компания номер 1</p>
            </section>
          </div>
        </div>
      </div>

      <div class="events">
        <span>Нет события</span>
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
  display: flex;
  flex-direction: row;
  gap: 5%;
  padding: 0;
  margin: 0;

  width: 100%;

  justify-items: stretch;
  align-items: stretch;
  align-content: stretch;
  justify-content: space-between;
  margin-bottom: 40px;
}

.grid-item {
  width: 100%;
  height: 100%;
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

.achievements .content,
.leaders .content {
  display: flex;
  flex-direction: column;
  gap: 36px;
}

.achievements section,
.leaders section {
  background: #3D8C00;
  padding: 5px 10px;
}

.content {
  font-family: "Ubuntu Mono", monospace;
  text-align: center;
}

.name {
  font-size: 3rem;
  text-transform: uppercase;
  margin: 0;
}

.desc {
  opacity: 80%;
  margin: 0;

}

.events {
  font-size: 5rem;
  text-transform: uppercase;

  text-align: center;
  justify-content: center;

  padding: 40px 0;

  background-color: #3D8C00;

  color: white;
  font-family: "Ubuntu Mono", monospace;

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
  margin: 0;
  padding: 0;
}
</style>
