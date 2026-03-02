<template>
  <div class="qa-page">
    <el-card class="chat-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">智能问答</span>
          <el-button class="header-btn" :icon="Clock" circle @click="clearHistory" />
        </div>
      </template>

      <div class="qa-layout">
        <!-- 对话窗口 -->
        <div class="chat-container" ref="chatContainer">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message', message.role]"
          >
            <div class="message-bubble">
              <div class="message-content">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.timestamp) }}</div>
            </div>
          </div>

          <div v-if="loading" class="message assistant">
            <div class="message-bubble loading">
              <el-icon class="is-loading" :size="20"><Loading /></el-icon>
              <span>思考中...</span>
            </div>
          </div>
        </div>

        <!-- 问答提示区 - 右侧 -->
        <div class="quick-questions-panel">
          <div class="panel-title">常见问题</div>
          <div class="quick-questions">
            <el-tag
              v-for="(question, index) in quickQuestions"
              :key="index"
              class="question-tag"
              @click="askQuickQuestion(question)"
            >
              {{ question }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-section">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入问题，如：如何养护？"
            @keydown.enter.prevent="handleEnter"
            class="message-input"
          />
          <div class="input-actions">
            <el-button :icon="Upload" circle @click="uploadImage" />
            <el-button
              type="primary"
              class="send-btn"
              :icon="Promotion"
              :loading="loading"
              @click="sendMessage"
            >
              发送
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onActivated, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, Clock, Upload, Promotion } from '@element-plus/icons-vue'
import axios from 'axios'
import { api } from '../api/config'

const route = useRoute()
const chatContainer = ref<HTMLElement>()
const inputMessage = ref('')
const loading = ref(false)

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

const messages = ref<Message[]>([])

const quickQuestions = ref([
  '如何浇水？',
  '适合什么土壤？',
  '如何防治病虫害？',
  '花期是什么时候？',
  '需要多少光照？',
  '如何施肥？'
])

