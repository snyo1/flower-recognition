import { createRouter, createWebHistory } from 'vue-router'
import { useStore } from '@/stores/index'

const router = createRouter({
  history: createWebHistory('/hua-shi-jie/'),
  routes: [
    {
      path: '/hua-shi-jie/',
      name: 'welcome',
      component: () => import('@/views/WelcomeView.vue'),
      children: [
        {
          path: '',
          name: 'welcome-login',
          component: () => import('@/components/welcome/LoginPage.vue')
        }, {
          path: 'register',
          name: 'welcome-register',
          component: () => import('@/components/welcome/RegisterPage.vue')
        }, {
          path: 'forget',
          name: 'welcome-forget',
          component: () => import('@/components/welcome/ForgetPage.vue')
        }
      ]
    },
    {
      path: '/hua-shi-jie/index',
      component: () => import('@/layout/MainLayout.vue'),
      children: [
        {
          path: '',
          name: 'index',
          component: () => import('@/views/HomeView.vue')
        }
      ]
    },
    {
      path: '/hua-shi-jie/qa',
      component: () => import('@/layout/MainLayout.vue'),
      children: [
        {
          path: '',
          name: 'qa',
          component: () => import('@/views/QAView.vue')
        }
      ]
    },
    {
      path: '/hua-shi-jie/knowledge',
      component: () => import('@/layout/MainLayout.vue'),
      children: [
        {
          path: '',
          name: 'knowledge',
          component: () => import('@/views/KnowledgeView.vue')
        }
      ]
    },
    {
      path: '/hua-shi-jie/history',
      component: () => import('@/layout/MainLayout.vue'),
      children: [
        {
          path: '',
          name: 'history',
          component: () => import('@/views/HistoryView.vue')
        }
      ]
    },
    {
      path: '/hua-shi-jie/profile',
      component: () => import('@/layout/MainLayout.vue'),
      children: [
        {
          path: '',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/WelcomeView.vue') // Reusing welcome view or any view, logic will be in beforeEach
    }
  ],
})

router.beforeEach((to, from, next) => {
  const store = useStore()
  const token = localStorage.getItem('access_token')
  const isAuthed = !!(store.auth.user || token)

  // 1. 如果请求的是不存在的页面 (not-found 路由)
  if (to.name === 'not-found') {
    if (isAuthed) {
      return next('/hua-shi-jie/index')
    } else {
      return next('/hua-shi-jie/')
    }
  }

  // 2. 访问登录/注册相关页面
  const isWelcomePage = to.path === '/hua-shi-jie/' || to.path.startsWith('/hua-shi-jie/register') || to.path.startsWith('/hua-shi-jie/forget')
  
  if (isWelcomePage) {
    if (isAuthed) {
      return next('/hua-shi-jie/index')
    }
    return next()
  }

  // 3. 访问受保护页面 (非登录/注册页面)
  if (!isAuthed) {
    return next('/hua-shi-jie/')
  }

  return next()
})

export default router
