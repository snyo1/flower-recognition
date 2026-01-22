<template>
  <div class="history-page">
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">📜 历史记录</span>
          <div class="header-actions">
            <el-button @click="exportHistory" :disabled="historyList.length === 0">
              <el-icon><Download /></el-icon>
              导出记录
            </el-button>
            <el-button type="danger" @click="clearAllHistory" :disabled="historyList.length === 0">
              <el-icon><Delete /></el-icon>
              清空历史
            </el-button>
          </div>
        </div>
      </template>

      <!-- Tab 切换 -->
      <el-tabs v-model="activeTab" class="history-tabs">
        <el-tab-pane label="识别记录" name="recognition">
          <div v-if="recognitionHistory.length === 0" class="empty-state">
            <el-empty description="暂无识别记录" />
          </div>
          <el-timeline v-else>
            <el-timeline-item
              v-for="(item, index) in recognitionHistory"
              :key="item.id"
              :timestamp="formatDate(item.timestamp)"
              placement="top"
              :type="index === 0 ? 'primary' : undefined"
              :hollow="index > 0"
            >
              <el-card class="history-item-card" shadow="hover">
                <div class="history-content">
                  <div class="flower-info">
                    <div class="flower-thumbnail">
                      <el-icon :size="32"><Picture /></el-icon>
                    </div>
                    <div class="flower-details">
                      <h3 class="flower-name">{{ item.flowerName }}</h3>
                      <p class="flower-family">{{ item.family }}</p>
                      <div class="flower-tags">
                        <el-tag size="small" type="success">置信度 {{ item.confidence }}%</el-tag>
                        <el-tag size="small" type="info">{{ item.color }}</el-tag>
                        <el-tag size="small">{{ item.bloomingPeriod }}</el-tag>
                      </div>
                    </div>
                  </div>
                  <div class="history-actions">
                    <el-button type="primary" link @click="viewDetail(item)">
                      查看详情
                    </el-button>
                    <el-button type="danger" link @click="deleteHistory(item.id, 'recognition')">
                      删除
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>

        <el-tab-pane label="问答记录" name="qa">
          <div v-if="qaHistory.length === 0" class="empty-state">
            <el-empty description="暂无问答记录" />
          </div>
          <el-timeline v-else>
            <el-timeline-item
              v-for="(item, index) in qaHistory"
              :key="item.id"
              :timestamp="formatDate(item.timestamp)"
              placement="top"
              :type="index === 0 ? 'success' : undefined"
              :hollow="index > 0"
            >
              <el-card class="history-item-card qa-card" shadow="hover">
                <div class="qa-content">
                  <div class="qa-flower">
                    <el-icon><Orange /></el-icon>
                    <span class="qa-flower-name">{{ item.flowerName }}</span>
                  </div>
                  <div class="qa-conversation">
                    <div class="qa-question">
                      <span class="qa-label">问：</span>
                      <span class="qa-text">{{ item.question }}</span>
                    </div>
                    <div class="qa-answer">
                      <span class="qa-label">答：</span>
                      <span class="qa-text">{{ item.answer }}</span>
                    </div>
                  </div>
                  <div class="qa-actions">
                    <el-button type="primary" link size="small" @click="viewQADetail(item)">
                      查看详情
                    </el-button>
                    <el-button type="danger" link size="small" @click="deleteHistory(item.id, 'qa')">
                      删除
                    </el-button>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 识别详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="识别详情"
      width="700px"
    >
      <div v-if="selectedHistory" class="detail-content">
        <div class="detail-image">
          <el-icon :size="60"><Picture /></el-icon>
        </div>
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="花卉名称" span="2">
            {{ selectedHistory.flowerName }}
          </el-descriptions-item>
          <el-descriptions-item label="科属分类">
            {{ selectedHistory.family }}
          </el-descriptions-item>
          <el-descriptions-item label="识别时间">
            {{ formatDateTime(selectedHistory.timestamp) }}
          </el-descriptions-item>
          <el-descriptions-item label="颜色特征">
            {{ selectedHistory.color }}
          </el-descriptions-item>
          <el-descriptions-item label="花期">
            {{ selectedHistory.bloomingPeriod }}
          </el-descriptions-item>
          <el-descriptions-item label="置信度" span="2">
            <el-tag type="success">{{ selectedHistory.confidence }}%</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">特征描述</el-divider>
        <p class="detail-text">{{ selectedHistory.description }}</p>

        <el-divider content-position="left">养护指南</el-divider>
        <p class="detail-text">{{ selectedHistory.careGuide }}</p>

        <el-divider content-position="left">花语寓意</el-divider>
        <p class="detail-text">{{ selectedHistory.flowerLanguage }}</p>

        <div class="detail-actions">
          <el-button type="primary" @click="goToQA(selectedHistory.flowerName)">
            <el-icon><ChatDotRound /></el-icon>
            继续询问
          </el-button>
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 问答详情对话框 -->
    <el-dialog
      v-model="qaDetailDialogVisible"
      title="问答详情"
      width="700px"
    >
      <div v-if="selectedQA" class="qa-detail-content">
        <div class="qa-detail-header">
          <el-icon><Orange /></el-icon>
          <span class="qa-detail-flower">{{ selectedQA.flowerName }}</span>
          <el-tag type="info" size="small">{{ formatDateTime(selectedQA.timestamp) }}</el-tag>
        </div>

        <div class="qa-detail-message">
          <div class="message-label user-label">您的问题：</div>
          <div class="message-content user-content">{{ selectedQA.question }}</div>
        </div>

        <div class="qa-detail-message">
          <div class="message-label assistant-label">系统回答：</div>
          <div class="message-content assistant-content">{{ selectedQA.answer }}</div>
        </div>

        <div class="qa-detail-actions">
          <el-button type="primary" @click="askSimilarQuestion(selectedQA)">
            <el-icon><ChatDotRound /></el-icon>
            继续提问
          </el-button>
          <el-button @click="qaDetailDialogVisible = false">关闭</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete, Picture, ChatDotRound, Orange } from '@element-plus/icons-vue'

