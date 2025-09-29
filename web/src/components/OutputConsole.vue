<template>
  <div 
    class="output-console" 
    :class="{ 'pinned': isPinned }"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    v-show="isVisible"
  >
    <div class="console-header">
      <span class="console-title">Output Console</span>
      <button 
        class="pin-button" 
        @click="togglePin"
        :title="isPinned ? 'Unpin console' : 'Pin console'"
      >
        {{ isPinned ? '📌' : '📍' }}
      </button>
    </div>
    <div class="console-content" ref="consoleContent">
      <div 
        v-for="(entry, index) in consoleEntries" 
        :key="entry.id"
        class="console-entry"
        :class="entry.type"
      >
        <span class="timestamp">{{ entry.timestamp }}</span>
        <span class="message">{{ entry.message }}</span>
      </div>
    </div>
    <div class="console-actions">
      <button @click="clearConsole" class="clear-button">Clear</button>
      <button @click="exportLogs" class="export-button">Export</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const isVisible = ref(false)
const isPinned = ref(false)
const consoleEntries = ref([])
const consoleContent = ref(null)
let entryId = 0

const emit = defineEmits(['mouseenter', 'mouseleave'])

// Format timestamp
function formatTimestamp() {
  const now = new Date()
  return now.toLocaleTimeString('en-US', { 
    hour12: false, 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    fractionalSecondDigits: 3
  })
}

// Add log entry
function addLogEntry(message, type = 'log') {
  console.log(message);
  consoleEntries.value.push({
    id: ++entryId,
    message: String(message),
    type: type,
    timestamp: formatTimestamp()
  })
  
  // Limit console entries to prevent memory issues
  if (consoleEntries.value.length > 1000) {
    consoleEntries.value.shift()
  }
  
  // Auto-scroll to bottom
  nextTick(() => {
    if (consoleContent.value) {
      consoleContent.value.scrollTop = consoleContent.value.scrollHeight
    }
  })
}

// Global log method
function log(message) {
  addLogEntry(message, 'log')
}

// Global error method
function error(message) {
  addLogEntry(message, 'error')
}

// Clear console
function clearConsole() {
  consoleEntries.value = []
}

