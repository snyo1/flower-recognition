<template>
  <div class="qa-page">
    <el-card class="chat-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">智能问答</span>
          <el-button class="header-btn" :icon="Clock" circle @click="clearHistory" title="清空对话" />
        </div>
      </template>

      <div class="qa-layout">
        <div class="chat-container" ref="chatContainer">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message', message.role]"
          >
            <div class="message-bubble">
              <div v-if="message.role === 'assistant'" class="message-content" v-html="renderMarkdown(message.content)"></div>
              <div v-else class="message-content user-text">{{ message.content }}</div>
              <div class="message-time">{{ formatDateTime(message.timestamp) }}</div>
            </div>
          </div>

          <div v-if="loading" class="message assistant">
            <div class="message-bubble loading">
              <el-icon class="is-loading" :size="20"><Loading /></el-icon>
              <span>思考中...</span>
            </div>
          </div>
        </div>

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

      <div class="input-section">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入问题，如：如何养护？（Ctrl+Enter 发送）"
            @keydown.enter.prevent="handleEnter"
            class="message-input"
          />
          <div class="input-actions">
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
import { Loading, Clock, Promotion } from '@element-plus/icons-vue'
import axios from 'axios'
import { api } from '../api/config'
import { marked } from 'marked'

marked.setOptions({ breaks: true, gfm: true })

const renderMarkdown = (content: string) => {
  if (!content) return ''
  return marked.parse(content) as string
}

const decorateAnswer = (content: string) => {
  if (!content) return ''
  const normalized = content.trim()
  if (/^#|^- |^\d+\./m.test(normalized)) {
    return normalized
  }

  const lines = normalized
    .split('\n')
    .map(line => line.trim())
    .filter(Boolean)

  if (lines.length <= 1) {
    return `### 花卉建议\n\n${normalized}`
  }

  const [summary, ...rest] = lines
  return `### 花卉建议\n\n${summary}\n\n${rest.map(line => `- ${line.replace(/^\d+[、.\s]*/, '')}`).join('\n')}`
}

const DEFAULT_ANSWER = '抱歉，我暂时无法回答您的问题。您可以尝试询问花卉的养护方法、花期、花语等相关知识，或稍后再试。'

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

const getCurrentUserId = (): string => {
  const token = localStorage.getItem('access_token')
  if (!token) return ''
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub || ''
  } catch {
    return ''
  }
}

const formatDateTime = (timestamp: number) => {
  const date = new Date(timestamp)
  const now = new Date()
  const isToday = date.toDateString() === now.toDateString()
  const timeStr = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  if (isToday) return timeStr
  const dateStr = `${date.getMonth() + 1}月${date.getDate()}日`
  return `${dateStr} ${timeStr}`
}

const scrollToBottom = () => {
  nextTick(() => {
    setTimeout(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    }, 50)
  })
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) {
    ElMessage.warning('请输入问题')
    return
  }
  if (loading.value) return

  messages.value.push({
    role: 'user',
    content: inputMessage.value,
    timestamp: Date.now()
  })

  const userQuestion = inputMessage.value
  inputMessage.value = ''
  loading.value = true
  scrollToBottom()

  const currentFlower = route.query.flower as string || ''
  let assistantAnswer = ''

  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const recentHistory = messages.value.slice(-6).map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const response = await axios.post(api.chat, {
        question: userQuestion,
        history: recentHistory
      }, {
        headers: {
          ...(localStorage.getItem('access_token') ? { Authorization: `Bearer ${localStorage.getItem('access_token')}` } : {})
        },
        timeout: 20000
      })

      assistantAnswer = decorateAnswer(response.data.answer || DEFAULT_ANSWER)
      break
    } catch (error) {
      console.error(`问答第${attempt + 1}次尝试失败:`, error)
      if (attempt === 1) {
        assistantAnswer = decorateAnswer(DEFAULT_ANSWER)
      } else {
        await new Promise(r => setTimeout(r, 1000))
      }
    }
  }

  messages.value.push({
    role: 'assistant',
    content: assistantAnswer,
    timestamp: Date.now()
  })

  saveQARecord(currentFlower || '通用', userQuestion, assistantAnswer)
  loading.value = false
  scrollToBottom()
}

const saveQARecord = (flower: string, question: string, answer: string) => {
  const userId = getCurrentUserId()
  if (!userId) return
  const key = `qaRecords_${userId}`
  const qaRecords = JSON.parse(localStorage.getItem(key) || '[]')
  const record = { id: Date.now(), flower, question, answer, timestamp: Date.now() }
  const updated = [record, ...qaRecords].slice(0, 50)
  localStorage.setItem(key, JSON.stringify(updated))
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

const loadHistory = () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    messages.value = []
    return
  }

  axios.get('/api/qa/history', {
    headers: { Authorization: `Bearer ${token}` }
  }).then(({ data }) => {
    if (Array.isArray(data) && data.length > 0) {
      const pairs = data.slice().reverse()
      const hist: Message[] = []
      for (const p of pairs) {
        hist.push({ role: 'user', content: p.question, timestamp: Date.parse(p.created_at) })
        hist.push({ role: 'assistant', content: decorateAnswer(p.answer || ''), timestamp: Date.parse(p.created_at) })
      }
      messages.value = hist
    } else {
      messages.value = []
    }
    scrollToBottom()
  }).catch(() => {
    messages.value = []
  })
}

