<template>
  <div class="knowledge-page">
    <el-card class="knowledge-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">📚 花卉知识库</span>
          <div class="header-actions">
            <el-tag v-if="selectedCategory" closable @close="clearCategory">
              {{ selectedCategory }}
            </el-tag>
          </div>
        </div>
      </template>

      <!-- 搜索和分类筛选区 -->
      <div class="filter-section">
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索花卉名称、科属或特征"
            clearable
            size="large"
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="category-filters">
          <el-divider content-position="left">
            <span class="filter-title">按科属筛选</span>
          </el-divider>
          <div class="filter-tags">
            <el-tag
              v-for="category in familyCategories"
              :key="category"
              :type="selectedCategory === category ? 'success' : ''"
              :effect="selectedCategory === category ? 'dark' : 'plain'"
              class="filter-tag"
              @click="selectCategory(category)"
            >
              {{ category }}
            </el-tag>
          </div>

          <el-divider content-position="left" style="margin-top: 20px;">
            <span class="filter-title">按颜色筛选</span>
          </el-divider>
          <div class="filter-tags">
            <el-tag
              v-for="color in colorCategories"
              :key="color.name"
              color="#FFFFFF"
              effect="plain"
              class="filter-tag color-tag"
              :style="{ 
                borderColor: color.value, 
                color: color.value,
                borderWidth: selectedColor === color.name ? '3px' : '1px',
                fontWeight: selectedColor === color.name ? '700' : '400',
                transform: selectedColor === color.name ? 'scale(1.1)' : 'scale(1)'
              }"
              @click="selectColor(color.name)"
            >
              {{ color.name }}
            </el-tag>
          </div>

          <el-divider content-position="left" style="margin-top: 20px;">
            <span class="filter-title">按花期筛选</span>
          </el-divider>
          <div class="filter-tags">
            <el-tag
              v-for="period in bloomingPeriods"
              :key="period"
              :type="selectedPeriod === period ? 'success' : ''"
              :effect="selectedPeriod === period ? 'dark' : 'plain'"
              class="filter-tag"
              @click="selectPeriod(period)"
            >
              {{ period }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 热门推荐 -->
      <div v-if="!searchKeyword && !selectedCategory && !selectedColor && !selectedPeriod" class="hot-section">
        <el-divider content-position="left">
          <span class="hot-title">🔥 热门推荐</span>
        </el-divider>
        <div class="hot-flowers">
          <div
            v-for="flower in hotFlowers"
            :key="flower.id"
            class="hot-flower-card"
            @click="viewDetail(flower)"
          >
            <div class="hot-flower-image">
              <el-icon :size="32"><Picture /></el-icon>
            </div>
            <div class="hot-flower-info">
              <div class="hot-flower-name">{{ flower.name }}</div>
              <div class="hot-flower-family">{{ flower.family }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 花卉列表 -->
      <div class="flowers-section">
        <el-divider content-position="left">
          <span class="section-title">
            {{ searchKeyword || selectedCategory || selectedColor || selectedPeriod ? '搜索结果' : '全部花卉' }}
            <el-tag type="info" size="small">{{ filteredFlowers.length }} 项</el-tag>
          </span>
        </el-divider>

        <el-empty v-if="filteredFlowers.length === 0" description="暂无相关花卉" />

        <div v-else class="flower-grid">
          <el-card
            v-for="flower in filteredFlowers"
            :key="flower.id"
            class="flower-card"
            shadow="hover"
            @click="viewDetail(flower)"
          >
            <div class="flower-card-image">
              <el-icon :size="48"><Picture /></el-icon>
            </div>
            <div class="flower-card-content">
              <h3 class="flower-card-name">{{ flower.name }}</h3>
              <p class="flower-card-family">{{ flower.family }}</p>
              <div class="flower-card-tags">
                <el-tag size="small" type="info">{{ flower.color }}</el-tag>
                <el-tag size="small" type="success">{{ flower.bloomingPeriod }}</el-tag>
              </div>
              <p class="flower-card-description">{{ flower.description }}</p>
              <div class="flower-card-actions">
                <el-button type="primary" link @click.stop="viewDetail(flower)">
                  查看详情
                </el-button>
                <el-button link @click.stop="startQA(flower)">
                  发起问答
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>

    <!-- 花卉详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      :title="selectedFlower?.name"
      width="800px"
    >
      <div v-if="selectedFlower" class="flower-detail">
        <div class="detail-image">
          <el-icon :size="80"><Picture /></el-icon>
        </div>
        <div class="detail-info">
          <h2 class="detail-name">{{ selectedFlower.name }}</h2>
          <p class="detail-family">{{ selectedFlower.family }}</p>

          <el-descriptions :column="2" border class="detail-descriptions">
            <el-descriptions-item label="颜色特征">
              {{ selectedFlower.color }}
            </el-descriptions-item>
            <el-descriptions-item label="花期">
              {{ selectedFlower.bloomingPeriod }}
            </el-descriptions-item>
          </el-descriptions>

          <el-divider content-position="left">特征描述</el-divider>
          <p class="detail-description">{{ selectedFlower.description }}</p>

          <el-divider content-position="left">养护方法</el-divider>
          <p class="detail-care">{{ selectedFlower.careGuide }}</p>

          <el-divider content-position="left">花语文化</el-divider>
          <p class="detail-language">{{ selectedFlower.flowerLanguage }}</p>

          <div class="detail-actions">
            <el-button type="primary" @click="startQA(selectedFlower)">
              <el-icon><ChatDotRound /></el-icon>
              发起问答
            </el-button>
            <el-button @click="addToFavorites(selectedFlower)">
              <el-icon><Star /></el-icon>
              收藏
            </el-button>
            <el-button type="success" @click="openCommentArea">评论</el-button>
            <el-button type="warning" @click="openFeedbackDialog">反馈</el-button>
            <el-button @click="detailVisible = false">关闭</el-button>
          </div>

          <div v-if="commentAreaVisible" class="comments-section">
            <el-divider content-position="left">评论</el-divider>
            <div class="comment-input">
              <el-input
                v-model="newComment"
                type="textarea"
                :rows="3"
                placeholder="发表你的看法（支持最多300字）"
                maxlength="300"
                show-word-limit
              />
              <div class="comment-actions">
                <el-button type="primary" @click="submitComment" :loading="commentSubmitting">发布评论</el-button>
                <el-button @click="commentAreaVisible = false">收起</el-button>
              </div>
            </div>
            <el-empty v-if="comments.length === 0" description="暂无评论，来发表第一条吧" />
            <div v-else class="comment-list">
              <el-card
                v-for="c in comments"
                :key="c.id"
                class="comment-item"
                shadow="never"
              >
                <div class="comment-content">{{ c.content }}</div>
                <div class="comment-meta">
                  <span class="comment-time">{{ formatTime(c.created_at) }}</span>
                  <div class="comment-actions-inline">
                    <el-button text type="primary" @click="toggleLike(c.id)">👍 {{ c.likes }}</el-button>
                    <el-button
                      v-if="canDeleteComment(c)"
                      text
                      type="danger"
                      @click="removeComment(c.id)"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
              </el-card>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <el-dialog
      v-model="feedbackDialogVisible"
      title="提交反馈"
      width="600px"
    >
      <el-input
        v-model="feedbackContent"
        type="textarea"
        :rows="5"
        placeholder="针对该花卉知识的建议或问题（最多500字）"
        maxlength="500"
        show-word-limit
      />
      <template #footer>
        <el-button @click="feedbackDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="submitFeedback" :loading="feedbackSubmitting">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Picture, ChatDotRound, Star } from '@element-plus/icons-vue'
import axios from 'axios'
import { api } from '../api/config'
import { useStore } from '@/stores'

interface Flower {
  id: number
  name: string
  family: string
  color: string
  bloomingPeriod: string
  description: string
  careGuide: string
  flowerLanguage: string
}

const router = useRouter()
const searchKeyword = ref('')
const selectedCategory = ref('')
const selectedColor = ref('')
const selectedPeriod = ref('')
const detailVisible = ref(false)
const selectedFlower = ref<Flower | null>(null)

const flowers = ref<Flower[]>([])

// 评论相关
interface CommentItem {
  id: number
  user_id: number
  flower_id: number
  content: string
  created_at: string
  likes: number
}
const comments = ref<CommentItem[]>([])
const newComment = ref('')
const commentAreaVisible = ref(false)
const commentSubmitting = ref(false)

// 反馈相关
const feedbackDialogVisible = ref(false)
const feedbackContent = ref('')
const feedbackSubmitting = ref(false)

// 科属分类
const familyCategories = ref(['蔷薇科', '菊科', '兰科', '百合科', '豆科', '仙人掌科'])

// 颜色分类
const colorCategories = ref([
  { name: '红色', value: '#F44336' },
  { name: '粉色', value: '#E91E63' },
  { name: '黄色', value: '#FFC107' },
  { name: '白色', value: '#FFFFFF' },
  { name: '蓝色', value: '#2196F3' },
  { name: '紫色', value: '#9C27B0' }
])

// 花期分类
const bloomingPeriods = ref(['春季', '夏季', '秋季', '冬季', '全年'])

// 热门花卉
const hotFlowers = ref<Flower[]>([])

const loadFlowers = async () => {
  try {
    const response = await axios.get(api.getKnowledge(searchKeyword.value))
    flowers.value = response.data.flowers || []
    // 设置热门花卉（前6个）
    hotFlowers.value = flowers.value.slice(0, 6)
  } catch (error) {
    console.error('加载知识库失败:', error)
    // 使用模拟数据
    flowers.value = [
      {
        id: 1,
        name: '月季',
        family: '蔷薇科',
        color: '红色、粉色、黄色等',
        bloomingPeriod: '5月-10月（夏秋）',
        description: '月季花被称为"花中皇后"，四季开花，花色丰富，芳香浓郁。',
        careGuide: '喜阳光充足，耐旱耐寒，但不耐水湿。春秋季可每天浇水，保持土壤湿润。生长旺季每月施肥一次。冬季适当修剪，去除病弱枝。',
        flowerLanguage: '寓意纯洁的爱、热情和祝福，是爱情的象征。'
      },
      {
        id: 2,
        name: '玫瑰',
        family: '蔷薇科',
        color: '红色、粉色、白色等',
        bloomingPeriod: '5月-10月（夏秋）',
        description: '玫瑰是世界著名的观赏植物，花形优美，香气浓郁，被称为"爱情之花"。',
        careGuide: '喜温暖、阳光充足的环境，耐寒性较强，需要充足的阳光。春秋季每天浇水，夏季早晚各浇一次。生长季每半月施肥一次。',
        flowerLanguage: '象征爱情、美丽和热情，表达真挚的情感。'
      },
      {
        id: 3,
        name: '向日葵',
        family: '菊科',
        color: '金黄色',
        bloomingPeriod: '7月-9月（夏季）',
        description: '向日葵因花序随太阳转动而得名，象征光明和希望。',
        careGuide: '喜温暖、阳光充足的环境，耐旱不耐涝。每天需6-8小时直射光照。生长期保持土壤微湿，每周浇水一次。播种后30-40天开花。',
        flowerLanguage: '寓意忠诚、爱慕、阳光和希望。'
      },
      {
        id: 4,
        name: '兰花',
        family: '兰科',
        color: '白色、紫色、绿色等',
        bloomingPeriod: '全年（不同品种）',
        description: '兰花是中国的传统名花，高雅清香，被誉为"花中君子"。',
        careGuide: '喜阴凉湿润环境，忌强光直射。保持空气湿度60%-80%。浇水要见干见湿，避免积水。生长季每月施肥一次薄肥。',
        flowerLanguage: '象征高洁、典雅、纯洁和友谊。'
      },
      {
        id: 5,
        name: '百合',
        family: '百合科',
        color: '白色、粉色、黄色等',
        bloomingPeriod: '5月-7月（春夏）',
        description: '百合花姿雅致，清香怡人，寓意百年好合。',
        careGuide: '喜凉爽、湿润的环境，耐寒怕热。春秋季每2-3天浇水一次，夏季每天浇水。种植前施足基肥，生长期追施磷钾肥。',
        flowerLanguage: '象征纯洁、高雅、百年好合和美好祝愿。'
      },
      {
        id: 6,
        name: '郁金香',
        family: '百合科',
        color: '红色、黄色、粉色、紫色等',
        bloomingPeriod: '3月-5月（春季）',
        description: '郁金香是世界著名的球根花卉，花色艳丽，花形优美。',
        careGuide: '喜凉爽、湿润、阳光充足的环境。春秋季每2-3天浇水一次，夏季休眠期停止浇水。种植前施足基肥，花期前后追施磷钾肥。',
        flowerLanguage: '象征高贵、典雅、爱情和祝福。'
      },
      {
        id: 7,
        name: '菊花',
        family: '菊科',
        color: '黄色、白色、红色等',
        bloomingPeriod: '9月-11月（秋季）',
        description: '菊花是中国十大名花之一，傲霜开放，寓意高洁。',
        careGuide: '喜阳光充足的环境，耐旱耐寒。生长季保持土壤湿润，浇水要见干见湿。春秋季每月施肥一次，夏末增施磷钾肥。',
        flowerLanguage: '象征高洁、隐逸、长寿和吉祥。'
      },
      {
        id: 8,
        name: '牡丹',
        family: '芍药科',
        color: '红色、粉色、白色、紫色等',
        bloomingPeriod: '4月-5月（春季）',
        description: '牡丹被誉为"花中之王"，雍容华贵，寓意富贵吉祥。',
        careGuide: '喜温暖、凉爽、阳光充足的环境，耐寒怕热。春秋季每2-3天浇水一次，夏季每天浇水。种植前施足基肥，生长期追施复合肥。',
        flowerLanguage: '象征富贵、吉祥、幸福和美好。'
      }
    ]
    hotFlowers.value = flowers.value.slice(0, 6)
  }
}

onMounted(() => {
  loadFlowers()
})

// 筛选逻辑
const filteredFlowers = computed(() => {
  let result = flowers.value

  // 搜索关键词
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(flower =>
      flower.name.toLowerCase().includes(keyword) ||
      flower.family.toLowerCase().includes(keyword) ||
      flower.description.toLowerCase().includes(keyword)
    )
  }

  // 科属筛选
  if (selectedCategory.value) {
    result = result.filter(flower => flower.family === selectedCategory.value)
  }

  // 颜色筛选
  if (selectedColor.value) {
    result = result.filter(flower => flower.color.includes(selectedColor.value))
  }

  // 花期筛选
  if (selectedPeriod.value) {
    result = result.filter(flower => flower.bloomingPeriod.includes(selectedPeriod.value))
  }

  return result
})

// 分类选择
const selectCategory = (category: string) => {
  selectedCategory.value = selectedCategory.value === category ? '' : category
}

const selectColor = (color: string) => {
  selectedColor.value = selectedColor.value === color ? '' : color
}

const selectPeriod = (period: string) => {
  selectedPeriod.value = selectedPeriod.value === period ? '' : period
}

const clearCategory = () => {
  selectedCategory.value = ''
  selectedColor.value = ''
  selectedPeriod.value = ''
}

const handleSearch = () => {
  // 搜索逻辑在computed中处理
}

// 查看详情
const viewDetail = (flower: Flower) => {
  selectedFlower.value = flower
  detailVisible.value = true
  commentAreaVisible.value = true
  loadComments()
}

// 发起问答
const startQA = (flower: Flower) => {
  router.push({
    path: '/qa',
    query: { flower: flower.name }
  })
  detailVisible.value = false
}

// 添加到收藏
const addToFavorites = (flower: Flower) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    ElMessage.warning('请先登录后再进行收藏')
    return
  }
  axios.post(`/api/favorites/add/${(flower as any).id || 0}`, {}, {
    headers: { Authorization: `Bearer ${token}` }
  }).then(() => {
    ElMessage.success(`已将${flower.name}添加到收藏`)
  }).catch(err => {
    ElMessage.error(err?.response?.data?.detail || '收藏失败')
  })
}

