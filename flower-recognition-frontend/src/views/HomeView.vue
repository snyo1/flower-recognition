<template>
  <div class="home-page">
    <div class="home-layout">
      <!-- 左侧：上传控制区 -->
      <div class="layout-left">
        <el-card class="upload-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">上传花卉图片</span>
              <el-icon class="header-icon" :size="24"><Camera /></el-icon>
            </div>
          </template>

          <div class="upload-section">
            <el-upload
              ref="uploadRef"
              class="upload-demo"
              drag
              multiple
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="fileList"
              accept="image/jpeg,image/png"
            >
              <div class="upload-content">
                <el-icon class="upload-icon" :size="48"><UploadFilled /></el-icon>
                <div class="upload-text-primary">上传图片进行识别</div>
                <div class="upload-text-secondary">支持批量识别 (JPG/PNG)</div>
              </div>
            </el-upload>
          </div>

          <div v-if="previewUrls.length > 0" class="preview-section">
            <el-scrollbar max-height="300px">
              <div class="preview-grid">
                <div v-for="(url, index) in previewUrls" :key="index" class="preview-container">
                  <el-image :src="url" fit="cover" class="preview-image-small" />
                  <el-button
                    class="delete-btn-small"
                    type="danger"
                    :icon="Delete"
                    circle
                    size="small"
                    @click="removeFile(index)"
                  />
                </div>
              </div>
            </el-scrollbar>
          </div>

          <div class="action-buttons">
            <el-button class="btn-secondary" :icon="Upload" @click="triggerFileUpload">
              选择图片
            </el-button>
            <el-button
              type="primary"
              class="btn-primary"
              :icon="Camera"
              :disabled="previewUrls.length === 0"
              @click="identifyFlower"
              :loading="identifying"
            >
              {{ previewUrls.length > 1 ? '批量识别' : '开始识别' }}
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 右侧：识别结果与科普信息 -->
      <div class="layout-right">
        <el-card class="results-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">识别结果与科普</span>
              <el-tag v-if="results.length > 0" type="success" effect="dark">
                已识别 {{ results.length }} 个结果
              </el-tag>
            </div>
          </template>

          <div class="results-scroll-container">
            <el-scrollbar v-if="results.length > 0" height="calc(100vh - 250px)">
              <div class="results-list">
                <el-card v-for="(res, idx) in results" :key="idx" class="result-card" shadow="hover">
                  <div class="result-layout">
                    <!-- 结果卡片左侧：图片 -->
                    <div class="result-image-box">
                      <el-image
                        :src="res.imagePreview || previewUrls[idx]"
                        fit="cover"
                        class="result-image"
                        :preview-src-list="[res.imagePreview || previewUrls[idx]]"
                      />
                      <div class="confidence-tag">
                        置信度: {{ res.confidence }}%
                      </div>
                    </div>

                    <!-- 结果卡片右侧：信息 -->
                    <div class="result-info-box">
                      <div class="info-header">
                        <h2 class="flower-name">{{ res.name }}</h2>
                        <el-tag size="small" effect="plain">{{ res.family }}</el-tag>
                      </div>

                      <el-descriptions :column="1" size="small" border class="info-desc">
                        <el-descriptions-item label="颜色">{{ res.color }}</el-descriptions-item>
                        <el-descriptions-item label="花期">{{ res.bloomingPeriod }}</el-descriptions-item>
                      </el-descriptions>

                      <div class="info-content">
                        <el-collapse accordion>
                          <el-collapse-item title="特征描述" :name="'desc' + idx">
                            <p class="content-p">{{ res.description }}</p>
                          </el-collapse-item>
                          <el-collapse-item title="养护方法" :name="'care' + idx">
                            <p class="content-p">{{ res.careGuide }}</p>
                          </el-collapse-item>
                          <el-collapse-item title="花语文化" :name="'lang' + idx">
                            <p class="content-p">{{ res.flowerLanguage }}</p>
                          </el-collapse-item>
                        </el-collapse>
                      </div>

                      <div class="info-footer">
                        <el-button-group>
                          <el-button 
                            size="small" 
                            :type="res.isFavorite ? 'warning' : 'default'"
                            :icon="res.isFavorite ? Check : Star" 
                            @click="toggleFavorite(res)"
                          >
                            {{ res.isFavorite ? '已收藏' : '收藏' }}
                          </el-button>
                          <el-button size="small" :icon="Share" @click="shareResult(res)">分享</el-button>
                          <el-button size="small" type="primary" :icon="ChatDotRound" @click="goToQA(res)">问答</el-button>
                        </el-button-group>
                      </div>
                    </div>
                  </div>
                </el-card>
              </div>
            </el-scrollbar>
            <el-empty v-else description="暂无识别结果，请在左侧上传图片" :image-size="200" />
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled,
  Upload,
  Camera,
  Delete,
  Check,
  Star,
  Share,
  ChatDotRound,
  User
} from '@element-plus/icons-vue'
import type { UploadInstance, UploadProps } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { api } from '../api/config'

const router = useRouter()
const uploadRef = ref<UploadInstance>()
const fileList = ref<any[]>([])
const previewUrls = ref<string[]>([])
const identifying = ref(false)
const activeCollapse = ref('')
const isFavorite = ref(false)

interface RecognitionResult {
  id?: number
  name: string
  family: string
  color: string
  bloomingPeriod: string
  description: string
  careGuide: string
  flowerLanguage: string
  confidence: number
  imagePreview?: string
  isFavorite?: boolean
}

const results = ref<RecognitionResult[]>([])

const handleFileChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  if (uploadFile.raw) {
    const file = uploadFile.raw

    // 验证文件类型
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg']
    if (!validTypes.includes(file.type)) {
      ElMessage.error('请上传JPG/PNG格式的图片')
      return
    }

    // 验证文件大小
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.error('图片过大，请压缩后上传')
      return
    }

    previewUrls.value.push(URL.createObjectURL(file))
    fileList.value.push(uploadFile)
    results.value = []
  }
}

const removeFile = (index: number) => {
  previewUrls.value.splice(index, 1)
  fileList.value.splice(index, 1)
}

const identifyFlower = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先上传图片')
    return
  }

  identifying.value = true
  results.value = []

  try {
    const formData = new FormData()
    const token = localStorage.getItem('access_token')
    
    let apiUrl = api.identify
    if (fileList.value.length > 1) {
      apiUrl = api.identify.replace('/identify', '/batch-identify')
      fileList.value.forEach(file => {
        formData.append('files', file.raw)
      })
    } else {
      formData.append('file', fileList.value[0].raw)
    }

    const response = await axios.post(apiUrl, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      }
    })

    if (fileList.value.length > 1) {
      results.value = response.data.results
    } else {
      results.value = [response.data]
    }
    
    ElMessage.success('识别完成！')
  } catch (error) {
    console.error('识别失败:', error)
    ElMessage.error('识别过程中出现错误，请稍后重试')
  } finally {
    identifying.value = false
  }
}

const resetUpload = () => {
  previewUrls.value = []
  fileList.value = []
  results.value = []
  uploadRef.value?.clearFiles()
}

const goToQA = (res: RecognitionResult) => {
  router.push({
    path: '/qa',
    query: { flower: res.name }
  })
}

const toggleFavorite = async (res: RecognitionResult) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    ElMessage.warning('请先登录后再进行收藏')
    return
  }

  try {
    if (!res.isFavorite) {
      // 添加收藏
      await axios.post(`/api/favorites/add/${res.id}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      })
      res.isFavorite = true
      ElMessage.success(`已将${res.name}添加到收藏`)
    } else {
      // 取消收藏
      await axios.delete(`/api/favorites/remove/${res.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      res.isFavorite = false
      ElMessage.success(`已取消${res.name}的收藏`)
    }
    
    // 同时更新本地存储（作为备份，虽然后端已持久化）
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')
    if (res.isFavorite) {
      if (!favorites.find((f: any) => f.name === res.name)) {
        favorites.push({ ...res, timestamp: Date.now() })
      }
    } else {
      const idx = favorites.findIndex((f: any) => f.name === res.name)
      if (idx !== -1) favorites.splice(idx, 1)
    }
    localStorage.setItem('favorites', JSON.stringify(favorites))
  } catch (error) {
    console.error('收藏操作失败:', error)
    ElMessage.error('操作失败，请重试')
  }
}

const shareResult = (res: RecognitionResult) => {
  const shareText = `我刚刚识别出了一朵${res.name}！\n${res.family} | ${res.color}\n${res.description}\n\n快来试试智能花卉识别系统吧！`
  copyToClipboard(shareText)
}

const copyToClipboard = (text: string) => {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => {
      ElMessage.success('识别结果已复制到剪贴板')
    }).catch(() => {
      ElMessage.warning('复制失败，请手动复制')
    })
  } else {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      ElMessage.success('识别结果已复制到剪贴板')
    } catch (err) {
      ElMessage.warning('复制失败，请手动复制')
    }
    document.body.removeChild(textarea)
  }
}

const triggerFileUpload = () => {
  const input = document.querySelector('.el-upload__input') as HTMLInputElement
  input?.click()
}
</script>

<style scoped>
.home-page {
  padding: 20px;
  height: calc(100vh - 100px);
  overflow: hidden;
}

.home-layout {
  display: flex;
  gap: 20px;
  height: 100%;
}

.layout-left {
  flex: 0 0 400px;
  display: flex;
  flex-direction: column;
}

.layout-right {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.upload-card, .results-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.el-card__body) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-weight: bold;
  font-size: 18px;
}

.upload-section {
  padding: 10px 0;
}

:deep(.el-upload-dragger) {
  padding: 20px 10px;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.upload-text-primary {
  font-weight: bold;
  font-size: 14px;
}

.upload-text-secondary {
  font-size: 12px;
  color: #999;
}

.preview-section {
  margin-top: 15px;
  flex: 1;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 5px;
}

.preview-container {
  position: relative;
}

.preview-image-small {
  width: 100%;
  height: 120px;
  border-radius: 8px;
}

.delete-btn-small {
  position: absolute;
  top: -5px;
  right: -5px;
}

.action-buttons {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.btn-primary, .btn-secondary {
  flex: 1;
}

/* 结果列表样式 */
.results-scroll-container {
  flex: 1;
  overflow: hidden;
}

.result-card {
  margin-bottom: 15px;
}

.result-layout {
  display: flex;
  gap: 20px;
}

.result-image-box {
  flex: 0 0 180px;
  position: relative;
}

.result-image {
  width: 180px;
  height: 180px;
  border-radius: 8px;
  cursor: pointer;
}

.confidence-tag {
  position: absolute;
  bottom: 5px;
  left: 5px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.result-info-box {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.flower-name {
  margin: 0;
  font-size: 20px;
  color: #409EFF;
}

.info-desc {
  margin: 5px 0;
}

.content-p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #666;
}

.info-footer {
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .home-layout {
    flex-direction: column;
    overflow: auto;
  }
  .layout-left {
    flex: none;
    width: 100%;
  }
  .home-page {
    height: auto;
    overflow: auto;
  }
}
</style>
