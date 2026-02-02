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
      path: '/hua-shi-jie/friends',
      component: () => import('@/layout/MainLayout.vue'),
      children: [
        {
          path: '',
          name: 'friends',
          component: () => import('@/views/FriendsView.vue')
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
      redirect: '/hua-shi-jie/'
    }
  ],
})

router.beforeEach((to, from, next) => {
  const store = useStore()
  const token = localStorage.getItem('access_token')
  const isAuthed = !!(store.auth.user || token)
  const protectedPrefixes = [
    '/hua-shi-jie/index',
    '/hua-shi-jie/qa',
    '/hua-shi-jie/friends',
    '/hua-shi-jie/knowledge',
    '/hua-shi-jie/history',
    '/hua-shi-jie/profile',
  ]

  if (to.path === '/hua-shi-jie/') {
    if (isAuthed) return next('/hua-shi-jie/index')
    return next()
  }

  if (!isAuthed && protectedPrefixes.some(p => to.path.startsWith(p))) {
    return next('/hua-shi-jie/')
  }

  return next()
})

export default router
