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
  [TileTypes.MOUNTAINS]: { color: "Gray"},
  [TileTypes.WATER]: { color: "dodgerBlue"},
  [TileTypes.FOREST]: { color: "ForestGreen"},
  [TileTypes.FIELD]: { color: "Khaki"},
  [TileTypes.CITY]: { color: "orange"},
  [TileTypes.BANK]: { color: "red"},
}

function setTile(row, col, tileType, text, font_size) {
  if (row < 0 || row >= rows || col < 0 || col >= cols) return
  const idx = row * cols + col
  const tile = tileRefs.value[idx]
  if (!tile) return
  if (tileType) tile.style.backgroundColor = tileStyles[tileType].color
  if (text) tile.textContent = text
  if (font_size) tile.style.fontSize = font_size
}

export { tiles, tileRefs, TileTypes, tileStyles, setTile, rows, cols }