<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

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