// Export logs
function exportLogs() {
  const logs = consoleEntries.value.map(entry => 
    `[${entry.timestamp}] ${entry.type.toUpperCase()}: ${entry.message}`
  ).join('\n')
  
  const blob = new Blob([logs], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `console-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// Handle mouse events
function handleMouseEnter() {
  if (!isPinned.value) {
    isVisible.value = true
  }
  emit('mouseenter')
}

function handleMouseLeave() {
  if (!isPinned.value) {
    isVisible.value = false
  }
  emit('mouseleave')
}

// Toggle pin state
function togglePin() {
  isPinned.value = !isPinned.value
  if (isPinned.value) {
    isVisible.value = true
  }
}

// Get viewport width using multiple fallback methods
function getViewportWidth() {
  // Try multiple methods to get viewport width
  return document.body.clientWidth ||
         screen.width
}

// Show console on mouse move to top-right corner
function handleGlobalMouseMove(e) {
  const threshold = 32
  const viewportWidth = getViewportWidth()
  
  // Debug: Uncomment the line below to see mouse position in console
  // console.log(`Mouse: ${e.clientX}/${viewportWidth}, ${e.clientY} | Trigger zone: >${viewportWidth - threshold}, <${threshold}`)
  
  if (e.clientX > viewportWidth - threshold && e.clientY < threshold) {
    isVisible.value = true
  }
}

onMounted(() => {
  // Add global mouse move listener
  document.addEventListener('mousemove', handleGlobalMouseMove)
  
  // Make log and error methods globally available
  window.error = error
  
  // Also add them to globalThis for broader compatibility
  globalThis.error = error
  
  // Optional: Add window resize listener for debugging
  const handleResize = () => {
  }
  
  window.addEventListener('resize', handleResize)
  
  // Store the resize handler for cleanup
  window._consoleResizeHandler = handleResize
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleGlobalMouseMove)
  
  // Clean up resize listener
  if (window._consoleResizeHandler) {
    window.removeEventListener('resize', window._consoleResizeHandler)
    delete window._consoleResizeHandler
  }
  
  // Clean up global methods
  delete window.error  
  delete globalThis.error
})

// Expose methods for external access
defineExpose({
  log,
  error,
  clearConsole,
  togglePin,
  show: () => { isVisible.value = true },
  hide: () => { isVisible.value = false }
})
</script>

<style scoped>
.output-console {
  position: fixed;
  top: 0;
  right: 0;
  width: clamp(320px, 30vw, 450px);
  height: clamp(250px, 40vh, 400px);
  background: rgba(255, 255, 255, 0.95);
  border: var(--border-width) solid rgba(255, 255, 255, 0.2);
  border-radius: var(--border-radius) 0 0 var(--border-radius);
  color: #333;
  font-family: inherit;
  font-size: var(--text-sm);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

.output-console:not(.pinned):not(:hover) {
  opacity: 0.9;
  transform: translateX(2px);
}

.output-console.pinned {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(102, 126, 234, 0.1);
  border-bottom: var(--border-width) solid rgba(102, 126, 234, 0.2);
  font-weight: 600;
}

.console-title {
  font-size: var(--text-md);
  color: #333;
  font-weight: 800;
}

.pin-button {
  background: rgba(102, 126, 234, 0.1);
  border: var(--border-width) solid rgba(102, 126, 234, 0.2);
  color: #333;
  cursor: pointer;
  font-size: var(--text-md);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius);
  transition: all 0.2s ease;
  font-family: inherit;
}

.pin-button:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.pin-button:active {
  transform: translateY(0);
}

.console-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-sm);
  line-height: 1.5;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--text-xs);
}

.console-content::-webkit-scrollbar {
  width: 6px;
}

.console-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.console-content::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
  transition: background 0.2s ease;
}

.console-content::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}

.console-entry {
  margin-bottom: var(--spacing-xs);
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs);
  border-radius: calc(var(--border-radius) / 2);
  transition: background-color 0.1s ease;
}

.console-entry:hover {
  background: rgba(102, 126, 234, 0.05);
}

.console-entry.log {
  color: #333;
}

.console-entry.error {
  color: #e53e3e;
  background: rgba(229, 62, 62, 0.05);
  border-left: 3px solid #e53e3e;
  padding-left: calc(var(--spacing-xs) - 3px);
}

.console-entry.error:hover {
  background: rgba(229, 62, 62, 0.1);
}

.timestamp {
  color: #666;
  font-size: calc(var(--text-xs) * 0.9);
  min-width: clamp(60px, 15%, 80px);
  flex-shrink: 0;
  font-weight: 500;
}

.message {
  word-break: break-word;
  flex: 1;
  font-weight: 400;
}

.console-actions {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(102, 126, 234, 0.05);
  border-top: var(--border-width) solid rgba(102, 126, 234, 0.1);
}

.clear-button,
.export-button {
  background: rgba(102, 126, 234, 0.1);
  border: var(--border-width) solid rgba(102, 126, 234, 0.2);
  color: #333;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius);
  font-size: var(--text-xs);
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  flex: 1;
}

.clear-button:hover,
.export-button:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

.clear-button:active,
.export-button:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(102, 126, 234, 0.1);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .output-console {
    width: clamp(280px, 40vw, 350px);
    height: clamp(200px, 35vh, 300px);
  }
  
  .console-header {
    padding: var(--spacing-xs) var(--spacing-sm);
  }
  
  .console-title {
    font-size: var(--text-sm);
  }
  
  .console-actions {
    padding: var(--spacing-xs) var(--spacing-sm);
  }
}

@media (max-width: 480px) {
  .output-console {
    width: clamp(250px, 50vw, 300px);
    height: clamp(180px, 30vh, 250px);
  }
  
  .console-content {
    font-size: calc(var(--text-xs) * 0.9);
  }
  
  .console-actions {
    flex-direction: column;
    gap: var(--spacing-xs);
  }
}
</style>