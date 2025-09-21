<script setup>
import { ref, onMounted, nextTick } from 'vue'


</script>

<template>
  <div id="page">
    <div id="column-left">
      <div id="graphs">

      </div>
    </div>

    <div id="column-right">
      <div id="by-money" class="element">
      </div>
      <div id="by-rep" class="element">
      </div>
      <div id="by-level" class="element">
      </div>
    </div>
  </div>

</template>

<style scoped>
#page {
  display: flex;
  align-items: stretch;

  margin: 0;
  padding: var(--spacing-sm);

  gap: var(--spacing-lg);
  width: calc(100vw - var(--spacing-sm) * 2);
  height: calc(100vh - var(--spacing-sm) * 2);
}

#column-left {
  flex: 3;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

#column-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: var(--spacing-sm);
}


#column-right-header {
  display: flex;
  flex-direction: row;
}

#graphs {
  flex: 1;
  background: lightgray;
  border-radius: var(--border-radius);
  border: var(--border-width) solid gray;
}


.element {
  flex: 1;
  padding: var(--spacing-sm);
  background: lightgray;
  border-radius: var(--border-radius);
  border: var(--border-width) solid gray;
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
