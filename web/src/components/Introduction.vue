<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'
import { gsap } from 'gsap'
import { animationConfig, getDuration, getDelay, logTimelineDuration } from '../animationConfig.js'

const dfsglsdfklhls = "QHNuZWdfZ2FtZWJvdA==";

const pageRef = ref(null)
const sessionId = ref('')
const currentInstructionIndex = ref(0)
const instructionInterval = ref(null)
const isJoining = ref(false)

// Get WebSocket manager from parent
const wsManager = inject('wsManager', null)

// Define emit to send events to parent
const emit = defineEmits(['navigateTo'])

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
  if (!wsManager) {
    if (typeof window.error === 'function') {
      window.error('WebSocket manager not available');
    } else {
      console.error('WebSocket manager not available');
    }
    return;
  }

  if (!sessionId.value.trim()) {
    if (typeof window.error === 'function') {
      window.error('Please enter a session ID');
    } else {
      console.error('Please enter a session ID');
    }
    return;
  }

  isJoining.value = true;

  if (typeof window.log === 'function') {
    window.log('Attempting to join session: ' + sessionId.value);
  }

  // Use the WebSocket manager to join the session
  wsManager.join_session(sessionId.value.trim(), (result) => {
    isJoining.value = false;

    if (result.success) {
      if (typeof window.log === 'function') {
        window.log('Successfully joined session: ' + wsManager.session_id);
      }

      // Navigate to the next page (Preparation)
      emit('navigateTo', 'Preparation');
    } else {
      if (typeof window.error === 'function') {
        window.error('Failed to join session: ' + (result.error || 'Session not found'));
      } else {
        console.error('Failed to join session:', result.error);
      }
    }
  });
}

let sdfhlhksg = atob(dfsglsdfklhls);

function playEntranceAnimation() {
  gsap.set('.acronym', { y: -100, opacity: 0 })
  gsap.set('.left-container', { scale: 0.8, opacity: 0 })
  gsap.set('footer', { y: 100, opacity: 0 })

  const tl = gsap.timeline({ delay: getDelay(animationConfig.durations.delay) })

  tl.to('.acronym', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.bounce })
    .to('.left-container', { scale: 1, opacity: 1, duration: getDuration(animationConfig.durations.entrance), ease: animationConfig.ease.mapBounce }, '-=0.4')
    .to('footer', { y: 0, opacity: 1, duration: getDuration(animationConfig.durations.slide), ease: animationConfig.ease.smooth }, '-=0.3')
    
  logTimelineDuration(tl, 'Introduction', 'entrance')
}

function playExitAnimation() {
  const tl = gsap.timeline()

  tl.to('.acronym', { y: 50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth })
    .to('.left-containerl', { scale: 0.9, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.2')
    .to('footer', { y: 50, opacity: 0, duration: getDuration(animationConfig.durations.exit), ease: animationConfig.ease.exitSmooth }, '-=0.2')

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
    <div class="left">
      <div class="left-container">
        <div class="image-box">image</div>
        <div class="text">
          {{ instructions[currentInstructionIndex].text }}
        </div>
      </div>
    </div>

    <div class="right">
      <div class="acronym">
        <span>S — SIMPLE</span>
        <span>E — ECONOMIC</span>
        <span>G — GAME</span>
      </div>
      <footer>
        <div class="oisdfuoiuiodsfho">{{ sdfhlhksg }}</div>
        <input class="input-box" type="text" placeholder="Введите код" autofocus v-model="sessionId"
          @keyup.enter="joinSession">
      </footer>
    </div>
  </div>
</template>

<style scoped>
* {
  box-sizing: border-box;
}

#page {
  display: flex;
  height: 100vh;
  background-color: #f7b515;
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
  background-color: #f7b515;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.left-container {
  text-align: center;
  padding: 5%;
  margin: 5%;
  background-color: #e1521d;
}

.image-box {
  width: 100%;
  aspect-ratio: 16 / 9;
  background-color: #555;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  margin-bottom: 20px;
}

.text {
  background-color: #e1521d;
  padding: 30px;
  text-align: center;
  font-size: 3rem;
  line-height: 1.4;
}

.right {
  background-color: #e1521d;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content:space-between;

  color: black;
  padding: 90px 50px;
}

.acronym {
  top: 0;
  font-size: 10rem;

  font-family: "Ubuntu Mono", monospace;
  font-weight: 700;
  font-style: normal;
}

.acronym span {
  display: block;
  padding: 15px;

  transition: color 0.3s ease;
}

.acronym span:hover {
  color: #f7b515;
  cursor:default;
}

footer {
  bottom: 0;
  text-align: center;
  width: 100%;
}

.oisdfuoiuiodsfho {
  font-size: 4rem;
  margin-bottom: 20px;;
}

.input-box {
  background-color: #f7b515;
  color: black;
  font-size: 4rem;
  padding: 40px 30px;
  width: 80%;
  
  text-align: center;
  border: none;
  outline: none;
}

.input-box::placeholder {
  color: black;
  opacity: 0.5;
}
</style>