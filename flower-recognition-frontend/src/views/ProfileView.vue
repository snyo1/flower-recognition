<template>
  <div class="profile-page">
    <el-row :gutter="24">
      <!-- 左侧：个人信息卡片 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">个人信息</span>
              <el-button link type="primary" @click="editProfileDialog = true">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
            </div>
          </template>

          <div class="profile-content">
            <div class="avatar-section">
              <el-avatar :size="100" :src="userInfo.avatar">
                <el-icon :size="50"><User /></el-icon>
              </el-avatar>
            </div>
            <h2 class="user-name">{{ userInfo.nickname || '未设置昵称' }}</h2>
            <p class="user-username">用户名：{{ store.auth.user?.username || '未知' }}</p>
            <p class="user-email">{{ store.auth.user?.email || '未绑定邮箱' }}</p>
            <p class="user-bio">{{ userInfo.bio }}</p>

            <el-divider />

            <div class="stats-section">
              <div class="stat-item">
                <div class="stat-value">{{ userInfo.recognitionCount }}</div>
                <div class="stat-label">识别次数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userInfo.favoritesCount }}</div>
                <div class="stat-label">收藏数</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userInfo.qaCount }}</div>
                <div class="stat-label">问答次数</div>
              </div>
            </div>

            <el-divider />

            <el-button type="danger" plain style="width: 100%" @click="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：收藏列表 -->
      <el-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
        <el-card class="favorites-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">❤️ 我的收藏</span>
              <div class="header-actions">
                <el-input
                  v-model="searchFavorite"
                  placeholder="搜索收藏的花卉"
                  clearable
                  style="width: 200px"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
            </div>
          </template>

          <div v-if="filteredFavorites.length === 0" class="empty-state">
            <el-empty description="暂无收藏的花卉" />
          </div>

          <div v-else class="favorites-grid">
            <el-card
              v-for="flower in pagedFavorites"
              :key="flower.id"
              class="favorite-card"
              shadow="hover"
            >
              <div class="favorite-card-image">
                <el-icon :size="40"><Picture /></el-icon>
              </div>
              <div class="favorite-card-content">
                <h3 class="favorite-name">{{ flower.name }}</h3>
                <p class="favorite-family">{{ flower.family }}</p>
                <div class="favorite-tags">
                  <el-tag size="small" type="info">{{ flower.color }}</el-tag>
                  <el-tag size="small" type="success">{{ flower.bloomingPeriod }}</el-tag>
                </div>
                <div class="favorite-time">
                  <el-icon><Clock /></el-icon>
                  {{ formatFavoriteTime(flower.timestamp) }}
                </div>
                <div class="favorite-actions">
                  <el-button type="primary" link size="small" @click="viewDetail(flower)">
                    查看详情
                  </el-button>
                  <el-button type="primary" link size="small" @click="askQuestion(flower)">
                    询问
                  </el-button>
                  <el-button type="danger" link size="small" @click="removeFavorite(flower.id)">
                    取消收藏
                  </el-button>
                </div>
              </div>
            </el-card>
          </div>
        </el-card>
        <div class="pagination-wrapper" v-if="filteredFavorites.length > pageSize">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="filteredFavorites.length"
            :page-size="pageSize"
            v-model:current-page="currentPage"
          />
        </div>
      </el-col>
    </el-row>

    <!-- 编辑个人信息对话框 -->
    <el-dialog
      v-model="editProfileDialog"
      title="编辑个人信息"
      width="500px"
    >
      <el-form
        ref="profileFormRef"
        :model="editForm"
        :rules="profileRules"
        label-width="100px"
      >
        <el-form-item label="头像">
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept="image/*"
            :on-change="handleAvatarChange"
          >
            <el-avatar :size="80" :src="editForm.avatar">
              <el-icon><Plus /></el-icon>
            </el-avatar>
            <div class="upload-tip">点击更换头像</div>
          </el-upload>
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="editForm.nickname" placeholder="请输入昵称" />
        </el-form-item>

        <el-form-item label="个人简介">
          <el-input
            v-model="editForm.bio"
            type="textarea"
            :rows="3"
            placeholder="介绍一下自己吧"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editProfileDialog = false">取消</el-button>
        <el-button type="primary" @click="saveProfile" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useStore } from '@/stores'