const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const scrollToBottom = () => {
  nextTick(() => {
    setTimeout(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    }, 50) // 给一点点延迟确保渲染完成
  })
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }

  if (loading.value) {
    return
  }

  messages.value.push({
    role: 'user',
    content: inputMessage.value,
    timestamp: Date.now()
  })

  const userQuestion = inputMessage.value
  inputMessage.value = ''
  loading.value = true
  scrollToBottom()

  // 获取当前花卉名称（从路由参数或对话历史中提取）
  const currentFlower = route.query.flower as string || extractFlowerFromHistory()

  try {
    // 限制历史记录为最近的5轮对话（10条消息），并转换为后端要求的格式
    const recentHistory = messages.value.slice(-10).map(msg => ({
      role: msg.role,
      content: msg.content
    }))

    const response = await axios.post(api.chat, {
      question: userQuestion,
      history: recentHistory
    }, {
      headers: {
        ...(localStorage.getItem('access_token') ? { Authorization: `Bearer ${localStorage.getItem('access_token')}` } : {})
      }
    })

    const assistantAnswer = response.data.answer

    messages.value.push({
      role: 'assistant',
      content: assistantAnswer,
      timestamp: Date.now()
    })

    // 保存问答记录到本地存储
    saveQARecord(currentFlower || '未知', userQuestion, assistantAnswer)
  } catch (error) {
    console.error('问答失败:', error)
    if (axios.isAxiosError(error)) {
      ElMessage.error(`API调用失败: ${error.message}`)
    } else {
      ElMessage.error('回答失败，请稍后重试')
    }
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 从对话历史中提取花卉名称
const extractFlowerFromHistory = (): string => {
  const recentMessages = messages.value.slice(-6)
  for (const msg of recentMessages) {
    if (msg.role === 'assistant') {
      // 尝试从回答中提取花卉名称
      const flowerMatch = msg.content.match(/(?:这是|识别出|发现|关于)[\s]*(.+?)[\s]*(?:花|植物)/)
      if (flowerMatch && flowerMatch[1]) {
        return flowerMatch[1].trim()
      }
    }
  }
  return ''
}

// 生成会话ID
const generateConversationId = (): string => {
  return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// 保存问答记录到本地存储
const saveQARecord = (flower: string, question: string, answer: string) => {
  const qaRecords = JSON.parse(localStorage.getItem('qaRecords') || '[]')
  const record = {
    id: Date.now(),
    flower,
    question,
    answer,
    timestamp: Date.now()
  }
  // 只保留最近50条记录
  const updatedRecords = [record, ...qaRecords].slice(0, 50)
  localStorage.setItem('qaRecords', JSON.stringify(updatedRecords))
}

const handleEnter = (event: KeyboardEvent) => {
  if (event.ctrlKey || event.metaKey) {
    sendMessage()
  }
}

const clearHistory = () => {
  messages.value = []
  ElMessage.success('对话已清空')
}

const askQuickQuestion = (question: string) => {
  inputMessage.value = question
  sendMessage()
}

const uploadImage = () => {
  ElMessage.info('图片上传功能开发中')
}

const loadHistory = () => {
  // 加载后端问答历史（已登录）或本地存储（未登录）
  const token = localStorage.getItem('access_token')
  const headers = token ? { Authorization: `Bearer ${token}` } : {}
  axios.get('/api/qa/history', { headers }).then(({ data }) => {
    // 将问答记录转换为对话消息（按时间降序返回，反向插入维持时间顺序）
    if (Array.isArray(data) && data.length > 0) {
      const pairs = data.slice().reverse()
      const hist: Message[] = []
      for (const p of pairs) {
        hist.push({ role: 'user', content: p.question, timestamp: Date.parse(p.created_at) })
        hist.push({ role: 'assistant', content: p.answer || '', timestamp: Date.parse(p.created_at) })
      }
      messages.value = hist
      scrollToBottom()
    } else {
      // 后端无记录时回退到本地最近记录
      const qaRecords = JSON.parse(localStorage.getItem('qaRecords') || '[]')
      const hist: Message[] = []
      for (const r of qaRecords.reverse()) {
        hist.push({ role: 'user', content: r.question, timestamp: r.timestamp })
        hist.push({ role: 'assistant', content: r.answer, timestamp: r.timestamp })
      }
      messages.value = hist
      scrollToBottom()
    }
  }).catch(() => {
    // 未登录则读取本地存储
    const qaRecords = JSON.parse(localStorage.getItem('qaRecords') || '[]')
    const hist: Message[] = []
    for (const r of qaRecords.reverse()) {
      hist.push({ role: 'user', content: r.question, timestamp: r.timestamp })
      hist.push({ role: 'assistant', content: r.answer, timestamp: r.timestamp })
    }
    messages.value = hist
    scrollToBottom()
  })
}

onMounted(() => {
  if (route.query.flower) {
    const flowerName = route.query.flower as string
    inputMessage.value = `请介绍一下${flowerName}的养护方法`
    sendMessage()
  }
  loadHistory()
})

onActivated(() => {
  loadHistory()
  scrollToBottom()
})
</script>

<style scoped>
.qa-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0;
}

.chat-card {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px); /* 稍微缩小一点高度，确保不超出主容器 */
  overflow: hidden;
}

:deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px 24px !important;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 28px;
  color: #333333;
  margin: 0;
}