const router = useRouter()
const activeTab = ref('recognition')

interface RecognitionItem {
  id: number
  imageUrl: string
  flowerName: string
  family: string
  color: string
  bloomingPeriod: string
  description: string
  careGuide: string
  flowerLanguage: string
  confidence: number
  timestamp: number
}

interface QAItem {
  id: number
  flowerName: string
  question: string
  answer: string
  timestamp: number
}

const recognitionHistory = ref<RecognitionItem[]>([
  {
    id: 1,
    imageUrl: '',
    flowerName: '月季',
    family: '蔷薇科',
    color: '红色、粉色、黄色等',
    bloomingPeriod: '5月-10月（夏秋）',
    description: '月季花被称为"花中皇后"，四季开花，花色丰富，芳香浓郁。',
    careGuide: '喜阳光充足，耐旱耐寒，但不耐水湿。春秋季可每天浇水，保持土壤湿润。生长旺季每月施肥一次。',
    flowerLanguage: '寓意纯洁的爱、热情和祝福，是爱情的象征。',
    confidence: 95,
    timestamp: Date.now() - 3600000
  },
  {
    id: 2,
    imageUrl: '',
    flowerName: '玫瑰',
    family: '蔷薇科',
    color: '红色、粉色、白色等',
    bloomingPeriod: '5月-10月（夏秋）',
    description: '玫瑰是世界著名的观赏植物，花形优美，香气浓郁，被称为"爱情之花"。',
    careGuide: '喜温暖、阳光充足的环境，耐寒性较强，需要充足的阳光。春秋季每天浇水，夏季早晚各浇一次。',
    flowerLanguage: '象征爱情、美丽和热情，表达真挚的情感。',
    confidence: 92,
    timestamp: Date.now() - 86400000
  },
  {
    id: 3,
    imageUrl: '',
    flowerName: '向日葵',
    family: '菊科',
    color: '金黄色',
    bloomingPeriod: '7月-9月（夏季）',
    description: '向日葵因花序随太阳转动而得名，象征光明和希望。',
    careGuide: '喜温暖、阳光充足的环境，耐旱不耐涝。每天需6-8小时直射光照。',
    flowerLanguage: '寓意忠诚、爱慕、阳光和希望。',
    confidence: 88,
    timestamp: Date.now() - 172800000
  }
])

const qaHistory = ref<QAItem[]>([
  {
    id: 1,
    flowerName: '月季',
    question: '月季如何浇水？',
    answer: '月季的浇水原则是"见干见湿"。春秋两季生长旺盛期，可每2-3天浇一次水；夏季高温时，每天早晚各浇一次水；冬季休眠期减少浇水，每周一次即可。注意避免积水，以免根部腐烂。',
    timestamp: Date.now() - 7200000
  },
  {
    id: 2,
    flowerName: '玫瑰',
    question: '玫瑰需要多少光照？',
    answer: '玫瑰喜阳光充足的环境，每天至少需要6-8小时的直射光照。光照不足会导致花朵稀少、颜色暗淡。如果是盆栽玫瑰，应放置在阳台或庭院阳光充足处。',
    timestamp: Date.now() - 3600000
  },
  {
    id: 3,
    flowerName: '月季',
    question: '如何防治月季的白粉病？',
    answer: '防治月季白粉病的方法：1）改善通风，避免植株过密；2）控制湿度，避免叶片长时间湿润；3）发现病叶及时摘除销毁；4）发病初期喷洒75%百菌清可湿性粉剂800倍液或50%多菌灵可湿性粉剂1000倍液，每7-10天喷一次，连续2-3次。',
    timestamp: Date.now() - 1800000
  }
])

