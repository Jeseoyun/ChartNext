<script setup>
import { ref } from 'vue';

const selectedOption = ref('6mo');
const options = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'];

function fetchChartData(option) {
  // API 호출 로직을 여기에 추가하세요.
  console.log(`Fetching data for ${option}`);
  // 예시: fetch(`api/stock-data?range=${option}`)
}

function selectOption(option) {
  selectedOption.value = option;
  fetchChartData(option);
}
</script>

<template>
  <div>
    <a>chart가 보여질 부분</a>
    <div>
      <button
        v-for="option in options"
        :key="option"
        :class="{ selected: option === selectedOption }"
        @click="selectOption(option)"
      >
        {{ option }}
      </button>
    </div>
  </div>
</template>

<style scoped>
button {
  margin: 3px;
  padding: 5px;
  border: none;
  background: transparent;
  color: gray;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'AppleSDGothicNeoB', sans-serif;
}

button:hover {
  background: linear-gradient(120deg, #b0b0b0, #d0d0d0);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

button.selected {
  background-color: #808080;
  color: white;
  border-radius: 15px;
}
</style>