.header-btn {
  background-color: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-btn:hover {
  color: #4CAF50;
  border-color: #4CAF50;
}

.qa-layout {
  display: flex;
  gap: 32px;
  flex: 1;
  overflow: hidden;
  padding: 20px 0;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: #F5F5F5;
  border-radius: 12px;
}

.message {
  display: flex;
  margin-bottom: 24px;
  align-items: flex-end;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 16px 20px;
  border-radius: 12px;
  position: relative;
}

.message.user .message-bubble {
  background-color: #E3F2FD;
  color: #1976D2;
}

.message.assistant .message-bubble {
  background-color: #FFFFFF;
  color: #333333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message-bubble.loading {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #666666;
}

.message-content {
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 17px;
  line-height: 1.7;
  margin-bottom: 6px;
  white-space: pre-wrap; /* 保证换行符生效 */
}

.message-time {
  font-family: 'Roboto', sans-serif;
  font-weight: 300;
  font-size: 13px;
  color: #999999;
  text-align: right;
}

.quick-questions-panel {
  flex: 0 0 320px;
  background-color: #FFFFFF;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #E0E0E0;
  overflow-y: auto;
}

.panel-title {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 20px;
  color: #333333;
  margin-bottom: 20px;
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.question-tag {
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 15px;
  color: #2196F3;
  background-color: #E3F2FD;
  border-color: #2196F3;
  padding: 14px 18px;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 10px;
  text-align: left;
}

.question-tag:hover {
  background-color: #BBDEFB;
  transform: translateX(6px);
}

.input-section {
  padding-top: 20px;
  border-top: 2px solid #E0E0E0;
}

.input-container {
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: 10px;
  font-family: 'Roboto', sans-serif;
  font-size: 17px;
  resize: none;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.send-btn {
  background-color: #4CAF50;
  border-color: #4CAF50;
  color: white !important;
  border-radius: 10px;
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 18px;
  padding: 14px 32px;
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.send-btn:hover {
  background-color: #43A047;
  border-color: #43A047;
  box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4);
}

/* 响应式布局 - 中等屏幕 (≤1400px) */
@media (max-width: 1400px) {
  .qa-page {
    padding: 0;
  }

  .card-title {
    font-size: 26px;
  }

  .quick-questions-panel {
    flex: 0 0 280px;
    padding: 20px;
  }

  .panel-title {
    font-size: 19px;
  }

  .question-tag {
    font-size: 14px;
    padding: 13px 16px;
  }

  .message-content {
    font-size: 16px;
  }
}

/* 响应式布局 - 小屏幕 (≤1200px) */
@media (max-width: 1200px) {
  .card-title {
    font-size: 24px;
  }

  .quick-questions-panel {
    flex: 0 0 240px;
    padding: 18px;
  }

  .panel-title {
    font-size: 18px;
    margin-bottom: 16px;
  }

  .quick-questions {
    gap: 12px;
  }

  .question-tag {
    font-size: 14px;
    padding: 12px 14px;
  }

  .message-bubble {
    padding: 14px 18px;
  }

  .message-content {
    font-size: 16px;
  }

  .chat-container {
    padding: 20px;
  }
}

/* 响应式布局 - 平板 (≤992px) */
@media (max-width: 992px) {
  .card-title {
    font-size: 22px;
  }

  .quick-questions-panel {
    flex: 0 0 220px;
    padding: 16px;
  }

  .panel-title {
    font-size: 17px;
    margin-bottom: 14px;
  }

  .question-tag {
    font-size: 13px;
    padding: 11px 13px;
  }

  .message-bubble {
    padding: 12px 16px;
  }

  .message-content {
    font-size: 15px;
  }
}

/* 响应式布局 - 移动端 (≤768px) */
@media (max-width: 768px) {
  .qa-page {
    padding: 0;
  }

  .chat-card {
    height: calc(100vh - 96px);
  }

  .card-title {
    font-size: 20px;
  }

  /* 左右布局改为上下布局，快速问题面板变为可折叠区域 */
  .qa-layout {
    flex-direction: column;
    gap: 16px;
  }

  .quick-questions-panel {
    flex: 0 0 auto;
    max-height: 180px;
    padding: 16px;
  }

  .panel-title {
    font-size: 16px;
    margin-bottom: 12px;
  }

  .question-tag {
    font-size: 13px;
    padding: 10px 12px;
  }

  .message-bubble {
    max-width: 85%;
    padding: 12px 16px;
  }

  .message-content {
    font-size: 15px;
  }

  .message {
    margin-bottom: 20px;
  }

  .chat-container {
    padding: 16px;
  }

  .input-container {
    gap: 12px;
  }

  .message-input :deep(.el-textarea__inner) {
    font-size: 15px;
  }

  .send-btn {
    font-size: 16px;
    padding: 12px 24px;
  }
}

/* 小屏移动端 (≤480px) */
@media (max-width: 480px) {
  .qa-page {
    padding: 0;
  }

  .chat-card {
    height: calc(100vh - 88px);
  }

  .card-title {
    font-size: 18px;
  }

  .qa-layout {
    gap: 12px;
  }

  .quick-questions-panel {
    padding: 12px;
    max-height: 150px;
  }

  .panel-title {
    font-size: 15px;
    margin-bottom: 10px;
  }

  .quick-questions {
    gap: 8px;
  }

  .question-tag {
    font-size: 12px;
    padding: 8px 10px;
  }

  .message-bubble {
    max-width: 90%;
    padding: 10px 14px;
  }

  .message-content {
    font-size: 14px;
  }

  .message-time {
    font-size: 12px;
  }

  .message {
    margin-bottom: 16px;
  }

  .chat-container {
    padding: 12px;
  }

  .input-actions {
    flex-direction: row;
    align-items: center;
  }

  .send-btn {
    padding: 10px 20px;
    font-size: 15px;
  }
}
</style>
