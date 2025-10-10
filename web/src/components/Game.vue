<script setup>
import Map from './Map.vue'
import { onMounted, ref } from 'vue'

const pageRef = ref(null)

onMounted(() => {
  // Component mounted
})
</script>


<template>
  <!--
    Preparation page layout.
    Left column: title, map, session key.
    Right columns: alternating company slots (left/right).
  -->
  <div id="page" ref="pageRef">
    <div class="left">
      <Map class="map" />
      <div class="footer">
        <div>До конца этапа 02:53</div>
        <div>4/5</div>
      </div>
    </div>
    <div class="right">
      <div class="grid">
        
        <div class="cities grid-item">
          <p class="title">ГОРОДА</p>
          <div class="content">
          <span>
Город А (ЛВ)<br/>
&nbsp;&nbsp;• Генератор<br/>
&nbsp;&nbsp;• Медикаменты<br/>
<br/>
Город Б (НЛ)<br/>
&nbsp;&nbsp;• Генератор<br/>
&nbsp;&nbsp;• Медикаменты<br/>
          </span>

          <span>
Город В (ПВ)<br/>
&nbsp;&nbsp;• Генератор<br/>
&nbsp;&nbsp;• Медикаменты<br/>
<br/>
Город Г (НП)<br/>
&nbsp;&nbsp;• Генератор<br/>
&nbsp;&nbsp;• Медикаменты<br/>
          </span>
          </div>
        </div>

        <div class="stock grid-item">
          <p class="title">БИРЖА</p>
          <div class="content">
            <span>Компания А выставила на продажу продукт Б</span>
            <span>Компания Б выкупила Х товара у компании С</span>
            <span>Компания А выставила на продажу продукт Б</span>
            <span>Компания А выставила на продажу продукт Б</span>
          </div>
        </div>
        <div class="upgrades grid-item">
          <p class="title">УЛУЧШЕНИЯ</p>
          <div class="content">
            <span>Компания А улучшила своё хранилище до уровня 2</span>
            <span>Компания А улучшила своё хранилище до уровня 2</span>
            <span>Компания А улучшила своё хранилище до уровня 2</span>
            <span>Компания А улучшила своё хранилище до уровня 2</span>
          </div>
        </div>
        <div class="contracts grid-item">
          <p class="title">КОНТРАКТЫ</p>
          <div class="content">
            <span>Компания А создала свободный контракт на Х продукта Б на С ходов</span>
            <span>Компания А создала свободный контракт на Х продукта Б на С ходов</span>
          </div>
        </div>


      </div>
    </div>
  </div>
</template>

<style scoped>
#page {
  display: flex;
  height: 100vh;
  background-color: #3D8C00;
  font-family: "Inter", sans-serif;
  padding: 0;
  margin: 0;
}

.left,
.right {
  width: 50%;
  padding: 40px;
}


.left {
  background-color: #3D8C00;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.right {
  background-color: #0C6892;

  color: black;
  padding: 90px 50px;
}

.grid {
  margin: auto;
  display: grid;
  padding: 0; margin: 0;

  width: 100%;
  height: 100%;

  justify-items: stretch;
  align-items: center;
  align-content: space-between;
  justify-content: space-between;

  grid-template-columns: 47.5% 47.5%;
  grid-template-rows: 47.5% 47.5%;
}

.grid-item {
  width: 100%; height: 100%;
  /* background: #0f0; */
}

.content {
  font-size: 2.25rem;
  color: white;
  font-weight: 400;
}

.title {
  font-size: 4rem;
  margin: 0;
  margin-bottom: 10px;
  text-transform: uppercase;
  margin-bottom: 20px;
  color: white;
  text-align: center;
}

.cities .content {
  padding: 5px 10px;

  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  text-align: left;
  line-height: 1.5;
  background: #3D8C00;
}

.stock .content, .upgrades .content, .contracts .content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.stock span, .upgrades span, .contracts span {
  background: #3D8C00;
  padding: 5px 10px;
}

.footer {
  width: 90%;

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;

  font-weight: normal;
  font-size: 4rem;

  gap: 5%;

  color: white;
}

.footer div {
  background: #0C6792;
  padding: 25px 50px;
}

.map {
  width: 90%;
  margin: 0; padding: 0;
}
</style>
