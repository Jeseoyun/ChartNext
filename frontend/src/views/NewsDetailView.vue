<template>
  <div class="news-detail-page">
    <!-- 스크롤 프로그레스 바 -->
    <div class="scroll-progress-container">
      <div class="scroll-progress-bar" :style="{ width: scrollProgress + '%' }"></div>
    </div>

    <!-- 기본 헤더 영역 -->
    <div class="header-area" :class="{ 'hidden': isScrolled }">
      <!-- 상단 고정 헤더 -->
      <div class="fixed-header">
        <LogoComponent />
        <NavBarComponent />
      </div>

      <!-- 카테고리 및 검색 섹션 -->
      <div class="top-section">
        <div class="category-section">
          <v-chip-group
            v-model="selectedCategory"
            selected-class="category-selected"
            mandatory
            class="justify-center"
          >
            <v-chip
              v-for="category in categories"
              :key="category.value"
              :value="category.value"
              class="category-chip"
              variant="text"
              @click="handleCategoryClick(category)"
              :class="{ 'category-selected': article?.category === category.value }"
            >
              {{ category.text }}
            </v-chip>
          </v-chip-group>
        </div>
        <div class="search-section">
          <v-text-field
            v-model="searchQuery"
            placeholder="검색어를 입력하세요"
            append-inner-icon="mdi-magnify"
            variant="outlined"
            density="compact"
            class="search-field"
            hide-details
            @keyup.enter="searchNews"
            @click:append-inner="searchNews"
          ></v-text-field>
        </div>
      </div>
    </div>

    <!-- 스크롤 시 나타나는 타이틀바 -->
    <div class="scroll-header" :class="{ 'visible': isScrolled }">
      <div class="header-content">
        <router-link to="/" class="logo-small">
          <img src="@/assets/logo.png" alt="Logo" />
        </router-link>
        <h1 class="header-title">{{ article?.title || '' }}</h1>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
      <span class="ml-3">기사를 불러오는 중...</span>
    </div>
    
    <!-- 에러 상태 -->
    <div v-else-if="!article" class="error">
      <v-icon color="error" size="large">mdi-alert-circle</v-icon>
      <span class="ml-3">기사를 불러올 수 없습니다.</span>
    </div>
    
    <!-- 기사  -->
    <div v-else>
      <!-- 왼쪽 사이드 버튼 -->
      <div class="side-buttons">
        <v-btn icon class="mb-4" @click="scrollToTop">
          <v-icon>mdi-arrow-up</v-icon>
        </v-btn>
        <v-btn icon @click="scrollToComments">
          <v-icon>mdi-comment</v-icon>
        </v-btn>
      </div>

      <!-- 메인 컨텐츠 -->
      <div class="news-content-wrapper">
        <div class="main-content">
          <div class="article-header">
            <div class="category">{{ article.category }}</div>
            <h1 class="title">{{ article.title }}</h1>
            <div class="article-meta">
              <div class="author-info">
                <span class="author-email">{{ getAuthorEmail(article.authors) }}</span>
                <span class="author-name">{{ getAuthorName(article.authors) }}</span>
              </div>
              <span class="time">{{ formatDate(article.time) }}</span>
            </div>
          </div>

          <!-- 기사 본문 -->
          <div class="article-content">
            <template v-for="(item, index) in sortedContents" :key="index">
              <!-- 텍스트 컨텐츠 -->
              <p v-if="item.type === 'text'" class="content-text">
                {{ item.content }}
              </p>
              <!-- 이미지 컨텐츠 -->
              <div v-else-if="item.type === 'image'" class="content-image">
                <v-img :src="item.src" :alt="item.caption" />
                <p class="image-caption">{{ item.caption }}</p>
              </div>
            </template>
          </div>

          <!-- 댓글 섹션 -->
          <div class="comments-section">
            <div class="like-section">
              <v-btn
                icon
                class="like-button"
                :class="{ 'liked': isLiked }"
                @click="handleLike"
              >
                <v-icon>{{ isLiked ? 'mdi-emoticon' : 'mdi-emoticon-outline' }}</v-icon>
              </v-btn>
              <span class="like-count">좋아요 {{ likeCount }}</span>
            </div>

            <div class="comments-header">
              <h2>댓글 {{ comments.length }}</h2>
            </div>
            
            <!-- 댓글 작성 폼 -->
            <div 
              class="comment-form"
              :class="{ 'not-logged-in': !isLoggedIn }"
            >
              <div class="comment-input">
                <v-text-field
                  v-model="newComment"
                  :placeholder="isLoggedIn ? '댓글을 입력해주세요' : '로그인 후 댓글 작성이 가능합니다'"
                  variant="plain"
                  hide-details
                  class="comment-field"
                  :readonly="!isLoggedIn"
                  @click="!isLoggedIn && router.push('/login')"
                ></v-text-field>
                <div v-if="isLoggedIn" class="comment-counter">{{ newComment.length }} / 400</div>
              </div>
              <div v-if="isLoggedIn" class="form-actions">
                <v-btn
                  variant="text"
                  class="cancel-btn"
                  @click="newComment = ''"
                >
                  취소
                </v-btn>
                <v-btn
                  class="submit-btn"
                  @click="handleSubmitComment"
                  :loading="submittingComment"
                >
                  등록
                </v-btn>
              </div>
            </div>

            <!-- 댓글 목록 -->
            <div class="comments-list">
              <div v-for="comment in comments" :key="comment.id" class="comment-item">
                <div class="comment-header">
                  <span class="comment-author">{{ comment.username }}</span>
                  <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
                </div>
                <div class="comment-text">{{ comment.text }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 우측 챗봇 버튼 및 창 -->
        <div class="chatbot-container">
          <!-- 챗봇 토글 버튼 -->
          <v-btn
            icon
            class="chatbot-toggle"
            @click="toggleChatbot"
            :class="{ 'active': isChatbotOpen }"
          >
            <v-icon>mdi-robot</v-icon> 
          </v-btn>

          <!-- 챗봇 창 -->
          <div class="chatbot-section" :class="{ 'open': isChatbotOpen }" ref="chatbotSection">
            <div class="chatbot-header">
              <h3>뉴스 GPT</h3>
              <div class="header-actions">
                <v-btn icon size="small" @click="toggleChatbot">
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </div>
            </div>
            
            <!-- 리사이즈 핸들 부분 수정 -->
            <div class="resize-handle top" @mousedown="(e) => startResize('top', e)"></div>
            <div class="resize-handle right" @mousedown="(e) => startResize('right', e)"></div>
            <div class="resize-handle bottom" @mousedown="(e) => startResize('bottom', e)"></div>
            <div class="resize-handle left" @mousedown="(e) => startResize('left', e)"></div>
            <div class="resize-handle top-left" @mousedown="(e) => startResize('top-left', e)"></div>
            <div class="resize-handle top-right" @mousedown="(e) => startResize('top-right', e)"></div>
            <div class="resize-handle bottom-left" @mousedown="(e) => startResize('bottom-left', e)"></div>
            <div class="resize-handle bottom-right" @mousedown="(e) => startResize('bottom-right', e)"></div>
            
            <div class="chat-messages" ref="chatMessagesRef">
              <div v-for="(msg, index) in chatMessages" :key="index" 
                   :class="['chat-message', msg.type]">
                <v-card
                  :class="['message-card', msg.type]"
                  elevation="0"
                  rounded="lg"
                >
                  <v-card-text 
                    class="message-content"
                    v-html="msg.type === 'bot' ? marked(msg.text) : msg.text"
                  ></v-card-text>
                </v-card>
              </div>
              <!-- 로딩 애니메이션 추가 -->
              <div v-if="isLoading" class="chat-message bot">
                <v-card class="message-card bot loading-message" elevation="0" rounded="lg">
                  <v-card-text class="message-content">
                    <v-progress-circular
                      indeterminate
                      color="rgba(147, 80, 255, 0.8)"
                      size="20"
                      width="2"
                    ></v-progress-circular>
                    <span class="loading-text">답변 생성 중...</span>
                  </v-card-text>
                </v-card>
              </div>
            </div>
            
            <div class="chat-input">
              <v-text-field
                v-model="chatInput"
                placeholder="질문을 입력하세요"
                @keyup.enter="sendMessage"
                append-inner-icon="mdi-send"
                @click:append-inner="sendMessage"
                density="compact"
                variant="outlined"
                hide-details
                :disabled="isLoading"
              ></v-text-field>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import LogoComponent from '@/components/LogoComponent.vue';
import NavBarComponent from '@/components/NavBarComponent.vue';
import apiClient from '@/api';
import { useRouter } from 'vue-router';  // router 추가
import { useUserStore } from '@/stores/user';
import { marked } from 'marked';

const router = useRouter();
const userStore = useUserStore();

const props = defineProps({
  id: {
    type: String,
    required: true
  }
});

const article = ref(null);
const scrollProgress = ref(0);
const comments = ref([]);
const newComment = ref('');
const submittingComment = ref(false);
const chatMessages = ref([]);
const chatInput = ref('');
const loading = ref(true);
const isScrolled = ref(false);
const searchQuery = ref('');
const selectedCategory = ref('all');
const isChatbotOpen = ref(false);
const isLiked = ref(false);
const likeCount = ref(0);
const isLoggedIn = computed(() => userStore.isLoggedIn);
const isLoading = ref(false);
const chatbotSection = ref(null);
const isResizing = ref(false);
const resizeDirection = ref('');
const startPos = ref({ x: 0, y: 0 });
const startSize = ref({ width: 0, height: 0 });

// marked 설정
marked.setOptions({
  breaks: true,  // \n을 <br>로 변환
  gfm: true,     // GitHub Flavored Markdown 활성화
});

// 유틸리티 함수들
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getAuthorEmail = (authors) => {
  if (!authors || !authors.length) return '';
  return authors[0].email || '';
};

const getAuthorName = (authors) => {
  if (!authors || !authors.length) return '';
  return authors[0].name || '';
};

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const scrollToComments = () => {
  const commentsSection = document.querySelector('.comments-section');
  if (commentsSection) {
    commentsSection.scrollIntoView({ behavior: 'smooth' });
  }
};

// 스크롤 프로그레스 계산
const calculateScrollProgress = () => {
  const windowHeight = window.innerHeight;
  const documentHeight = document.documentElement.scrollHeight - windowHeight;
  const scrolled = window.scrollY;
  scrollProgress.value = (scrolled / documentHeight) * 100;
};

// 컨텐츠 정렬
const sortedContents = computed(() => {
  if (!article.value) return [];
  
  const images = article.value.images || [];
  const texts = article.value.contents || [];
  
  const allContents = [
    ...images.map(img => ({
      type: 'image',
      src: img.src,
      caption: img.caption,
      refid: img.refid
    })),
    ...texts.map(text => ({
      type: 'text',
      content: text.text,
      refid: text.refid
    }))
  ].sort((a, b) => a.refid - b.refid);
  
  return allContents;
});

// 기사 데이터 가져오기
const fetchArticle = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get(`/news/${props.id}/`);
    article.value = response.data;
  } catch (error) {
    console.error('기사 로딩 실패:', error.response || error);
    article.value = null;
  } finally {
    loading.value = false;
  }
};

