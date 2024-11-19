<template>
  <v-container>
    <h2>챗봇</h2>
    <v-text-field
      v-model="question"
      label="질문을 입력하세요"
      @keyup.enter="submitQuestion"
    ></v-text-field>
    <v-btn @click="submitQuestion">전송</v-btn>

    <div v-if="answer">
      <h3>답변:</h3>
      <p>{{ answer }}</p>
    </div>
  </v-container>
</template>

<script>
import apiClient from '@/api';

export default {
  name: 'ChatbotView',
  data() {
    return {
      question: '',
      answer: '',
    };
  },
  methods: {
    async submitQuestion() {
      if (!this.question) return;
      try {
        const response = await apiClient.post('companies/chatbot/', {
          question: this.question,
        });
        this.answer = response.data.answer;
      } catch (error) {
        console.error(error);
      }
    },
  },
};
</script>

<style scoped>
/* 필요한 스타일을 추가합니다 */
</style> 