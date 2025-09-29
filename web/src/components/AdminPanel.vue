<template>
  <div class="admin-panel">
    <h2>Admin Panel</h2>
    <div class="panel-section">
      <h3>Navigation</h3>
      <button @click="$emit('show', 'Introduction')">Show Introduction</button>
      <button @click="$emit('show', 'Preparation')">Show Preparation</button>
      <button @click="$emit('show', 'Game')">Show Game</button>
      <button @click="$emit('show', 'Between')">Show Between</button>
      <button @click="$emit('show', 'Endgame')">Show Endgame</button>
    </div>
    <div class="panel-section">
      <h3>Console Test</h3>
      <button @click="testLog">Test Log</button>
      <button @click="testError">Test Error</button>
      <button @click="testWebSocket">Test WebSocket</button>
    </div>
    <div class="panel-section">
      <h3>Session & Map Test</h3>
      <button @click="testSessionJoin">Test Session Join</button>
      <button @click="testMapRefresh">Refresh Map</button>
      <button @click="debugMapInfo">Debug Map Info</button>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'

const wsManager = inject('wsManager', null)

function testLog() {
}

function testError() {
  if (typeof window.error === 'function') {
    window.error('This is a test error message from Admin Panel')
  } else {
    console.error('Error function not available yet')
  }
}

function testWebSocket() {
  if (wsManager) {
    wsManager.ping()
  } else {
    if (typeof window.error === 'function') {
      window.error('WebSocket manager not available')
    }
  }
}

function testSessionJoin() {
  if (wsManager) {
    const testSessionId = 'test_session_123'
    wsManager.join_session(testSessionId, (result) => {
      if (result.success) {
        if (typeof window.log === 'function') {
          window.log('Test session join successful: ' + JSON.stringify(result.data))
        }
      } else {
        if (typeof window.error === 'function') {
          window.error('Test session join failed: ' + result.error)
        }
      }
    })
  } else {
    if (typeof window.error === 'function') {
      window.error('WebSocket manager not available')
    }
  }
}

function testMapRefresh() {
  if (wsManager) {
    if (wsManager.map) {
      wsManager.refreshMap()
      if (typeof window.log === 'function') {
        window.log('Map refresh requested - check current page for updates')
      }
    } else {
      if (typeof window.error === 'function') {
        window.error('No map data available to refresh')
      }
    }
  } else {
    if (typeof window.error === 'function') {
      window.error('WebSocket manager not available')
    }
  }
}

function debugMapInfo() {
  if (wsManager) {
    const mapElement = document.getElementById('map');
    if (mapElement) {
      const computedStyle = window.getComputedStyle(mapElement);
      const info = {
        mapData: wsManager.map,
        elementSize: {
          width: mapElement.offsetWidth + 'px',
          height: mapElement.offsetHeight + 'px',
          computedWidth: computedStyle.width,
          computedHeight: computedStyle.height
        },
        gridColumns: computedStyle.gridTemplateColumns,
        tiles: mapElement.children.length
      };
      
      if (typeof window.log === 'function') {
        window.log('Map debug info: ' + JSON.stringify(info, null, 2));
      }
    } else {
      if (typeof window.error === 'function') {
        window.error('No #map element found on current page');
      }
    }
  } else {
    if (typeof window.error === 'function') {
      window.error('WebSocket manager not available');
    }
  }
}
</script>

<style scoped>
.admin-panel {
  background: rgba(255, 255, 255, 0.95);
  padding: var(--spacing-md);
  border: var(--border-width) solid rgba(255, 255, 255, 0.2);
  border-radius: 0 0 var(--border-radius) 0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  font-family: inherit;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.admin-panel h2 {
  margin: 0 0 var(--spacing-md) 0;
  font-size: var(--text-lg);
  color: #333;
  font-weight: 800;
  text-align: center;
}

.panel-section {
  margin-bottom: var(--spacing-md);
}

.panel-section:last-child {
  margin-bottom: 0;
}

.panel-section h3 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--text-md);
  color: #333;
  font-weight: 600;
}

.admin-panel button {
  display: block;
  width: 100%;
  margin-bottom: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  background: #667eea;
  color: white;
  border: var(--border-width) solid #5a67d8;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: var(--text-sm);
  font-family: inherit;
  font-weight: 600;
  transition: all 0.2s ease;
}

.admin-panel button:hover {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.admin-panel button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.2);
}

.admin-panel button:last-child {
  margin-bottom: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .admin-panel {
    padding: var(--spacing-sm);
  }
  
  .admin-panel h2 {
    font-size: var(--text-md);
  }
  
  .panel-section h3 {
    font-size: var(--text-sm);
  }
}
</style>