// 챗봇 메시지 전송
const sendMessage = async () => {
  if (!chatInput.value.trim() || isLoading.value) return;

  const userMessage = chatInput.value;
  chatMessages.value.push({ type: 'user', text: userMessage });
  chatInput.value = '';
  isLoading.value = true;

  try {
    const response = await apiClient.post(`/news/${props.id}/chatbot/`, {
      question: userMessage
    });
    
    if (response.data.answer) {
      chatMessages.value.push({ type: 'bot', text: response.data.answer });
    } else {
      throw new Error('응답에 답변이 없습니다.');
    }
    
  } catch (error) {
    console.error('챗봇 응답 실패:', error);
    let errorMessage = '죄송합니다. 오류가 발생했습니다.';
    
    if (error.response?.data?.error) {
      errorMessage = error.response.data.error;
    }
    
    chatMessages.value.push({ 
      type: 'bot', 
      text: errorMessage
    });
  } finally {
    isLoading.value = false;
    // 채팅 메시지 영역 스크롤
    nextTick(() => {
      const chatMessagesEl = chatMessagesRef.value;
      if (chatMessagesEl) {
        chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
      }
    });
  }
};

// 스크롤 이벤트 핸들러 수정
const handleScroll = () => {
  // 스크롤 프로그레스 계산
  const windowHeight = window.innerHeight;
  const documentHeight = document.documentElement.scrollHeight - windowHeight;
  const scrolled = window.scrollY;
  scrollProgress.value = (scrolled / documentHeight) * 100;

  // 스크롤 위치에 따라 헤더 변경
  isScrolled.value = scrolled > 100;
};

