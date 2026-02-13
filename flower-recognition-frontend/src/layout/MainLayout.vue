<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <h1 class="app-title">🌸 花世界</h1>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          class="app-menu"
          router
        >
          <el-menu-item index="/index">首页</el-menu-item>
          <el-menu-item index="/knowledge">知识库</el-menu-item>
          <el-menu-item index="/qa">智能问答</el-menu-item>
          <el-menu-item index="/history">历史记录</el-menu-item>
          <el-menu-item index="/profile">个人中心</el-menu-item>
        </el-menu>
      </div>
    </el-header>
    <el-main class="app-main">
      <RouterView />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, RouterView, useRouter } from 'vue-router'
import { useStore } from '@/stores'
import { get } from '@/net'

const route = useRoute()
const router = useRouter()
const store = useStore()
const activeMenu = ref('/index')

const updateActiveMenu = () => {
  activeMenu.value = route.path
}

// 监听路由变化更新 activeMenu
watch(() => route.path, () => {
  updateActiveMenu()
}, { immediate: true })

onMounted(() => {
  if (!store.auth.user) {
    get('/api/user/me', (data) => {
      store.auth.user = data
    }, () => {
      store.auth.user = null
      router.push('/')
    })
  }
})

// 监听路由变化
onMounted(() => {
  window.addEventListener('popstate', updateActiveMenu)
})

onUnmounted(() => {
  window.removeEventListener('popstate', updateActiveMenu)
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  width: 100vw;
  background-color: #F5F5F5;
}

.app-header {
  background-color: #4CAF50;
  padding: 0 32px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 72px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  height: 100%;
}

.app-title {
  color: white;
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 28px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.app-menu {
  background: transparent;
  border: none;
  flex: 1;
  justify-content: flex-end;
  margin-left: 48px;
  overflow-x: auto;
}

.app-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.9);
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 18px;
  padding: 0 24px;
  border-radius: 8px;
  transition: all 0.3s;
  white-space: nowrap;
}

.app-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.app-menu .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.3);
  color: white;
  font-weight: 600;
}

.app-main {
  padding: 32px 24px;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  min-height: calc(100vh - 72px);
}

/* 响应式布局 - 大屏幕 (>1600px) */
@media (min-width: 1600px) {
  .app-main {
    padding: 40px 32px;
  }
}

/* 响应式布局 - 中等屏幕 (≤1400px) */
@media (max-width: 1400px) {
  .app-header {
    padding: 0 28px;
    height: 68px;
  }

  .app-title {
    font-size: 26px;
  }

  .app-menu {
    margin-left: 40px;
  }

  .app-menu .el-menu-item {
    font-size: 17px;
    padding: 0 22px;
  }

  .app-main {
    padding: 28px 20px;
    min-height: calc(100vh - 68px);
  }
}

/* 响应式布局 - 小屏幕 (≤1200px) */
@media (max-width: 1200px) {
  .app-header {
    padding: 0 24px;
    height: 64px;
  }

  .app-title {
    font-size: 24px;
  }

  .app-menu {
    margin-left: 32px;
  }

  .app-menu .el-menu-item {
    font-size: 16px;
    padding: 0 20px;
  }

  .app-main {
    padding: 24px 16px;
    min-height: calc(100vh - 64px);
  }
}

/* 响应式布局 - 平板 (≤992px) */
@media (max-width: 992px) {
  .app-header {
    padding: 0 20px;
    height: 60px;
  }

  .app-title {
    font-size: 22px;
  }

  .app-menu {
    margin-left: 24px;
  }

  .app-menu .el-menu-item {
    font-size: 15px;
    padding: 0 16px;
  }

  .app-main {
    padding: 20px 16px;
    min-height: calc(100vh - 60px);
  }
}

/* 响应式布局 - 移动端 (≤768px) */
@media (max-width: 768px) {
  .app-header {
    padding: 0 16px;
    height: 56px;
  }

  .header-content {
    gap: 16px;
  }

  .app-title {
    font-size: 20px;
  }

  .app-menu {
    margin-left: 16px;
  }

  .app-menu .el-menu-item {
    font-size: 14px;
    padding: 0 12px;
  }

  .app-main {
    padding: 16px 12px;
    min-height: calc(100vh - 56px);
  }
}

/* 响应式布局 - 小屏移动端 (≤480px) */
@media (max-width: 480px) {
  .app-header {
    padding: 0 12px;
    height: 52px;
  }

  .header-content {
    gap: 8px;
  }

  .app-title {
    font-size: 18px;
    gap: 6px;
  }

  .app-menu {
    margin-left: 8px;
  }

  .app-menu .el-menu-item {
    font-size: 13px;
    padding: 0 8px;
  }

  .app-main {
    padding: 12px 8px;
    min-height: calc(100vh - 52px);
  }
}

/* 超小屏幕 (≤360px) */
@media (max-width: 360px) {
  .app-header {
    padding: 0 8px;
    height: 48px;
  }

  .app-title {
    font-size: 16px;
  }

  .app-menu .el-menu-item {
    font-size: 12px;
    padding: 0 6px;
  }

  .app-main {
    padding: 10px 6px;
    min-height: calc(100vh - 48px);
  }
}
</style>
