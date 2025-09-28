<template>
  <div class="admin-panel">
    <h2>Admin Panel</h2>
    <button @click="$emit('show', 'Introduction')">Show Introduction</button>
    <button @click="$emit('show', 'Preparation')">Show Preparation</button>
    <button @click="$emit('show', 'Game')">Show Game</button>
    <button @click="$emit('show', 'Between')">Show Between</button>
    <button @click="$emit('show', 'Endgame')">Show Endgame</button>
  </div>
</template>

<script setup>

</script>

<style scoped>
.admin-panel {
  background: #f5f5f5;
  padding: 4px;
  border-bottom: 1px solid #ccc;
  position: sticky;
  top: 0;
  z-index: 100;
}
</style>
