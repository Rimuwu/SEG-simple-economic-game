<template>
  <div class="admin-panel">
    <h2>Admin Panel</h2>
    <!-- Add admin controls here -->
    <button @click="$emit('show', 'Preparation')">Show Preparation</button>
    <button @click="$emit('show', 'Game')">Show Game</button>
  </div>
</template>

<script setup>
// No script needed for basic panel
</script>

<style scoped>
.admin-panel {
  background: #f5f5f5;
  padding: 16px;
  border-bottom: 1px solid #ccc;
  position: sticky;
  top: 0;
  z-index: 100;
}
</style>
