<script setup>
import Map from './Map.vue'
import { onMounted, ref, inject, computed } from 'vue'

const pageRef = ref(null)
const wsManager = inject('wsManager', null)

// Computed properties for time and turn display
const timeToNextStage = computed(() => {
  return wsManager?.gameState?.getFormattedTimeToNextStage() || '--:--'
})

const turnInfo = computed(() => {
  const step = wsManager?.gameState?.state?.session?.step || 0
  const maxSteps = wsManager?.gameState?.state?.session?.max_steps || 0
  return `${step}/${maxSteps}`
})

onMounted(() => {
  // Component mounted
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
        <div>До конца этапа {{ timeToNextStage }}</div>
        <div>{{ turnInfo }}</div>
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