// 카테고리 매핑 객체 추가
const categoryToPath = {
  '전체': '',
  '경제': 'economy',
  '기업': 'business',
  '정치': 'politics',
  '사회': 'society',
  '국제': 'international',
  '문화': 'culture',
  'IT·과학': 'it-science'
};

// 카테고리 데이터 수정
const categories = [
  { text: '전체', value: 'all' },
  { text: '기업', value: 'business' },
  { text: '정치', value: 'politics' },
  { text: '경제', value: 'economy' },
  { text: '증권', value: 'stock' },
  { text: '사회', value: 'society' },
  { text: '국제', value: 'international' },
  { text: '문화', value: 'culture' },
  { text: 'IT·과학', value: 'it-science' }
];

const searchNews = () => {
  if (searchQuery.value.trim()) {
    router.push({
      path: '/',
      query: { search: searchQuery.value }
    });
  }
};

const toggleChatbot = () => {
  isChatbotOpen.value = !isChatbotOpen.value;
};

// 좋아요 처리 함수
const handleLike = () => {
  if (!isLoggedIn.value) {
    router.push('/login');
    return;
  }
  isLiked.value = !isLiked.value;
  likeCount.value += isLiked.value ? 1 : -1;
};

// 댓글 관련 함수들
const fetchComments = async () => {
  try {
    const response = await apiClient.get(`/news/${props.id}/comments/`);
    comments.value = response.data;
  } catch (error) {
    console.error('댓글을 불러오는데 실패했습니다:', error);
  }
};

