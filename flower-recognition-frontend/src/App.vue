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
          <el-menu-item index="/">首页</el-menu-item>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, RouterView } from 'vue-router'

const route = useRoute()
const activeMenu = ref('/')

const updateActiveMenu = () => {
  activeMenu.value = route.path
}

onMounted(() => {
  updateActiveMenu()
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
  min-height: 100vh;
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

<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Roboto', sans-serif;
  background-color: #F5F5F5;
  color: #333333;
}

#app {
  min-height: 100vh;
}

/* 全局样式覆盖 */
.el-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: none;
}

.el-button--primary {
  background-color: #4CAF50 !important;
  border-color: #4CAF50 !important;
  border-radius: 8px;
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 16px;
  padding: 12px 24px;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
}

.el-button--primary:hover {
  background-color: #43A047 !important;
  border-color: #43A047 !important;
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
}

.el-button--default {
  background-color: #E0E0E0;
  border-color: #E0E0E0;
  border-radius: 8px;
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 16px;
  padding: 12px 24px;
  color: #333333;
}

.el-button--default:hover {
  background-color: #D5D5D5;
  border-color: #D5D5D5;
}

.el-button.is-circle {
  background-color: #FFFFFF;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 8px;
}

.el-input__inner {
  border-radius: 8px;
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
}

.el-textarea__inner {
  border-radius: 8px;
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
}

.el-tag {
  border-radius: 6px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
}

.el-tag--success {
  background-color: #E8F5E9;
  border-color: #4CAF50;
  color: #4CAF50;
}

.el-tag--primary {
  background-color: #E3F2FD;
  border-color: #2196F3;
  color: #2196F3;
}

.el-tag--danger {
  background-color: #FFEBEE;
  border-color: #F44336;
  color: #F44336;
}

.el-card__header {
  background-color: #FFFFFF;
  border-bottom: 1px solid #E0E0E0;
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 18px;
  color: #333333;
  padding: 16px 20px;
}

.el-descriptions__label {
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 16px;
  color: #666666;
}

.el-descriptions__content {
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 16px;
  color: #333333;
}

/* 响应式全局组件样式 */
@media (max-width: 768px) {
  .el-button--primary,
  .el-button--default {
    font-size: 14px;
    padding: 10px 16px;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 14px;
  }

  .el-card__header {
    font-size: 16px;
    padding: 12px 16px;
  }

  .el-descriptions__label,
  .el-descriptions__content {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .el-button--primary,
  .el-button--default {
    font-size: 13px;
    padding: 8px 14px;
  }

  .el-input__inner,
  .el-textarea__inner {
    font-size: 13px;
  }

  .el-card__header {
    font-size: 15px;
    padding: 10px 12px;
  }

  .el-descriptions__label,
  .el-descriptions__content {
    font-size: 13px;
  }
}
</style>
