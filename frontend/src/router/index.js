import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import ChatbotView from '@/views/ChatbotView.vue'
import NewsListView from '@/views/NewsListView.vue'
import InterestListView from '@/views/InterestListView.vue'
import InterestDetailView from '@/views/InterestDetailView.vue'
import UserInitView from '@/views/UserInitView.vue'
import NewsDetailView from '@/views/NewsDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'Signup',
      component: SignupView
    },
    {
      path: '/chatbot',
      name: 'Chatbot',
      component: ChatbotView
    },
    {
      path: '/news',
      name: 'News',
      component: NewsListView
    },
    {
      path: '/interests',
      name: 'Interests',
      component: InterestListView
    },
    {
      path: '/interests/:ticker',
      name: 'InterestDetail',
      component: InterestDetailView,
      props: true
    },
    {
      path: '/user-init',
      name: 'UserInit',
      component: UserInitView
    },
    {
      path: '/news/:id',
      name: 'NewsDetail',
      component: NewsDetailView,
      props: true
    }
  ]
})

export default router
