<template>
    <div class="map-wrapper">
        <div id="map" ref="mapRoot">
            <div v-for="(tile, idx) in tiles" :key="tile.id" class="tile" :data-index="idx" ref="tileRefs">
                {{ tile.label }}
            </div>
        </div>
    </div>
</template>

<script setup>
import { tiles, tileRefs, TileTypes, tileStyles, setTile, rows, cols } from './mapScripts.js'
import { onMounted, onUnmounted, nextTick, inject, watch, ref } from 'vue'

// Get WebSocket manager from parent
const wsManager = inject('wsManager', null)

onMounted(async () => {
    await nextTick()
    // Make functions globally available
    window.setTile = setTile
    window.TileTypes = TileTypes

    // Load map from WebSocket data if available
    if (wsManager && wsManager.map) {
        if (typeof window.log === 'function') {
            window.log('WebSocket map data available on mount: ' + JSON.stringify(wsManager.map));
        }
        wsManager.loadMapToDOM()
        if (typeof window.log === 'function') {
            window.log('Map loaded from session data on mount')
        }
    } else {
        // Fallback to default static setup if no session data
        if (typeof window.log === 'function') {
            window.log('No WebSocket map data available, using default setup');
        }
        setTile(1, 1, TileTypes.CITY, "ГОРОД А")
        setTile(5, 1, TileTypes.CITY, "ГОРОД В")
        setTile(1, 5, TileTypes.CITY, "ГОРОД Б")
        setTile(5, 5, TileTypes.CITY, "ГОРОД Г")
        setTile(3, 3, TileTypes.BANK, "ЦЕНТР. БАНК")
        
        if (typeof window.log === 'function') {
            window.log('Map loaded with default static data')
        }
    }
})

onUnmounted(() => {
    // Cleanup global functions
    if (window.setTile) delete window.setTile
    if (window.TileTypes) delete window.TileTypes
})

// Watch for session changes and reload map
if (wsManager) {
    watch(() => wsManager.session_id, (newSessionId) => {
        if (newSessionId && wsManager.map) {
            wsManager.loadMapToDOM()
        }
    })
}
</script>

<style scoped>
.map-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;

    overflow: hidden;
}

#map {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    grid-template-rows: repeat(7, 1fr);
    background: white;
    /* gap: 4px; */
    padding: 15px;

    box-sizing: border-box;
    overflow: hidden;
    
    aspect-ratio: 1/1;

    gap: 0;
}

.tile {
    width: 100%;
    height: 100%;
    aspect-ratio: 1/1;

    box-shadow: inset 0 0 0 2px rgba(1,1,1,0.5);
    
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f3f4f6;
    user-select: none;
    cursor: pointer;
    font-weight: 600;
    margin: 0;
    padding: 0;

    
    font-size: 1.5rem;
    
    /* Text handling for overflow */
    word-wrap: break-word;
    text-align: center;
    overflow: hidden;
    
    /* Smooth transitions */
    transition: background-color 1s ease, font-size 0.3s ease;
}
</style>