const tokenHeader = () => {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const openCommentArea = () => {
  commentAreaVisible.value = true
  loadComments()
}

const loadComments = () => {
  if (!selectedFlower.value) return
  axios.get(`/api/comments/list/${selectedFlower.value.id}`).then(({ data }) => {
    comments.value = data
  }).catch(() => {
    comments.value = []
  })
}

const submitComment = () => {
  if (!selectedFlower.value) return
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  commentSubmitting.value = true
  axios.post(
    `/api/comments/add/${selectedFlower.value.id}`,
    null,
    { params: { content: newComment.value }, headers: tokenHeader() }
  ).then(() => {
    ElMessage.success('评论已发布')
    newComment.value = ''
    loadComments()
  }).catch(err => {
    ElMessage.error(err?.response?.data?.detail || '发布失败')
  }).finally(() => {
    commentSubmitting.value = false
  })
}

const toggleLike = (commentId: number) => {
  axios.post(`/api/comments/${commentId}/like`, null, { headers: tokenHeader() }).then(() => {
    loadComments()
  })
}

const removeComment = (commentId: number) => {
  axios.delete(`/api/comments/remove/${commentId}`, { headers: tokenHeader() }).then(() => {
    ElMessage.success('评论已删除')
    loadComments()
  }).catch(err => {
    ElMessage.error(err?.response?.data?.detail || '删除失败')
  })
}

const canDeleteComment = (c: CommentItem) => {
  const userId = (useStore().auth.user?.id as any) || null
  return userId && c.user_id === userId
}

const formatTime = (iso: string) => {
  const d = new Date(iso)
  const now = new Date()
  const diff = (now.getTime() - d.getTime()) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff/60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff/3600)}小时前`
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

const openFeedbackDialog = () => {
  feedbackDialogVisible.value = true
}

const submitFeedback = () => {
  if (!selectedFlower.value) return
  if (!feedbackContent.value.trim()) {
    ElMessage.warning('请输入反馈内容')
    return
  }
  feedbackSubmitting.value = true
  axios.post(
    `/api/feedbacks/add/${selectedFlower.value.id}`,
    null,
    { params: { content: feedbackContent.value }, headers: tokenHeader() }
  ).then(() => {
    ElMessage.success('反馈已提交')
    feedbackDialogVisible.value = false
    feedbackContent.value = ''
  }).catch(err => {
    ElMessage.error(err?.response?.data?.detail || '提交失败')
  }).finally(() => {
    feedbackSubmitting.value = false
  })
}
</script>

<style scoped>
.knowledge-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0;
}

.knowledge-card {
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

.filter-section {
  margin-bottom: 32px;
}

.search-bar {
  margin-bottom: 32px;
}

.filter-title {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 18px;
  color: #333333;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

.filter-tag {
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 10px 18px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 14px;
  border-radius: 20px;
}

.color-tag {
  background-color: #FFFFFF !important;
  border-width: 2px;
}

.filter-tag:hover {
  transform: translateY(-2px);
}

.hot-section {
  margin-bottom: 32px;
}

.hot-title {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 20px;
  color: #F44336;
}

.hot-flowers {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.hot-flower-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  color: white;
}

.hot-flower-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.hot-flower-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.hot-flower-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 18px;
  margin-bottom: 4px;
}

.hot-flower-family {
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 14px;
  opacity: 0.9;
}

.section-title {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 20px;
  color: #333333;
  display: flex;
  align-items: center;
  gap: 12px;
}

.flower-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  padding: 20px 0;
}

.flower-card {
  cursor: pointer;
  transition: all 0.3s;
}

.flower-card:hover {
  transform: translateY(-4px);
}

.flower-card-image {
  height: 200px;
  background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%);
  border-radius: 8px 8px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.flower-card-content {
  padding: 20px;
}

.flower-card-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 20px;
  color: #333333;
  margin: 0 0 8px 0;
}

.flower-card-family {
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 14px;
  color: #666666;
  margin: 0 0 12px 0;
}

.flower-card-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.flower-card-description {
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 14px;
  color: #666666;
  line-height: 1.6;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.flower-card-actions {
  display: flex;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #E0E0E0;
}

.flower-detail {
  display: flex;
  gap: 32px;
}

.detail-image {
  flex: 0 0 300px;
  height: 300px;
  background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.detail-info {
  flex: 1;
}

.detail-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 32px;
  color: #4CAF50;
  margin: 0 0 8px 0;
}

.detail-family {
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 18px;
  color: #666666;
  margin: 0 0 24px 0;
}

.detail-descriptions {
  margin-bottom: 24px;
}

.detail-description,
.detail-care,
.detail-language {
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 16px;
  color: #333333;
  line-height: 1.8;
  margin: 0;
}

.detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 2px solid #E0E0E0;
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .flower-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }

  .hot-flowers {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .card-title {
    font-size: 22px;
  }

  .filter-tags {
    gap: 8px;
  }

  .filter-tag {
    font-size: 13px;
    padding: 8px 14px;
  }

  .flower-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .hot-flowers {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .flower-detail {
    flex-direction: column;
  }

  .detail-image {
    flex: none;
    width: 100%;
  }

  .detail-name {
    font-size: 24px;
  }

  .detail-actions {
    flex-direction: column;
  }

  .detail-actions .el-button {
    width: 100%;
  }
}

.comments-section {
  margin-top: 16px;
}
.comment-input {
  margin-bottom: 12px;
}
.comment-actions {
  margin-top: 8px;
  display: flex;
  gap: 8px;
}
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.comment-item {
  padding: 8px 12px;
}
.comment-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #666;
}
</style>
