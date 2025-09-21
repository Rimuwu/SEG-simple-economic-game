<script setup>
import { ref, onMounted, nextTick } from 'vue'


const rows = 7
const cols = 7
const total = rows * cols
const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


const tiles = Array.from({ length: total }, (_, i) => ({
  id: `t-${i}`,
  label: letters[i % rows] + (Math.floor(i / cols) + 1),
}))

const tileRefs = ref([])

const TileTypes = {
  MOUNTAINS: 0,
  WATER: 1,
  FOREST: 2,
  FIELD: 3,
  CITY: 4,
  BANK: 5
}

const tileStyles = {
  [TileTypes.MOUNTAINS]: { color: "Gray" },
  [TileTypes.WATER]: { color: "dodgerBlue" },
  [TileTypes.FOREST]: { color: "ForestGreen" },
  [TileTypes.FIELD]: { color: "Khaki" },
  [TileTypes.CITY]: { color: "orange" },
  [TileTypes.BANK]: { color: "red" },
}

// Called after the DOM has been loaded
onMounted(async () => {
  await nextTick()
  // console.log('tile DOM nodes count:', tileRefs.value.length)
  tileRefs.value[0].style.borderTopLeftRadius = "4px"
  tileRefs.value[cols - 1].style.borderTopRightRadius = "4px"
  tileRefs.value[(rows - 1) * cols].style.borderBottomLeftRadius = "4px"
  tileRefs.value[rows * cols - 1].style.borderBottomRightRadius = "4px"

  setTile(1, 1, TileTypes.CITY, "ГОРОД А")
  setTile(5, 1, TileTypes.CITY, "ГОРОД В")
  setTile(1, 5, TileTypes.CITY, "ГОРОД Б")
  setTile(5, 5, TileTypes.CITY, "ГОРОД Г")
  setTile(3, 3, TileTypes.BANK, "ЦЕНТР. БАНК", "var(--text-xs)")
})

function setTile(row, col, tileType, text, font_size) {
  if (row < 0 || row >= rows || col < 0 || col >= cols) return
  const idx = row * cols + col
  const tile = tileRefs.value[idx]
  if (!tile) return
  if (tileType) tile.style.backgroundColor = tileStyles[tileType].color
  if (text) tile.textContent = text
  if (font_size) tile.style.fontSize = font_size
}

</script>

<template>
  <div id="page">
    <div id="column-left">
      <div id="map-title">
        Карта мира
      </div>

      <div id="map">
        <div v-for="(tile, idx) in tiles" :key="tile.id" class="tile" :data-index="idx" ref="tileRefs">
          {{ tile.label }}
        </div>
      </div>

      <div id="timer">
        Время до конца этапа: 00:00
      </div>
    </div>

    <div id="column-right">
      <div id="column-right-header">
        <p class="column-title"> Спрос </p>
        <p class="column-title"> Биржа </p>
      </div>
      <div id="column-right-content">
        <div id="list-col-left" class="column">
          <div v-for="n in 4" :key="n" class="list-item" :id="'demand-' + n">
            Товар {{ n }}
          </div>
        </div>
        <div id="list-col-right" class="column">
          <div v-for="n in 4" :key="n" class="list-item" :id="'stock-' + n">
            Компания А выставила Y продукта X за Z продукта / монет {{ n }}
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<style scoped>
#page {
  display: flex;
  margin: 0;
  padding: var(--spacing-sm);

  gap: var(--spacing-lg);
  width: calc(100vw - var(--spacing-sm) * 2);
  height: calc(100vh - var(--spacing-sm) * 2);
}

#column-left {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
}

#column-right {
  flex: 1;
  display: flex;
  flex-direction: column;
}

#column-right-content {
  flex: 1;
  display: flex;
  gap: var(--spacing-sm);
}

#column-right-header {
  display: flex;
  flex-direction: row;
}

.column-title {
  flex: 1;
  font-size: var(--text-xl);
  font-weight: 600;
  text-align: center;
  margin-bottom: var(--spacing-sm);
}

.column {
  flex: 1;
  padding: var(--spacing-sm);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.list-item {
  background-color: lightgray;
  color: black;
  border: var(--border-width) solid gray;
  border-radius: var(--border-radius);
  padding: var(--spacing-sm) 0;
  font-size: var(--text-md);

  text-align: center;
  flex: 1;
}

#map-title {
  font-size: var(--text-xl);
  font-weight: 600;
  text-align: center;
  margin: var(--spacing-sm) 0;
  padding: var(--spacing-sm) 0;
  width: 90%;
}

#timer {
  font-size: var(--text-lg);
  text-align: center;
  margin: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
  width: 90%;
  background: lightgray;
  border-radius: var(--border-radius);
  border: var(--border-width) solid gray;
}


#map {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  aspect-ratio: 1/1;
  margin: 0;
  background: #333;
  border-radius: 6px;
  gap: 4px;
  padding: 4px;

  align-content: center;
  justify-content: center;
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
}
</style>