const handleSubmitComment = async () => {
  if (!isLoggedIn.value) {
    router.push('/login');
    return;
  }
  
  if (!newComment.value.trim()) return;
  
  submittingComment.value = true;
  try {
    await apiClient.post(`/news/${props.id}/comments/create/`, {
      text: newComment.value
    });
    
    // 댓글 작성 후 목록 새로고침
    await fetchComments();
    newComment.value = '';
  } catch (error) {
    console.error('댓글 작성에 실패했습니다:', error);
  } finally {
    submittingComment.value = false;
  }
};

// 카테고리 클릭 핸들러 수정
const handleCategoryClick = (category) => {
  if (category.value === 'all') {
    router.push('/news');
  } else {
    router.push(`/news/category/${category.value}`);
  }
};

const goToNewsDetail = (article) => {
  router.push({
    name: 'NewsDetail',
    params: { id: article.id }
  });
};

// ref 추가
const chatMessagesRef = ref(null);

// 리사이즈 시작
const startResize = (direction, e) => {
  e.preventDefault(); // 이벤트 기본 동작 방지
  isResizing.value = true;
  resizeDirection.value = direction;
  
  const chatbot = chatbotSection.value;
  startPos.value = {
    x: e.clientX,
    y: e.clientY
  };
  startSize.value = {
    width: chatbot.offsetWidth,
    height: chatbot.offsetHeight
  };
  
  document.addEventListener('mousemove', handleResize);
  document.addEventListener('mouseup', stopResize);
};

