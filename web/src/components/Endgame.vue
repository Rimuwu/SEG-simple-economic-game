<script setup>
import { ref, onMounted } from 'vue'

const pageRef = ref(null)

const AUTHORS = import.meta.env.VITE_AUTHORS;

onMounted(() => {
  document.getElementById("authors").innerHTML = AUTHORS.split("/").join("<br/>");
})

</script>

<template>
  <div id="page" ref="pageRef">
    
    <div id="column-left">
      <p id="title">Победители</p>
      <div id="by-money" class="element">
        <p class="title">по капиталу</p>
        <p class="name">супер крутая компания номер 1</p>
      </div>
      <div id="by-rep" class="element">
        <p class="title">по репутации</p>
        <p class="name">супер крутая компания номер 1</p>
      </div>
      <div id="by-level" class="element">
        <p class="title">по экономическому уровню</p>
        <p class="name">супер крутая компания номер 1</p>
      </div>
    </div>

    <div id="column-right">
      <p>
        Спасибо за игру в SEG.<br/><br/>
        Игра создана и разработана по авторской идеи и без использования потусторонних сил.<br/><br/>
        Создатели:<br/>
        <span id="authors"></span>
      </p>
    </div>
  </div>

</template>

<style scoped>
#page {
  display: flex;
  align-items: stretch;

  margin: 0;
  padding: 0;

  width: 100%;
  height: 100vh;

  background: #0C9273;
}

#column-left {
  flex: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #0C9273;
  gap: 36px;
}

#column-right {
  flex: 1;
  display: flex;
  flex-direction: column;

  background: #0C6892;

  font-size: 4rem;
  color: white;
  text-align: center;
  justify-content: center;
  line-height: 1.5;
}

#title {
  color: white;
  font-size: 6rem;
  margin: 0;
}

.element {
  margin: 0;
  padding: 10px;
  color: white;
  text-align: center;
  background: #0C6892;
  width: 90%;
}

.title {
  font-family: "Ubuntu Mono", monospace;
  font-size: 4rem;
  text-transform: uppercase;
}
.name {
  font-size: 5rem;
}
</style>
