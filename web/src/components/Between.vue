<script setup>
import Map from './Map.vue'
</script>

<template>
  <div id="page">
    <div id="column-left">
      <div id="map-title">
        Карта мира
      </div>

      <Map />

      <div id="round-info">
        <div id="timer">
          Время до конца этапа: 00:00
        </div>
        <div id="teams-ready">
          4/10
        </div>
      </div>

    </div>

    <div id="column-right">
      <div id="column-right-header">
        <p class="column-title"> Лучшие Результаты </p>
        <p class="column-title"> Топ компании </p>
      </div>
      <div id="column-right-content-top">
        <div id="list-col-left" class="column">
          <div v-for="n in 3" :key="n" class="list-item" :id="'demand-' + n">
            Результат {{ n }}
          </div>
        </div>
        <div id="list-col-right" class="column">
          <div v-for="n in 3" :key="n" class="list-item" :id="'stock-' + n">
            Топовая компания {{ n }}
          </div>
        </div>
      </div>
      <div id="column-right-content-bottom">
        Информация о событии
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
  width: 100%;
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

#column-right-content-top {
  flex: 1;
  display: flex;
  gap: var(--spacing-sm);
}

#column-right-content-bottom {
  min-height: 100px;
  background-color: lightgray;
  color: black;
  border: var(--border-width) solid gray;
  border-radius: var(--border-radius);
  padding: var(--spacing-sm) 0;
  font-size: var(--text-md);

  text-align: center;
  margin-top: var(--spacing-sm);
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

#round-info {
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  gap: var(--spacing-sm);
}

#timer,
#teams-ready {
  font-size: var(--text-lg);
  text-align: center;
  justify-content: center;

  padding: var(--spacing-sm) var(--spacing-sm);
  background: lightgray;
  border-radius: var(--border-radius);
  border: var(--border-width) solid gray;
}


Map {
  margin: 0;
}
</style>
