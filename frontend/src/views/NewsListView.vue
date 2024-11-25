<template>
  <div class="news-page">
    <div class="fixed-header">
      <LogoComponent />
      <NavBarComponent />
    </div>

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

    <div class="news-content">
      <div v-if="searchQuery && articles.length === 0" class="no-results">
        <v-icon size="64" color="grey">mdi-file-search-outline</v-icon>
        <p>검색 결과가 없습니다.</p>
      </div>

      <template v-else>
        <div 
          v-if="articles[0]" 
          class="main-news"
          @click="goToNewsDetail(articles[0])"
        >
          <div class="main-news-image">
            <v-img
              v-if="articles[0].images && articles[0].images.length > 0"
              :src="articles[0].images[0].src"
              height="100%"
              cover
            ></v-img>
          </div>
          <div class="main-news-info">
            <div class="news-category">{{ articles[0].category }}</div>
            <h2 class="main-news-title">{{ articles[0].title }}</h2>
            <div class="news-time">{{ getTimeAgo(articles[0].time) }}</div>
          </div>
        </div>

        <div class="sub-news-grid">
          <div
            v-for="article in articles.slice(1)"
            :key="article.id"
            class="news-item"
            @click="goToNewsDetail(article)"
          >
            <div class="news-text">
              <div class="news-category">{{ article.category }}</div>
              <h3 class="news-title">{{ article.title }}</h3>
              <p class="news-content-preview">{{ getContentPreview(article) }}</p>
              <div class="news-time">{{ getTimeAgo(article.time) }}</div>
            </div>
            <div class="news-image">
              <v-img
                v-if="article.images && article.images.length > 0"
                :src="article.images[0].src"
                height="120"
                width="180"
                cover
              ></v-img>
            </div>
          </div>
        </div>

        <div v-if="articles.length > 0" class="load-more-container">
          <v-btn
            class="load-more-btn"
            @click="loadMore"
            :loading="loading"
            color="primary"
            variant="outlined"
          >
            더보기
          </v-btn>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import LogoComponent from '@/components/LogoComponent.vue';
import NavBarComponent from '@/components/NavBarComponent.vue';
import { ref, onMounted, watch } from 'vue';
import apiClient from '@/api';