// 所有历史记录（用于导出）
const historyList = computed(() => {
  return [...recognitionHistory.value, ...qaHistory.value]
})

const detailDialogVisible = ref(false)
const selectedHistory = ref<RecognitionItem | null>(null)
const qaDetailDialogVisible = ref(false)
const selectedQA = ref<QAItem | null>(null)

const formatDate = (timestamp: number) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`

  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
}

const formatDateTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const viewDetail = (item: RecognitionItem) => {
  selectedHistory.value = item
  detailDialogVisible.value = true
}

const viewQADetail = (item: QAItem) => {
  selectedQA.value = item
  qaDetailDialogVisible.value = true
}

const deleteHistory = async (id: number, type: 'recognition' | 'qa') => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条记录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    if (type === 'recognition') {
      recognitionHistory.value = recognitionHistory.value.filter(h => h.id !== id)
    } else {
      qaHistory.value = qaHistory.value.filter(h => h.id !== id)
    }

    ElMessage.success('删除成功')
  } catch {
    // 用户取消删除
  }
}

const clearAllHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有历史记录吗？此操作不可恢复。',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    recognitionHistory.value = []
    qaHistory.value = []
    ElMessage.success('已清空所有历史记录')
  } catch {
    // 用户取消
  }
}

const exportHistory = () => {
  // 导出为CSV格式
  const headers = ['ID', '类型', '花卉名称', '时间', '内容']
  const rows = historyList.value.map(item => {
    if ('question' in item) {
      return [
        item.id,
        '问答',
        item.flowerName,
        formatDateTime(item.timestamp),
        `问题: ${item.question}\n回答: ${item.answer}`
      ]
    } else {
      return [
        item.id,
        '识别',
        item.flowerName,
        formatDateTime(item.timestamp),
        `${item.family} | ${item.description}`
      ]
    }
  })

  const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `花卉识别历史记录_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
  ElMessage.success('导出成功')
}

const goToQA = (flowerName: string) => {
  detailDialogVisible.value = false
  router.push({
    path: '/qa',
    query: { flower: flowerName }
  })
}

const askSimilarQuestion = (qaItem: QAItem) => {
  qaDetailDialogVisible.value = false
  router.push({
    path: '/qa',
    query: { flower: qaItem.flowerName, question: qaItem.question }
  })
}
</script>

<style scoped>
.history-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0;
}

.history-card {
  margin-bottom: 32px;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.history-tabs {
  padding: 20px 0;
}

.empty-state {
  padding: 60px 0;
}

.history-item-card {
  margin-top: 12px;
}

.history-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.flower-info {
  display: flex;
  gap: 20px;
  flex: 1;
}

.flower-thumbnail {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.flower-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.flower-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 20px;
  color: #333333;
  margin: 0;
}

.flower-family {
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 15px;
  color: #666666;
  margin: 0;
}

.flower-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.history-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

/* 问答卡片样式 */
.qa-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
}

.qa-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.qa-flower {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #E3F2FD;
  border-radius: 8px;
  color: #1976D2;
}

.qa-flower-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 16px;
}

.qa-conversation {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.qa-question,
.qa-answer {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.qa-label {
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
  padding-top: 2px;
}

.qa-text {
  font-size: 14px;
  line-height: 1.6;
  color: #333333;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.qa-question .qa-label {
  color: #1976D2;
}

.qa-answer .qa-label {
  color: #4CAF50;
}

.qa-actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #E0E0E0;
}

/* 详情对话框样式 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-image {
  width: 100%;
  height: 250px;
  background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.detail-descriptions {
  margin-top: 10px;
}

.detail-text {
  font-family: 'Roboto', sans-serif;
  font-size: 15px;
  line-height: 1.8;
  color: #333333;
  margin: 0;
}

.detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px solid #E0E0E0;
}

/* 问答详情对话框 */
.qa-detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.qa-detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #E3F2FD;
  border-radius: 8px;
  color: #1976D2;
}

.qa-detail-flower {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 18px;
}

.qa-detail-message {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #F5F5F5;
  border-radius: 8px;
}

.message-label {
  font-weight: 600;
  font-size: 14px;
}

.user-label {
  color: #1976D2;
}

.assistant-label {
  color: #4CAF50;
}

.message-content {
  font-size: 15px;
  line-height: 1.8;
  color: #333333;
  white-space: pre-wrap;
}

.qa-detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .card-title {
    font-size: 22px;
  }

  .header-actions {
    flex-direction: column;
  }

  .history-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .flower-thumbnail {
    width: 80px;
    height: 80px;
  }

  .history-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .detail-image {
    height: 200px;
  }

  .detail-actions,
  .qa-detail-actions {
    flex-direction: column;
  }

  .detail-actions .el-button,
  .qa-detail-actions .el-button {
    width: 100%;
  }
}
</style>