import { get, post, del } from '@/net'
import axios from 'axios'
import {
  User,
  Edit,
  Bell,
  Moon,
  SwitchButton,
  Picture,
  Clock,
  Search,
  Plus
} from '@element-plus/icons-vue'

const router = useRouter()
const store = useStore()

interface UserInfo {
  avatar: string
  nickname: string
  bio: string
  recognitionCount: number
  favoritesCount: number
  qaCount: number
}

interface FavoriteItem {
  id: number
  name: string
  family: string
  color: string
  bloomingPeriod: string
  description: string
  timestamp: number
}

const userInfo = ref<UserInfo>({
  avatar: '',
  nickname: '',
  bio: '热爱花卉，享受自然',
  recognitionCount: 0,
  favoritesCount: 0,
  qaCount: 0
})

const favorites = ref<FavoriteItem[]>([])

const searchFavorite = ref('')
const editProfileDialog = ref(false)
const saving = ref(false)
const profileFormRef = ref<FormInstance>()
const currentPage = ref(1)
const pageSize = 8

const editForm = ref({
  avatar: '',
  nickname: '',
  bio: ''
})

const profileRules: FormRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度在 2 到 20 个字符', trigger: 'blur' }
  ]
}

const filteredFavorites = computed(() => {
  if (!searchFavorite.value) {
    return favorites.value
  }
  const keyword = searchFavorite.value.toLowerCase()
  return favorites.value.filter(flower =>
    flower.name.toLowerCase().includes(keyword) ||
    flower.family.toLowerCase().includes(keyword)
  )
})

const pagedFavorites = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredFavorites.value.slice(start, start + pageSize)
})

const tokenHeader = () => {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const loadStats = () => {
  get('/api/user/stats', (data) => {
    userInfo.value.recognitionCount = data.recognitionCount
    userInfo.value.favoritesCount = data.favoritesCount
    userInfo.value.qaCount = data.qaCount
  })
}

const loadFavorites = () => {
  get('/api/favorites/list', (data) => {
    favorites.value = data.map((d:any) => ({
      id: d.flower_id,
      name: d.name,
      family: d.family,
      color: d.color,
      bloomingPeriod: d.bloomingPeriod,
      description: d.description,
      timestamp: Date.parse(d.timestamp),
    }))
  })
}

const loadUserInfo = () => {
  get('api/user/me', (data) => {
    store.auth.user = data
    userInfo.value.nickname = data.nickname || ''
    userInfo.value.avatar = data.avatar || ''
    userInfo.value.bio = data.bio || '热爱花卉，享受自然'
  })
}

const refreshData = () => {
  loadUserInfo()
  loadStats()
  loadFavorites()
}

onMounted(() => {
  refreshData()
})

onActivated(() => {
  refreshData()
})

// 监听对话框打开，初始化编辑表单
watch(() => editProfileDialog.value, (val) => {
  if (val) {
    editForm.value = {
      avatar: userInfo.value.avatar,
      nickname: userInfo.value.nickname,
      bio: userInfo.value.bio
    }
  }
})

const formatFavoriteTime = (timestamp: number) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  if (days < 30) return `${Math.floor(days / 7)}周前`

  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const logout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    localStorage.removeItem('access_token')
    store.auth.user = null
    ElMessage.success('已退出登录')
    router.push('/')
  } catch {
    // 用户取消
  }
}

const handleAvatarChange = (file: any) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const img = new Image()
    img.onload = () => {
      // 创建 canvas 进行压缩
      const canvas = document.createElement('canvas')
      let width = img.width
      let height = img.height
      const maxSide = 400 // 头像不需要太大，限制最大边长为 400px

      if (width > height) {
        if (width > maxSide) {
          height = Math.round((height * maxSide) / width)
          width = maxSide
        }
      } else {
        if (height > maxSide) {
          width = Math.round((width * maxSide) / height)
          height = maxSide
        }
      }

      canvas.width = width
      canvas.height = height
      const ctx = canvas.getContext('2d')
      ctx?.drawImage(img, 0, 0, width, height)

      // 转换为较小的 base64 字符串 (jpeg 格式，0.7 质量)
      const compressedBase64 = canvas.toDataURL('image/jpeg', 0.7)
      editForm.value.avatar = compressedBase64
    }
    img.src = e.target?.result as string
  }
  reader.readAsDataURL(file.raw)
}

