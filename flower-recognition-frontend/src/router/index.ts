import { createRouter, createWebHashHistory } from 'vue-router'
import { useStore } from '@/stores/index'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
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
      path: '/index',
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
      path: '/qa',
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
      path: '/knowledge',
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
      path: '/history',
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
      path: '/profile',
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
      redirect: '/'
    }
  ],
})

router.beforeEach((to, from, next) => {
  const store = useStore()
  const token = localStorage.getItem('access_token')
  
  if (to.name?.toString().startsWith('welcome-')) {
    if (store.auth.user || token) {
      next('/index')
    } else {
      next()
    }
  } else {
    if (store.auth.user || token) {
      next()
    } else {
      next('/')
    }
  }
})

export default router
