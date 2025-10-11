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

// Computed properties for cities
const city1 = computed(() => {
  return wsManager?.gameState?.getCityById(1) || null
})

const city2 = computed(() => {
  return wsManager?.gameState?.getCityById(2) || null
})

const city3 = computed(() => {
  return wsManager?.gameState?.getCityById(3) || null
})

const city4 = computed(() => {
  return wsManager?.gameState?.getCityById(4) || null
})

// Helper function to format city demands
const formatCityDemands = (city) => {
  if (!city || !city.demands) return []
  
  // Filter demands with amount > 0 and get only 2
  return Object.entries(city.demands)
    .filter(([_, demand]) => demand.amount > 0)
    .slice(0, 2)
    .map(([resourceId, demand]) => ({
      resourceId,
      amount: demand.amount,
      price: demand.price
    }))
}

// Helper function to get resource display name (you can customize this)
const getResourceName = (resourceId) => {
  const names = {
    'wood_planks': 'Доски',
    'fabric': 'Ткань',
    'metal_parts': 'Металл. детали',
    'oil_products': 'Нефтепродукты',
    'generator': 'Генератор',
    'medicine': 'Медикаменты',
    'machinery': 'Техника',
    'furniture': 'Мебель',
    'clothing': 'Одежда',
    'electronics': 'Электроника'
  }
  return names[resourceId] || resourceId
}

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
        
        <div class="cities grid-item">
          <p class="title">ГОРОДА</p>
          <div class="content">
            <span>
              <!-- City 1 -->
              <template v-if="city1">
                {{ city1.name }}<br/>
                <template v-for="demand in formatCityDemands(city1)" :key="demand.resourceId">
                  &nbsp;&nbsp;• {{ getResourceName(demand.resourceId) }}<br/>
                </template>
              </template>
              <template v-else>
                Город 1<br/>
              </template>
              <br/>
              
              <!-- City 2 -->
              <template v-if="city2">
                {{ city2.name }}<br/>
                <template v-for="demand in formatCityDemands(city2)" :key="demand.resourceId">
                  &nbsp;&nbsp;• {{ getResourceName(demand.resourceId) }}<br/>
                </template>
              </template>
              <template v-else>
                Город 2<br/>
              </template>
            </span>

            <span>
              <!-- City 3 -->
              <template v-if="city3">
                {{ city3.name }}<br/>
                <template v-for="demand in formatCityDemands(city3)" :key="demand.resourceId">
                  &nbsp;&nbsp;• {{ getResourceName(demand.resourceId) }}<br/>
                </template>
              </template>
              <template v-else>
                Город 3<br/>
              </template>
              <br/>
              
              <!-- City 4 -->
              <template v-if="city4">
                {{ city4.name }}<br/>
                <template v-for="demand in formatCityDemands(city4)" :key="demand.resourceId">
                  &nbsp;&nbsp;• {{ getResourceName(demand.resourceId) }}<br/>
                </template>
              </template>
              <template v-else>
                Город 4<br/>
              </template>
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
  font-size: 2rem;
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
