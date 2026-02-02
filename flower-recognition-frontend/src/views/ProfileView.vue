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
            <h2 class="user-name">{{ store.auth.user?.username || '未登录用户' }}</h2>
            <p class="user-phone">{{ store.auth.user?.email || '未绑定邮箱' }}</p>

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
          </div>
        </el-card>

        <!-- 设置卡片 -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">⚙️ 设置</span>
            </div>
          </template>

          <div class="settings-list">
            <div class="setting-item">
              <div class="setting-info">
                <el-icon class="setting-icon"><Bell /></el-icon>
                <span>消息通知</span>
              </div>
              <el-switch v-model="settings.notification" @change="saveSettings" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <el-icon class="setting-icon"><Moon /></el-icon>
                <span>深色模式</span>
              </div>
              <el-switch v-model="settings.darkMode" @change="toggleDarkMode" />
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <el-icon class="setting-icon"><Lock /></el-icon>
                <span>隐私设置</span>
              </div>
              <el-button link type="primary" @click="openPrivacySettings">
                管理
              </el-button>
            </div>

            <el-divider />

            <el-button type="danger" style="width: 100%" @click="logout">
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
            :current-page="currentPage"
            @current-change="(p:number)=> currentPage = p"
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

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" />
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
    
    <el-dialog
      v-model="privacyDialog"
      title="隐私设置"
      width="520px"
    >
      <div class="settings-list">
        <div class="setting-item">
          <div class="setting-info">
            <el-icon class="setting-icon"><Lock /></el-icon>
            <span>显示邮箱给好友</span>
          </div>
          <el-switch v-model="privacySettings.show_email" />
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <el-icon class="setting-icon"><Lock /></el-icon>
            <span>允许好友查看识别次数</span>
          </div>
          <el-switch v-model="privacySettings.show_recognition_count" />
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <el-icon class="setting-icon"><Lock /></el-icon>
            <span>允许好友查看收藏数</span>
          </div>
          <el-switch v-model="privacySettings.show_favorites_count" />
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <el-icon class="setting-icon"><Lock /></el-icon>
            <span>允许好友查看问答次数</span>
          </div>
          <el-switch v-model="privacySettings.show_qa_count" />
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <el-icon class="setting-icon"><Lock /></el-icon>
            <span>允许好友查看收藏列表</span>
          </div>
          <el-switch v-model="privacySettings.show_favorites_list" />
        </div>
      </div>
      <template #footer>
        <el-button @click="privacyDialog = false">取消</el-button>
        <el-button type="primary" @click="savePrivacy" :loading="privacySaving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useStore } from '@/stores'
import axios from 'axios'
import {
  User,
  Edit,
  Bell,
  Moon,
  Lock,
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
  phone: string
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
  phone: '',
  bio: '热爱花卉，享受自然',
  recognitionCount: 0,
  favoritesCount: 0,
  qaCount: 0
})

const settings = ref({
  notification: true,
  darkMode: false
})

const favorites = ref<FavoriteItem[]>([])

const pageSize = 8
let currentPage = 1
const pagedFavorites = computed(() => {
  const start = (currentPage - 1) * pageSize
  return filteredFavorites.value.slice(start, start + pageSize)
})

const tokenHeader = () => {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const loadStats = () => {
  axios.get('/api/user/stats', { headers: tokenHeader() }).then(({data}) => {
    userInfo.value.recognitionCount = data.recognitionCount
    userInfo.value.favoritesCount = data.favoritesCount
    userInfo.value.qaCount = data.qaCount
  })
}

const loadFavorites = () => {
  axios.get('/api/favorites/list', { headers: tokenHeader() }).then(({data}) => {
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

loadStats()
loadFavorites()

const searchFavorite = ref('')
const editProfileDialog = ref(false)
const saving = ref(false)
const profileFormRef = ref<FormInstance>()

const editForm = ref({
  avatar: '',
  nickname: '',
  phone: '',
  bio: ''
})

const profileRules: FormRules = {
  nickname: [
    { required: true, message: '请输入昵称', trigger: 'blur' },
    { min: 2, max: 20, message: '昵称长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
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

const toggleDarkMode = () => {
  const root = document.documentElement
  if (settings.value.darkMode) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
  ElMessage.success('已切换主题')
}

const saveSettings = () => {
  ElMessage.success('设置已更新')
}

const privacyDialog = ref(false)
const privacySaving = ref(false)
const privacySettings = ref({
  show_email: true,
  show_recognition_count: true,
  show_favorites_count: true,
  show_qa_count: true,
  show_favorites_list: true
})
const openPrivacySettings = () => {
  privacyDialog.value = true
}
const savePrivacy = () => {
  privacySaving.value = true
  axios.post('/api/friends/privacy/save', privacySettings.value, { headers: tokenHeader() }).then(() => {
    ElMessage.success('隐私设置已保存')
    privacyDialog.value = false
  }).catch(err => {
    ElMessage.error(err?.response?.data?.detail || '保存失败')
  }).finally(() => {
    privacySaving.value = false
  })
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
    router.push('/hua-shi-jie/')
  } catch {
    // 用户取消
  }
}

const handleAvatarChange = (file: any) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    editForm.value.avatar = e.target?.result as string
  }
  reader.readAsDataURL(file.raw)
}

const saveProfile = async () => {
  if (!profileFormRef.value) return

  await profileFormRef.value.validate((valid) => {
    if (valid) {
      saving.value = true
      setTimeout(() => {
        userInfo.value = {
          ...userInfo.value,
          avatar: editForm.value.avatar || userInfo.value.avatar,
          nickname: editForm.value.nickname,
          phone: editForm.value.phone,
          bio: editForm.value.bio
        }
        saving.value = false
        editProfileDialog.value = false
        ElMessage.success('个人信息已更新')
      }, 1000)
    }
  })
}

const viewDetail = (flower: FavoriteItem) => {
  ElMessage.info(`查看${flower.name}的详情`)
}

const askQuestion = (flower: FavoriteItem) => {
  router.push({
    path: '/hua-shi-jie/qa',
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
    favorites.value = favorites.value.filter(f => f.id !== id)
    userInfo.value.favoritesCount--
    ElMessage.success('已取消收藏')
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
  max-height: 720px;
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

.user-phone {
  font-size: 14px;
  color: #666666;
  margin: 0;
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
