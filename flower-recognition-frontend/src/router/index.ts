import { createRouter, createWebHistory } from 'vue-router'
import { useStore } from '@/stores/index'
import { get } from '@/net'

const router = createRouter({
  history: createWebHistory(),
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
          component: () => import('@/views/HomeView.vue'),
          meta: { keepAlive: true }
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
          component: () => import('@/views/QAView.vue'),
          meta: { keepAlive: true }
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
          component: () => import('@/views/KnowledgeView.vue'),
          meta: { keepAlive: true }
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
          component: () => import('@/views/HistoryView.vue'),
          meta: { keepAlive: true }
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
          component: () => import('@/views/ProfileView.vue'),
          meta: { keepAlive: true }
        }
      ]
    },
    {
      path: '/admin',
      component: () => import('@/layout/MainLayout.vue'), // Using MainLayout as AdminLayout is not found
      meta: { requiresAuth: true, role: 'admin' }, // 权限元信息
      children: [
        { path: 'knowledge', name: 'AdminKnowledge', component: () => import('@/views/KnowledgeView.vue') }, // Reusing KnowledgeView for now
        { path: 'user', name: 'AdminUser', component: () => import('@/views/admin/UserManage.vue') }, // Assuming this path
        { path: 'feedback', name: 'AdminFeedback', component: () => import('@/views/admin/FeedbackManage.vue') }, // Assuming this path
        { path: 'comment', name: 'AdminComment', component: () => import('@/views/admin/CommentManage.vue') }, // Assuming this path
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      redirect: (to) => {
        const store = useStore()
        return store.auth.user ? '/index' : '/'
      }
    }
  ],
})

router.beforeEach(async (to, from, next) => {
  const store = useStore()
  const token = localStorage.getItem('access_token')

  // 如果 store 中没有用户信息但有 token，尝试初始化用户信息
  if (!store.auth.user && token) {
    try {
      // 这里的 get 是自定义的封装，它会自动带上 token
      await new Promise((resolve, reject) => {
        get('/api/user/me', (data) => {
          store.auth.user = data
          resolve(data)
        }, (msg, status) => {
          if (status === 401) {
            localStorage.removeItem('access_token')
          }
          reject(msg)
        })
      })
    } catch (e) {
      console.error('Failed to initialize user info:', e)
    }
  }

  const isAuthed = !!(store.auth.user)
  const userRole = store.auth.user ? store.auth.user.role : null // Assuming user role is available

  // Handle routes that require authentication
  if (to.meta.requiresAuth) {
    if (isAuthed) {
      // Check for role if specified in meta
      if (to.meta.role && userRole !== to.meta.role) {
        // If role doesn't match, redirect to index or an unauthorized page
        return next('/index') // Or a dedicated unauthorized page
      }
      return next() // Authenticated and authorized
    } else {
      // Not authenticated, redirect to login
      return next('/')
    }
  }

  // Handle welcome pages
  const isWelcomePage = to.path === '/' || to.path.startsWith('/register') || to.path.startsWith('/forget')
  if (isWelcomePage) {
    if (isAuthed) {
      return next('/index')
    }
    return next()
  }

  // For any other page, if not authenticated, redirect to login
  if (!isAuthed && to.path !== '/') { // Exclude '/' from this check to avoid double redirect
    return next('/')
  }

  return next()
})

export default router
