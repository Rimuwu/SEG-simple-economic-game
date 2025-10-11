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

// Achievements computed property
const achievements = computed(() => {
  return wsManager?.gameState?.getAchievements() || []
})

// Leaders computed property
const leaders = computed(() => {
  // Try to get session ID from session object
  let sessionId = wsManager?.gameState?.state?.session?.id
  
  // If no session ID, try to get all companies and use the first company's session_id
  const allCompanies = wsManager?.gameState?.state?.companies || []
  
  console.log('[Between.vue] Leaders - Session ID from session:', sessionId)
  console.log('[Between.vue] Leaders - All companies:', allCompanies)
  console.log('[Between.vue] Leaders - All companies count:', allCompanies.length)
  
  // If sessionId is null but we have companies, use the first company's session_id
  if (!sessionId && allCompanies.length > 0) {
    sessionId = allCompanies[0].session_id
    console.log('[Between.vue] Leaders - Using session_id from first company:', sessionId)
  }
  
  if (!sessionId) {
    console.log('[Between.vue] Leaders - No sessionId found anywhere')
    return { capital: null, reputation: null, economic: null }
  }
  
  const companies = wsManager?.gameState?.getCompaniesBySession(sessionId) || []
  console.log('[Between.vue] Leaders - Filtered companies:', companies)
  console.log('[Between.vue] Leaders - Filtered companies count:', companies.length)
  
  if (companies.length === 0) {
    console.log('[Between.vue] Leaders - No companies found for session:', sessionId)
    // Try using all companies as fallback
    if (allCompanies.length > 0) {
      console.log('[Between.vue] Leaders - Using all companies as fallback')
      const byCapital = [...allCompanies].sort((a, b) => (b.balance || 0) - (a.balance || 0))[0]
      const byReputation = [...allCompanies].sort((a, b) => (b.reputation || 0) - (a.reputation || 0))[0]
      const byEconomic = [...allCompanies].sort((a, b) => (b.economic_power || 0) - (a.economic_power || 0))[0]
      
      console.log('[Between.vue] Leaders - byCapital (fallback):', byCapital)
      console.log('[Between.vue] Leaders - byReputation (fallback):', byReputation)
      console.log('[Between.vue] Leaders - byEconomic (fallback):', byEconomic)
      
      return {
        capital: byCapital,
        reputation: byReputation,
        economic: byEconomic
      }
    }
    return { capital: null, reputation: null, economic: null }
  }
  
  // Find top companies
  const byCapital = [...companies].sort((a, b) => (b.balance || 0) - (a.balance || 0))[0]
  const byReputation = [...companies].sort((a, b) => (b.reputation || 0) - (a.reputation || 0))[0]
  const byEconomic = [...companies].sort((a, b) => (b.economic_power || 0) - (a.economic_power || 0))[0]
  
  console.log('[Between.vue] Leaders - byCapital:', byCapital)
  console.log('[Between.vue] Leaders - byReputation:', byReputation)
  console.log('[Between.vue] Leaders - byEconomic:', byEconomic)
  
  const result = {
    capital: byCapital,
    reputation: byReputation,
    economic: byEconomic
  }
  
  console.log('[Between.vue] Leaders - result:', result)
  
  return result
})

// Helper to format numbers with thousand separators
const formatNumber = (num) => {
  return num?.toLocaleString('ru-RU') || '0'
}

onMounted(() => {
  // Generate achievements when component mounts
  let sessionId = wsManager?.gameState?.state?.session?.id
  // Try to get session ID from companies if not in session object
  const companies = wsManager?.gameState?.state?.companies || []
  
  if (!sessionId && companies.length > 0) {
    sessionId = companies[0].session_id
  }
  
  if (sessionId) {
    wsManager?.gameState?.generateAchievements(sessionId)
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
            <section v-for="achievement in achievements" :key="achievement.name">
              <p class="name">{{ achievement.name }}</p>
              <p class="desc">{{ achievement.desc }}</p>
            </section>
            <section v-if="achievements.length === 0">
              <p class="desc">Выдающиеся достижения отсутсвуют</p>
            </section>
          </div>
        </div>

        <div class="leaders grid-item">
          <p class="title">ЛИДЕРЫ</p>
          <div class="content">
            <section>
              <p class="name">ПО КАПИТАЛУ</p>
              <p class="desc" v-if="leaders.capital">{{ leaders.capital.name }} ({{ formatNumber(leaders.capital.balance) }} ₽)</p>
              <p class="desc" v-else>—</p>
            </section>
            <section>
              <p class="name">ПО РЕПУТАЦИИ</p>
              <p class="desc" v-if="leaders.reputation">{{ leaders.reputation.name }} ({{ leaders.reputation.reputation }})</p>
              <p class="desc" v-else>—</p>
            </section>
            <section>
              <p class="name">ПО ЭКОНОМИЧЕСКОМУ УРОВНЮ</p>
              <p class="desc" v-if="leaders.economic">{{ leaders.economic.name }} ({{ leaders.economic.economic_power }})</p>
              <p class="desc" v-else>—</p>
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