// 리사이즈 처리
const handleResize = (e) => {
  if (!isResizing.value) return;
  
  const chatbot = chatbotSection.value;
  const deltaX = e.clientX - startPos.value.x;
  const deltaY = e.clientY - startPos.value.y;
  
  const minWidth = 280;
  const maxWidth = 500;
  const minHeight = 300;
  const maxHeight = 800;
  
  let newWidth = startSize.value.width;
  let newHeight = startSize.value.height;
  
  switch (resizeDirection.value) {
    case 'right':
      newWidth = startSize.value.width + deltaX;
      break;
    case 'left':
      newWidth = startSize.value.width - deltaX;
      break;
    case 'top':
      newHeight = startSize.value.height - deltaY;
      break;
    case 'bottom':
      newHeight = startSize.value.height + deltaY;
      break;
    case 'top-right':
      newWidth = startSize.value.width + deltaX;
      newHeight = startSize.value.height - deltaY;
      break;
    case 'top-left':
      newWidth = startSize.value.width - deltaX;
      newHeight = startSize.value.height - deltaY;
      break;
    case 'bottom-right':
      newWidth = startSize.value.width + deltaX;
      newHeight = startSize.value.height + deltaY;
      break;
    case 'bottom-left':
      newWidth = startSize.value.width - deltaX;
      newHeight = startSize.value.height + deltaY;
      break;
  }
  
  // 크기 제한 적용
  newWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);
  newHeight = Math.min(Math.max(newHeight, minHeight), maxHeight);
  
  chatbot.style.width = `${newWidth}px`;
  chatbot.style.height = `${newHeight}px`;
};

// 리사이즈 종료
const stopResize = () => {
  isResizing.value = false;
  document.removeEventListener('mousemove', handleResize);
  document.removeEventListener('mouseup', stopResize);
};

