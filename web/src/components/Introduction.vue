<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { gsap } from 'gsap'
import { animationConfig, getDuration, getDelay, logTimelineDuration } from '../animationConfig.js'

const pageRef = ref(null)
const sessionId = ref('')
const currentInstructionIndex = ref(0)
const instructionInterval = ref(null)

// Game instructions that rotate every 15 seconds
const instructions = [
  {
    title: "Добро пожаловать в экономическую игру!",
    text: "Соревнуйтесь с другими игроками в этой стратегической экономической симуляции. Стройте компании, управляйте ресурсами и доминируйте на рынке, чтобы стать абсолютной экономической силой."
  },
  {
    title: "Постройте свою империю",
    text: "Начните с создания компаний на карте. Выбирайте стратегические места, чтобы максимизировать свой потенциал прибыли. Каждая плитка предлагает разные преимущества и ресурсы."
  },
  {
    title: "Управляйте ресурсами",
    text: "Сбалансируйте свои финансы, репутацию и ресурсы. Делайте разумные инвестиции и наблюдайте, как ваша экономическая империя растет с каждым ходом."
  },
  {
    title: "Соревнуйтесь и побеждайте",
    text: "Перехитрите своих противников с помощью хитроумных стратегий. Формируйте альянсы, блокируйте конкурентов и используйте рыночную динамику в своих интересах."
  },
  {
    title: "Готовы играть?",
    text: "Введите идентификатор сеанса ниже, чтобы присоединиться к существующей игре или создать новый сеанс. Соберите своих друзей и начните строить свое экономическое наследие!"
  }
]

function nextInstruction() {
  currentInstructionIndex.value = (currentInstructionIndex.value + 1) % instructions.length
  animateTextChange()
}

function previousInstruction() {
  currentInstructionIndex.value = currentInstructionIndex.value === 0 
    ? instructions.length - 1 
    : currentInstructionIndex.value - 1
  animateTextChange()
}

function animateTextChange() {
  const title = document.querySelector('#instruction-title')
  const text = document.querySelector('#instruction-text')
  
  if (title && text) {
    gsap.timeline()
      .to([title, text], { opacity: 0, y: -10, duration: 0.2, ease: 'power2.out' })
      .to([title, text], { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' })
  }
}

function startInstructionRotation() {
  instructionInterval.value = setInterval(nextInstruction, 15000) // 15 seconds
}

function stopInstructionRotation() {
  if (instructionInterval.value) {
    clearInterval(instructionInterval.value)
    instructionInterval.value = null
  }
}

function joinSession() {
  // TODO: Implement join session functionality
  console.log('Joining session:', sessionId.value)
}

function playEntranceAnimation() {
  // Set initial positions (elements start off-screen)
  gsap.set('#game-logo', { y: -100, opacity: 0 })
  gsap.set('#instruction-panel', { scale: 0.8, opacity: 0 })
  gsap.set('#session-panel', { y: 100, opacity: 0 })
  gsap.set('#instruction-nav', { x: -50, opacity: 0 })

  // Create entrance animation timeline
  const tl = gsap.timeline({ delay: getDelay(animationConfig.durations.delay) })

  tl.to('#game-logo', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.bounce })
    .to('#instruction-panel', { scale: 1, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.mapBounce }, '-=0.4')
    .to('#instruction-nav', { x: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.3')
    .to('#session-panel', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.bounce }, '-=0.2')

  logTimelineDuration(tl, 'Introduction', 'entrance')
}

function playExitAnimation() {
  const tl = gsap.timeline()

  tl.to('#session-panel', { y: 50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth })
    .to('#instruction-nav', { x: -30, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.3')
    .to('#instruction-panel', { scale: 0.9, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.2')
    .to('#game-logo', { y: -50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.2')

  logTimelineDuration(tl, 'Introduction', 'exit')
}

onMounted(() => {
  playEntranceAnimation()
  startInstructionRotation()

  // Listen for exit animation trigger
  pageRef.value?.addEventListener('triggerExit', playExitAnimation)
})

onUnmounted(() => {
  stopInstructionRotation()
  pageRef.value?.removeEventListener('triggerExit', playExitAnimation)
})
</script>

<template>
  <div id="page" ref="pageRef">
    <div id="content">
      <!-- Game Logo/Title -->
      <div id="game-logo">
        <h1>Simple Economic Game</h1>
      </div>

      <!-- Instructions Panel -->
      <div id="instruction-panel">
        <div id="instruction-content">
          <h2 id="instruction-title">{{ instructions[currentInstructionIndex].title }}</h2>
          <p id="instruction-text">{{ instructions[currentInstructionIndex].text }}</p>
        </div>
        
        <!-- Navigation arrows -->
        <div id="instruction-nav">
          <button @click="previousInstruction" class="nav-btn" id="prev-btn">◀</button>
          <div id="instruction-counter">
            {{ currentInstructionIndex + 1 }} / {{ instructions.length }}
          </div>
          <button @click="nextInstruction" class="nav-btn" id="next-btn">▶</button>
        </div>
      </div>

      <!-- Session Panel -->
      <div id="session-panel">
        <div id="session-input-group">
          <label for="session-input">ID Сессии:</label>
          <input 
            type="text" 
            id="session-input" 
            v-model="sessionId" 
            placeholder="Введите ID Сессии"
            @keyup.enter="joinSession"
          />
        </div>
        <button id="join-btn" @click="joinSession" :disabled="!sessionId.trim()">
          Присоединиться к сессии
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
#page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

#content {
  max-width: 800px;
  width: 90%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  align-items: center;
}

#game-logo h1 {
  font-size: var(--text-2xl);
  color: white;
  text-align: center;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

#instruction-panel {
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  width: 100%;
  max-width: 600px;
}

#instruction-content {
  text-align: center;
  margin-bottom: var(--spacing-md);
}

#instruction-title {
  font-size: var(--text-xl);
  color: #333;
  margin: 0 0 var(--spacing-sm) 0;
  font-weight: 800;
}

#instruction-text {
  font-size: var(--text-md);
  color: #555;
  line-height: 1.6;
  margin: 0;
  font-weight: 500;
}

#instruction-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
}

.nav-btn {
  background: #667eea;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: var(--text-md);
  transition: all 0.2s ease;
}

.nav-btn:hover {
  background: #5a67d8;
  transform: scale(1.1);
}

.nav-btn:active {
  transform: scale(0.95);
}

#instruction-counter {
  font-size: var(--text-sm);
  color: #666;
  font-weight: 600;
  min-width: 60px;
  text-align: center;
}

#session-panel {
  background: rgba(255, 255, 255, 0.95);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

#session-input-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

#session-input-group label {
  font-size: var(--text-md);
  color: #333;
  font-weight: 600;
}

#session-input {
  padding: var(--spacing-sm);
  border: var(--border-width) solid #ddd;
  border-radius: var(--border-radius);
  font-size: var(--text-md);
  font-family: inherit;
  transition: border-color 0.2s ease;
}

#session-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

#join-btn {
  background: limegreen;
  color: white;
  border: var(--border-width) solid green;
  border-radius: var(--border-radius);
  padding: var(--spacing-md);
  font-size: var(--text-lg);
  font-family: inherit;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

#join-btn:hover:not(:disabled) {
  background: #32cd32;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(50, 205, 50, 0.3);
}

#join-btn:active:not(:disabled) {
  transform: translateY(0);
}

#join-btn:disabled {
  background: #ccc;
  border-color: #999;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  #content {
    width: 95%;
  }
  
  #instruction-panel,
  #session-panel {
    padding: var(--spacing-md);
  }
}
</style>