onMounted(() => {
  loadHistory()
  if (route.query.flower) {
    const flowerName = route.query.flower as string
    inputMessage.value = `请介绍一下${flowerName}的养护方法`
    sendMessage()
  }
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
  height: calc(100vh - 120px);
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
  font-weight: 700;
  font-size: 22px;
  color: #333;
  margin: 0;
}

.header-btn {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 50%;
}

.header-btn:hover {
  color: #4caf50;
  border-color: #4caf50;
}

.qa-layout {
  display: flex;
  gap: 24px;
  flex: 1;
  overflow: hidden;
  padding: 16px 0;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 10px;
}

.message {
  display: flex;
  margin-bottom: 18px;
  align-items: flex-end;
}

.message.user { justify-content: flex-end; }
.message.assistant { justify-content: flex-start; }

.message-bubble {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  position: relative;
}

.message.user .message-bubble {
  background-color: #e3f2fd;
  color: #1565c0;
}

.message.assistant .message-bubble {
  background: linear-gradient(180deg, #ffffff 0%, #f9fff8 100%);
  color: #333;
  box-shadow: 0 6px 18px rgba(76, 175, 80, 0.08);
  border: 1px solid rgba(76, 175, 80, 0.12);
}

.message-bubble.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #888;
}

.message-content {
  font-size: 14px;
  line-height: 1.7;
  margin-bottom: 4px;
  white-space: normal;
  word-break: break-word;
}

.message-content.user-text { white-space: pre-wrap; }

.message-content :deep(p) { margin: 0 0 8px 0; }
.message-content :deep(p:last-child) { margin-bottom: 0; }
.message-content :deep(ul), .message-content :deep(ol) { margin: 6px 0; padding-left: 20px; }
.message-content :deep(li) { margin-bottom: 4px; }
.message-content :deep(h1), .message-content :deep(h2), .message-content :deep(h3) {
  font-size: 15px;
  font-weight: 700;
  margin: 8px 0 6px 0;
  color: #2e7d32;
}
.message-content :deep(strong) {
  color: #1b5e20;
}
.message-content :deep(blockquote) {
  margin: 8px 0;
  padding: 8px 12px;
  border-left: 3px solid #81c784;
  background: rgba(129, 199, 132, 0.08);
  border-radius: 6px;
}
.message-content :deep(code) {
  background: rgba(0,0,0,0.06);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 13px;
}
.message-content :deep(pre) {
  background: rgba(0,0,0,0.06);
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 13px;
}

.message-time {
  font-size: 11px;
  color: #aaa;
  text-align: right;
  margin-top: 2px;
}

.quick-questions-panel {
  flex: 0 0 260px;
  background-color: #fff;
  border-radius: 10px;
  padding: 20px;
  border: 1px solid #e8e8e8;
  overflow-y: auto;
}

.panel-title {
  font-weight: 700;
  font-size: 15px;
  color: #333;
  margin-bottom: 14px;
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.question-tag {
  font-size: 13px;
  color: #1976d2;
  background-color: #e3f2fd;
  border-color: #90caf9;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.25s;
  border-radius: 8px;
  text-align: left;
  white-space: normal;
  height: auto;
}

.question-tag:hover {
  background-color: #bbdefb;
  transform: translateX(4px);
}

.input-section {
  padding-top: 14px;
  border-top: 1px solid #e8e8e8;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input { flex: 1; }

.message-input :deep(.el-textarea__inner) {
  border-radius: 8px;
  font-size: 14px;
  resize: none;
}

.input-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.send-btn {
  background-color: #4caf50;
  border-color: #4caf50;
  color: white !important;
  border-radius: 8px;
  font-weight: 700;
  font-size: 15px;
  padding: 10px 24px;
}

.send-btn:hover {
  background-color: #43a047;
  border-color: #43a047;
}

@media (max-width: 1100px) {
  .quick-questions-panel { flex: 0 0 200px; padding: 16px; }
}

@media (max-width: 768px) {
  .chat-card { height: calc(100vh - 96px); }
  .card-title { font-size: 18px; }
  .qa-layout { flex-direction: column; gap: 12px; }
  .quick-questions-panel { flex: 0 0 auto; max-height: 140px; overflow-y: auto; }
  .message-bubble { max-width: 88%; }
  .send-btn { font-size: 14px; padding: 9px 18px; }
}

@media (max-width: 480px) {
  .chat-card { height: calc(100vh - 88px); }
  .message-bubble { max-width: 92%; }
  .input-actions { flex-direction: row; }
}
</style>