onMounted(() => {
  fetchArticle();
  fetchComments();  // 댓글 목록 불러오기 추가
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
.news-detail-page {
  background-color: #000000;
  min-height: 100vh;
  padding-top: 80px;
  color: white;
}

.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 1920px;
  height: 80px;
  background-color: #000000;
  z-index: 1000;
  border-bottom: 1px solid #333;
}

.top-section {
  position: fixed;
  top: 80px;
  left: 0;
  width: 1920px;
  background: #000000;
  z-index: 100;
  padding: 10px 0;
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: 1px solid #333;
}

.category-section {
  width: 800px;
  display: flex;
  justify-content: center;
  margin-left: -660px;
}

.search-section {
  position: absolute;
  right: 640px;
  width: 220px;
}

.search-field {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.search-field :deep(.v-field__input) {
  color: white !important;
}

.search-field :deep(.v-field__outline) {
  color: #333 !important;
}

.search-field :deep(.v-field__append-inner) {
  cursor: pointer;
  color: #888;
}

.search-field :deep(.v-field__append-inner:hover) {
  color: white;
}

.category-chip {
  color: #888 !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  margin: 0 15px !important;
  font-family: 'AppleSDGothicNeoL', sans-serif !important;
}

.category-selected {
  color: white !important;
  background: transparent !important;
  font-weight: 700 !important;
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
}

.side-buttons, .chatbot-container {
  position: fixed;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1000;
}

.side-buttons {
  left: calc((100% - 1200px) / 2 - 80px);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chatbot-container {
  right: calc((100% - 1200px) / 2 - 80px);
  height: 120px;
}

.chatbot-toggle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff !important;
}

.chatbot-toggle:hover {
  background: rgba(255, 255, 255, 0.2) !important;
}

.chatbot-toggle.active {
  background: #4a9eff !important;
  border-color: #4a9eff;
}

.chatbot-section {
  position: fixed;
  right: -600px;
  width: 280px;
  height: 500px;
  top: 100%;
  transform: translateY(-50%);
  background: rgba(20, 20, 20, 0.95);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: right 0.3s ease, height 0.3s ease;
  display: flex;
  flex-direction: column;
  font-family: 'AppleSDGothicNeoB', sans-serif;
  min-height: 300px;
  max-height: 800px;
  resize: vertical;
}

.chatbot-section.open {
  right: -40px;
}

.chatbot-header {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px 12px 0 0;
  display: flex;
  justify-content: center;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.chatbot-header h3 {
  color: #fff;
  font-size: 16px;
  font-family: 'AppleSDGothicNeoB', sans-serif;
  margin: 0;
  text-align: center;
}

.chatbot-header .v-btn {
  min-width: 24px !important;
  width: 24px;
  height: 24px;
  color: #888;
}

.header-actions {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scrollbar-width: thin;
  scrollbar-color: rgba(147, 80, 255, 0.5) rgba(255, 255, 255, 0.1);
}

.chat-message {
  margin-bottom: 16px;
  max-width: 85%;
  display: flex;
  flex-direction: column;
}

.chat-message.user {
  margin-left: auto;
  align-items: flex-end;
}

.chat-message.bot {
  margin-right: auto;
  align-items: flex-start;
}

.message-card {
  position: relative;
  margin: 0;
  max-width: 100%;
}

.message-card.user {
  background: rgba(147, 80, 255, 0.8) !important;
  border-bottom-right-radius: 4px !important;
}

.message-card.bot {
  background: rgba(147, 80, 255, 0.2) !important;
  border-bottom-left-radius: 4px !important;
}

.message-content {
  padding: 8px 12px !important;
  color: white !important;
  font-size: 14px;
  line-height: 1.4;
  word-break: break-word;
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
}

/* 말풍선 꼬리 효과 */
.message-card.user::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: -8px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-left-color: rgba(147, 80, 255, 0.8);
  border-right: 0;
  border-bottom: 0;
}

.message-card.bot::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: -8px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-right-color: rgba(147, 80, 255, 0.2);
  border-left: 0;
  border-bottom: 0;
}

/* 봇 메시지 내용 색상 조정 */
.message-card.bot .message-content {
  color: rgba(255, 255, 255, 0.9) !important;
}

.chat-input {
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0 0 12px 12px;
}

.chat-input :deep(.v-field) {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.chat-input :deep(.v-field__input) {
  color: #fff !important;
  min-height: 36px;
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
}

.chat-input :deep(.v-field__append-inner) {
  color: rgba(147, 80, 255, 0.8) !important;
  cursor: pointer;
}

.chat-input :deep(.v-field__append-inner:hover) {
  color: rgba(147, 80, 255, 1) !important;
}

.chat-input :deep(.v-field--focused) {
  border-color: rgba(147, 80, 255, 0.5) !important;
}

.chat-input :deep(.v-field__outline) {
  color: rgba(147, 80, 255, 0.3) !important;
}

.chat-input :deep(.v-field__outline--focused) {
  color: rgba(147, 80, 255, 0.5) !important;
}

.comments-section {
  margin-top: 60px;
  padding-top: 40px;
  margin-bottom: 80px;
}

.like-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.like-button {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff !important;
}

.like-button:hover {
  background: rgba(255, 255, 255, 0.2) !important;
}

.like-button.liked {
  background: #4a9eff !important;
  border-color: #4a9eff;
}

.like-count {
  color: #fff;
  font-family: 'AppleSDGothicNeoL', sans-serif;
  font-size: 14px;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.comments-header h2 {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 18px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-form {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.03);
}

.comment-form.not-logged-in {
  cursor: pointer;
}

.comment-form.not-logged-in .comment-field {
  cursor: pointer;
}

.comment-input {
  position: relative;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.comment-field {
  font-family: 'AppleSDGothicNeoL', sans-serif;
}

.comment-field :deep(.v-field__input) {
  color: #fff !important;
  font-size: 14px;
  padding: 0;
}

.comment-field :deep(.v-field__input::placeholder) {
  color: rgba(255, 255, 255, 0.5) !important;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding: 8px;
  gap: 8px;
}

.cancel-btn {
  color: #888 !important;
  font-family: 'AppleSDGothicNeoL', sans-serif;
  font-size: 14px;
}

.submit-btn {
  background: #000 !important;
  color: #fff !important;
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 14px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  height: 32px;
  min-width: 60px;
}

.submit-btn:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.loading {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1002;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  color: #333;
}

.error {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1002;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  color: #ff0000;
}

.scroll-progress-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  z-index: 1001;
}

.scroll-progress-bar {
  height: 100%;
  background: #4a9eff;
  width: 0;
  transition: width 0.1s ease;
}

.header-area {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  transition: transform 0.3s ease;
  background-color: #000;
}

.header-area.hidden {
  transform: translateY(-200px);
}

.main-nav {
  width: 100%;
  height: 80px;
  background-color: #000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.nav-left .logo {
  height: 40px;
}

.nav-left .logo img {
  height: 100%;
}

.nav-center {
  display: flex;
  gap: 40px;
}

.nav-link {
  color: #fff;
  text-decoration: none;
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 16px;
}

.nav-link.active {
  color: #4a9eff;
}

.nav-right {
  width: 300px;
}

.search-container {
  width: 100%;
}

.search-container :deep(.v-field) {
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.1);
}

.search-container :deep(.v-field__input) {
  color: #fff;
  min-height: 40px;
  padding: 0 16px;
}

.search-container :deep(.v-field__prepend-inner) {
  padding-inline-start: 12px;
}

.category-bar {
  width: 100%;
  height: 48px;
  background-color: #000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.category-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 32px;
  padding: 0 20px;
}

.category-link {
  color: #888;
  text-decoration: none;
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 15px;
  transition: color 0.2s ease;
}

.category-link:hover {
  color: #fff;
}

.category-link.active {
  color: #4a9eff;
}

.scroll-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 80px;
  background-color: #000;
  z-index: 999;
  transform: translateY(-100%);
  transition: transform 0.3s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.scroll-header.visible {
  transform: translateY(0);
}

.header-content {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  position: relative;
}

.logo-small {
  height: 80px;
  display: flex;
  align-items: center;
  position: absolute;
  left: 20px;
  padding: 0px 0;
}

.logo-small img {
  height: 100%;
  object-fit: contain;
}

.header-title {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  color: #fff;
  font-size: 20px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 800px;
  line-height: 1.4;
  margin: 0 auto;
  text-align: center;
  padding: 0 100px;
}

/* 사이드 버튼 스타일 수정 */
.side-buttons {
  position: fixed;
  left: calc((100% - 1200px) / 2 - 80px);
  top: 50%;
  transform: translateY(-50%);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.side-buttons .v-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff !important;
}

.side-buttons .v-btn:hover {
  background: rgba(255, 255, 255, 0.2) !important;
}

/* 메인 컨츠 여백 조정 */
.news-content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 168px;
  display: flex;
  justify-content: center;
  position: relative;
}

.main-content {
  width: 800px;
  padding: 0 20px;
  margin: 0 auto;
}

/* 기사 내용 스타일 복원 */
.article-header {
  margin-bottom: 40px;
}

.category {
  color: #4a9eff;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
  font-family: 'AppleSDGothicNeoB', sans-serif;
}

.title {
  font-size: 36px;
  font-weight: 700;
  line-height: 1.4;
  margin-bottom: 20px;
  color: #fff;
  font-family: 'AppleSDGothicNeoB', sans-serif;
}

.article-meta {
  margin-top: 20px;
  padding-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.author-info {
  margin-bottom: 8px;
}

.author-email {
  font-family: 'AppleSDGothicNeoL', sans-serif;
  color: #888;
  margin-right: 10px;
}

.author-name {
  font-family: 'AppleSDGothicNeoL', sans-serif;
  color: #fff;
}

.time {
  font-family: 'AppleSDGothicNeoL', sans-serif;
  color: #888;
  font-size: 14px;
}

.content-text {
  font-family: 'AppleSDGothicNeoL', sans-serif;
  font-size: 16px;
  line-height: 1.8;
  margin-bottom: 20px;
  color: #fff;
}

.content-image {
  margin: 30px 0;
}

.image-caption {
  color: #888;
  font-size: 14px;
  text-align: center;
  margin-top: 10px;
  font-family: 'AppleSDGothicNeoL', sans-serif;
}

/* 채팅 메시지 영역 스크롤바 스타일링 */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(147, 80, 255, 0.5);
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(147, 80, 255, 0.7);
}

/* 마크다운 스타일 */
.message-content :deep(p) {
  margin: 0;
}

.message-content :deep(strong) {
  color: #fff;
  font-weight: 700;
}

.message-content :deep(code) {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

.message-content :deep(ul), 
.message-content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-content :deep(li) {
  margin: 4px 0;
}

.message-content :deep(blockquote) {
  border-left: 3px solid rgba(255, 255, 255, 0.3);
  margin: 8px 0;
  padding-left: 12px;
}

/* 챗봇 전체 폰트 스타일 */
.chatbot-section {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  /* ... 기존 스타일 유지 ... */
}

/* 메시지 내용 폰트 스타일 */
.message-content {
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
  /* ... 기존 스타일 유지 ... */
}

/* 입력 필드 폰트 스타일 */
.chat-input :deep(.v-field__input) {
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
  /* ... 기존 스타일 유지 ... */
}

/* 마크다운 스타일 폰트 수정 */
.message-content :deep(p),
.message-content :deep(strong),
.message-content :deep(li),
.message-content :deep(blockquote) {
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
}

/* 코드 스타일만 모노스페이스 폰트 유지 */
.message-content :deep(code) {
  font-family: monospace;
  /* ... 기존 스타일 유지 ... */
}

/* 플레이스홀더 텍스트 폰트 스타일 */
.chat-input :deep(.v-field__input::placeholder) {
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
}

/* 스타일 추가 */
.resize-handle {
  position: absolute;
  background: transparent;
  z-index: 1000;
}

.resize-handle.top {
  top: -3px;
  left: 0;
  width: 100%;
  height: 6px;
  cursor: ns-resize;
}

.resize-handle.right {
  top: 0;
  right: -3px;
  width: 6px;
  height: 100%;
  cursor: ew-resize;
}

.resize-handle.bottom {
  bottom: -3px;
  left: 0;
  width: 100%;
  height: 6px;
  cursor: ns-resize;
}

.resize-handle.left {
  top: 0;
  left: -3px;
  width: 6px;
  height: 100%;
  cursor: ew-resize;
}

.resize-handle.top-left {
  top: -3px;
  left: -3px;
  width: 10px;
  height: 10px;
  cursor: nw-resize;
}

.resize-handle.top-right {
  top: -3px;
  right: -3px;
  width: 10px;
  height: 10px;
  cursor: ne-resize;
}

.resize-handle.bottom-left {
  bottom: -3px;
  left: -3px;
  width: 10px;
  height: 10px;
  cursor: sw-resize;
}

.resize-handle.bottom-right {
  bottom: -3px;
  right: -3px;
  width: 10px;
  height: 10px;
  cursor: se-resize;
}

.resize-handle:hover {
  background: rgba(147, 80, 255, 0.3);
}

.loading-message {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-text {
  margin-left: 8px;
  color: rgba(255, 255, 255, 0.7);
}

/* 채팅창 transition 수정 */
.chatbot-section {
  transition: right 0.3s ease, height 0.3s ease;
  min-height: 300px;
  max-height: 800px;
  resize: vertical;
}

/* 입력창 비활성화 스타일 */
.chat-input :deep(.v-field--disabled) {
  opacity: 0.7;
}
</style> 