const saveProfile = async () => {
  if (!profileFormRef.value) return

  await profileFormRef.value.validate((valid) => {
    if (valid) {
      saving.value = true
      const token = localStorage.getItem('access_token')
      axios.put('/api/user/profile', {
        avatar: editForm.value.avatar,
        nickname: editForm.value.nickname,
        bio: editForm.value.bio
      }, {
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      }).then(() => {
        userInfo.value.avatar = editForm.value.avatar || userInfo.value.avatar
        userInfo.value.nickname = editForm.value.nickname
        userInfo.value.bio = editForm.value.bio
        if (store.auth.user) {
          store.auth.user.username = editForm.value.nickname
        }
        ElMessage.success('个人信息已更新')
        editProfileDialog.value = false
      }).catch(() => {
        ElMessage.error('保存失败，请稍后重试')
      }).finally(() => {
        saving.value = false
      })
    }
  })
}

const viewDetail = (flower: FavoriteItem) => {
  ElMessage.info(`查看${flower.name}的详情`)
}

const askQuestion = (flower: FavoriteItem) => {
  router.push({
    path: '/qa',
    query: { flower: flower.name }
  })
}

const removeFavorite = async (id: number) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消收藏吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    del(`/api/favorites/remove/${id}`, () => {
      favorites.value = favorites.value.filter(f => f.id !== id)
      userInfo.value.favoritesCount--
      ElMessage.success('已取消收藏')
    })
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.dark {
  --bg-color: #1f1f1f;
  --text-color: #e5e5e5;
  --card-bg: #2a2a2a;
  --border-color: #3a3a3a;
}

.profile-card, .settings-card, .favorites-card {
  background-color: var(--card-bg, #fff);
  color: var(--text-color, #333);
}

.card-title {
  color: var(--text-color, #333333);
}

.favorite-actions .el-button[type="primary"] {
  color: #0052cc;
}
.favorite-actions .el-button[type="danger"] {
  color: #d93025;
}

.el-button.btn-strong {
  background-color: #0052cc;
  color: #ffffff;
}
.el-button.btn-strong:hover {
  filter: brightness(1.05);
}
.profile-page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0;
}

.profile-card,
.settings-card,
.favorites-card {
  margin-bottom: 24px;
  height: 720px;
  display: flex;
  flex-direction: column;
}

:deep(.el-card__body) {
  flex: 1;
  overflow-y: auto;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 24px;
  color: #333333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 个人信息卡片 */
.profile-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.avatar-section {
  position: relative;
  cursor: pointer;
}

.user-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 24px;
  color: #333333;
  margin: 0;
}

.user-email {
  font-size: 14px;
  color: #666666;
  margin: 0;
}

.user-bio {
  font-size: 14px;
  color: #888888;
  margin-top: 8px;
  text-align: center;
  max-width: 80%;
}

.stats-section {
  display: flex;
  justify-content: space-around;
  width: 100%;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 28px;
  color: #4CAF50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666666;
}

/* 设置卡片 */
.settings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}

.setting-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.setting-icon {
  font-size: 18px;
  color: #666666;
}

/* 收藏卡片 */
.empty-state {
  padding: 60px 0;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 20px 0;
}
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 12px;
}

.favorite-card {
  cursor: pointer;
  transition: all 0.3s;
}

.favorite-card:hover {
  transform: translateY(-4px);
}

.favorite-card-image {
  height: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px 8px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.favorite-card-content {
  padding: 16px;
}

.favorite-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 18px;
  color: #333333;
  margin: 0 0 8px 0;
}

.favorite-family {
  font-size: 14px;
  color: #666666;
  margin: 0 0 12px 0;
}

.favorite-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.favorite-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999999;
  margin-bottom: 12px;
}

.favorite-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #E0E0E0;
  justify-content: space-between;
}

/* 编辑对话框 */
.upload-tip {
  font-size: 12px;
  color: #666666;
  margin-top: 8px;
  text-align: center;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .card-title {
    font-size: 20px;
  }

  .stats-section {
    padding: 16px 0;
  }

  .stat-value {
    font-size: 24px;
  }

  .favorites-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .favorite-time {
    margin-bottom: 8px;
  }

  .favorite-actions {
    flex-direction: column;
  }

  .favorite-actions .el-button {
    width: 100%;
  }
}
</style>
