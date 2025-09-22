<script setup>
import './mapScripts.js'
import Map from './Map.vue'
</script>

<template>
  <div id="page">
    <div id="column-left">
      <div id="start-btn">
        НАЧАТЬ ИГРУ
      </div>

      <Map />
      
      <div id="session-key">
        КЛЮЧ СЕССИИ
      </div>
    </div>

    <div id="column-right">
      <div id="list-col-left"  class="column">
        <div v-for="n in 7" :key="n" class="list-item" :id="'item-left-' + n">
          Item {{ n }}
        </div>
      </div>
      <div id="list-col-right" class="column">
        <div v-for="n in 7" :key="n" class="list-item" :id="'item-right-' + n">
          Item {{ n }}
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

#start-btn, #session-key {
  font-size: var(--text-lg);
  text-align: center;
  margin: var(--spacing-sm);
  padding: var(--spacing-sm) 0;
  width: 90%;
  background: limegreen;
  border-radius: var(--border-radius);
  border: var(--border-width) solid green; 
}
</style>
