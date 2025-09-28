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

// Ref to map root element for dynamic sizing
const mapRoot = ref(null)

let resizeObserver = null
let windowResizeHandler = null

function updateMapSize(reason = 'initial') {
    const el = mapRoot.value
    if (!el) return
    const parent = el.parentElement
    if (!parent) return

    let side = 0

    const parentStyles = getComputedStyle(parent)
    const parentWidth = parent.clientWidth - parseFloat(parentStyles.paddingLeft) - parseFloat(parentStyles.paddingRight)
    const parentHeightRaw = parent.clientHeight - parseFloat(parentStyles.paddingTop) - parseFloat(parentStyles.paddingBottom)

    // Viewport-based available height from parent's top (prevents one-way growth)
    const parentRect = parent.getBoundingClientRect()
    const viewportHeightAvailable = window.innerHeight - parentRect.top - 16 // 16px safety margin

    if (parentWidth > parentHeightRaw) {
        side = parentHeightRaw;
    } else {
        side = parentWidth;
    }

    el.style.width = side + 'px'
    el.style.height = side + 'px'

    if (typeof window.log === 'function') {
        window.log(`[Map] updateMapSize (${reason}) parentWidth=${parentWidth} parentHeightRaw=${parentHeightRaw} viewportAvail=${viewportHeightAvailable} side=${side}`)
    }
}

onMounted(async () => {
    await nextTick()

    // Setup resize observation for dynamic square sizing
    updateMapSize('mount')
    windowResizeHandler = () => updateMapSize('window-resize')
    window.addEventListener('resize', windowResizeHandler)

    if ('ResizeObserver' in window) {
        resizeObserver = new ResizeObserver(() => updateMapSize('parent-resize'))
        if (mapRoot.value && mapRoot.value.parentElement) {
            resizeObserver.observe(mapRoot.value.parentElement)
        }
    }

    // Set border radius for corner tiles (after tiles exist)
    if (tileRefs.value[0]) {
        tileRefs.value[0].style.borderTopLeftRadius = "4px"
        tileRefs.value[cols - 1].style.borderTopRightRadius = "4px"
        tileRefs.value[(rows - 1) * cols].style.borderBottomLeftRadius = "4px"
        tileRefs.value[rows * cols - 1].style.borderBottomRightRadius = "4px"
    }

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
        setTile(3, 3, TileTypes.BANK, "ЦЕНТР. БАНК", "var(--text-xs)")
        
        if (typeof window.log === 'function') {
            window.log('Map loaded with default static data')
        }
    }
})

onUnmounted(() => {
    if (windowResizeHandler) {
        window.removeEventListener('resize', windowResizeHandler)
    }
    if (resizeObserver && mapRoot.value && mapRoot.value.parentElement) {
        try { resizeObserver.unobserve(mapRoot.value.parentElement) } catch (_) {}
    }
    resizeObserver = null
})

// Watch for session changes and reload map
if (wsManager) {
    watch(() => wsManager.session_id, (newSessionId) => {
        if (newSessionId && wsManager.map) {
            // Small delay to ensure DOM & sizing applied first
            setTimeout(() => {
                wsManager.loadMapToDOM()
                updateMapSize('session-change')
                if (typeof window.log === 'function') {
                    window.log('Map reloaded due to session change: ' + newSessionId)
                }
            }, 100)
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
    /* Allow the JS to decide final square size */
    overflow: hidden;
}

#map {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    grid-template-rows: repeat(7, 1fr);
    background: #333;
    border-radius: 6px;
    gap: 4px;
    padding: 4px;
    box-sizing: border-box;
    overflow: hidden;
    /* Width/height are set dynamically via JS to enforce squareness */
}

.tile {
    width: 100%;
    height: 100%;
    aspect-ratio: 1/1;
    
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f3f4f6;
    user-select: none;
    cursor: pointer;
    font-weight: 600;
    margin: 0;
    padding: 0;
    
    /* Responsive font sizing based on cell size */
    font-size: clamp(8px, min(1.2vw, 1.2vh), 16px);
    
    /* Text handling for overflow */
    word-wrap: break-word;
    text-align: center;
    overflow: hidden;
    
    /* Smooth transitions */
    transition: background-color 1s ease, font-size 0.3s ease;
}

/* Responsive font sizing adjustments */
@media (max-width: 768px) {
    .tile {
        font-size: clamp(6px, 2vw, 12px);
    }
}

@media (max-width: 480px) {
    .tile {
        font-size: clamp(5px, 2.5vw, 10px);
    }
}
</style>
