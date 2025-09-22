<template>
    <div id="map">
        <div v-for="(tile, idx) in tiles" :key="tile.id" class="tile" :data-index="idx" ref="tileRefs">
            {{ tile.label }}
        </div>
    </div>
</template>

<script setup>
import { tiles, tileRefs, TileTypes, tileStyles, setTile, rows, cols } from './mapScripts.js'
import { onMounted, nextTick } from 'vue'

onMounted(async () => {
    await nextTick()

    tileRefs.value[0].style.borderTopLeftRadius = "4px"
    tileRefs.value[cols - 1].style.borderTopRightRadius = "4px"
    tileRefs.value[(rows - 1) * cols].style.borderBottomLeftRadius = "4px"
    tileRefs.value[rows * cols - 1].style.borderBottomRightRadius = "4px"

    setTile(1, 1, TileTypes.CITY, "ГОРОД А")
    setTile(5, 1, TileTypes.CITY, "ГОРОД В")
    setTile(1, 5, TileTypes.CITY, "ГОРОД Б")
    setTile(5, 5, TileTypes.CITY, "ГОРОД Г")
    setTile(3, 3, TileTypes.BANK, "ЦЕНТР. БАНК", "var(--text-xs)")

    window.setTile = setTile
    window.TileTypes = TileTypes
})
</script>

<style scoped>
#map {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    background: #333;
    border-radius: 6px;
    gap: 4px;
    padding: 4px;
    width: auto;
    height: auto;
    aspect-ratio: 1/1;
    max-height: 80vh;
    box-sizing: border-box;
    overflow: hidden;
}

.tile {
    aspect-ratio: 1/1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f3f4f6;
    user-select: none;
    cursor: pointer;
    font-weight: 600;
    font-size: var(--text-sm);
    margin: 0;
    padding: 3px;
    word-wrap: break-word;
    text-align: center;


    transition: background-color 1s ease, font-size 1s ease;
}
</style>