export default {
  name: 'NewsListView',
  components: {
    LogoComponent,
    NavBarComponent,
  },
  setup() {
    const articles = ref([])
    const loading = ref(false)
    const dialog = ref(false)
    const selectedArticle = ref(null)
    const selectedCategory = ref('all')
    const drawer = ref(false)
    const menuItems = ref([
      { 
        title: '오피니언',
        icon: 'mdi-newspaper',
        items: ['Pulse', 'MK China', 'MK밸리리더뉴스']
      },
      { 
        title: '프리미엄',
        icon: 'mdi-star',
        items: ['MK워클리연재', '매경e신문', '레이더M']
      },
      { 
        title: '재테크',
        icon: 'mdi-cash',
        items: ['마', '부동산', '시사 경제 용어']
      },
      { 
        title: '라이프',
        icon: 'mdi-heart',
        items: ['골프', 'Book', '여행']
      },
      { 
        title: '비즈니스',
        icon: 'mdi-briefcase',
        items: ['The Biz Times', '넷케이블레콤', 'KDX국데이터거래소']
      }
    ])

    const categories = ref([
      { text: '전체', value: 'all' },
      { text: '기업', value: '기업' },
      { text: '정치', value: '정치' },
      { text: '경제', value: '경제' },
      { text: '증권', value: '증권' },
      { text: '사회', value: '사회' },
      { text: '국제', value: '국제' },
      { text: '문화', value: '문화' },
      { text: 'IT·과학', value: 'IT·과학' }
    ])

    const page = ref(1)
    const limit = ref(8)
    const searchQuery = ref('')

    const fetchNews = async () => {
      loading.value = true
      try {
        console.log('Fetching news with category:', selectedCategory.value);
        const response = await apiClient.get('/news/', {
          params: {
            category: selectedCategory.value === 'all' ? '' : selectedCategory.value,
            limit: limit.value,
            offset: (page.value - 1) * limit.value,
            search: searchQuery.value
          }
        })
        if (page.value === 1) {
          articles.value = response.data
        } else {
          articles.value = [...articles.value, ...response.data]
        }
      } catch (error) {
        console.error('뉴스 데이터 로딩 실패:', error.response?.data || error)
      } finally {
        loading.value = false
      }
    }

    const loadMore = async () => {
      page.value += 1
      await fetchNews()
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatAuthors = (authors) => {
      if (!authors) return ''
      const authorList = JSON.parse(authors)
      return authorList.map(author => author.name).join(', ')
    }

    const showArticleDetail = (article) => {
      selectedArticle.value = article
      dialog.value = true
    }

    watch(selectedCategory, () => {
      page.value = 1
      searchQuery.value = ''
      fetchNews()
    })

    onMounted(() => {
      fetchNews()
    })

    const searchNews = async () => {
      if (searchQuery.value.trim()) {
        page.value = 1
        await fetchNews()
      }
    }

    return {
      articles,
      loading,
      categories,
      selectedCategory,
      formatDate,
      dialog,
      selectedArticle,
      formatAuthors,
      showArticleDetail,
      drawer,
      menuItems,
      loadMore,
      searchQuery,
      searchNews,
    }
  },
  methods: {
    getTimeAgo(dateString) {
      const now = new Date();
      const past = new Date(dateString);
      const diffInSeconds = Math.floor((now - past) / 1000);
      
      if (diffInSeconds < 60) {
        return '방금 전';
      } else if (diffInSeconds < 3600) {
        const minutes = Math.floor(diffInSeconds / 60);
        return `${minutes}분 전`;
      } else if (diffInSeconds < 86400) {
        const hours = Math.floor(diffInSeconds / 3600);
        return `${hours}시간 전`;
      } else {
        const days = Math.floor(diffInSeconds / 86400);
        return `${days}일 전`;
      }
    },
    goToNews(url) {
      window.open(url, '_blank');
    },
    getContentPreview(article) {
      if (article.contents && article.contents.length > 0) {
        const content = article.contents[0].text;
        return content.length > 100 ? content.slice(0, 100) + '...' : content;
      }
      return '';
    },
    goToNewsDetail(article) {
      this.$router.push({
        name: 'NewsDetail',
        params: { id: article.id }
      });
    }
  }
}
</script>

<style scoped>
@font-face {
  font-family: 'AppleSDGothicNeoL';
  src: url('@/assets/fonts/AppleSDGothicNeoL.ttf') format('truetype');
}

@font-face {
  font-family: 'AppleSDGothicNeoM';
  src: url('@/assets/fonts/AppleSDGothicNeoM.ttf') format('truetype');
}

@font-face {
  font-family: 'AppleSDGothicNeoB';
  src: url('@/assets/fonts/AppleSDGothicNeoB.ttf') format('truetype');
}

.news-page {
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

.news-content {
  max-width: 1200px;
  margin: 70px auto 0;
  padding: 20px;
}

.news-content-preview {
  color: #888;
  font-size: 14px;
  line-height: 1.6;
  margin: 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-family: 'AppleSDGothicNeoL', sans-serif;
}

.news-item {
  display: flex;
  justify-content: space-between;
  padding: 25px;
  background: #111111;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s ease;
  margin-bottom: 25px;
}

.news-item:hover {
  transform: translateY(-2px);
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

.news-category {
  color: #4a9eff;
  font-size: 14px;
  font-weight: 500;
  font-family: 'AppleSDGothicNeoL', sans-serif;
}

.news-title {
  font-size: 20px;
  font-weight: 600;
  margin: 10px 0;
  line-height: 1.4;
  color: white;
  font-family: 'AppleSDGothicNeoM', sans-serif;
}

.news-time {
  color: #888;
  font-size: 13px;
  font-family: 'AppleSDGothicNeoL', sans-serif;
}

.main-news {
  display: flex;
  margin-bottom: 40px;
  background: #111111;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.main-news-image {
  width: 35%;
  min-height: 400px;
}

.main-news-info {
  width: 65%;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.main-news-title {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.3;
  margin: 15px 0;
  color: white;
  font-family: 'AppleSDGothicNeoM', sans-serif;
}

.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  margin-bottom: 60px;
}

.load-more-btn {
  min-width: 200px;
  height: 48px;
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 16px;
  border: 1px solid #4a9eff;
  color: #4a9eff;
}

.load-more-btn:hover {
  background: rgba(74, 158, 255, 0.1);
}

@media (max-width: 960px) {
  .news-content {
    margin-left: 20px;
    margin-right: 20px;
  }
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
  color: #888;
  text-align: center;
}

.no-results p {
  margin-top: 20px;
  font-size: 18px;
  font-family: 'AppleSDGothicNeoL', sans-serif;
}
</style> 