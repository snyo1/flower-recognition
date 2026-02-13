<template>
  <div class="home-page">
    <!-- 上传中心页面 -->
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">上传花卉图片</span>
          <el-icon class="header-icon" :size="24"><User /></el-icon>
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
            <div class="upload-text-primary">上传花卉图片</div>
            <div class="upload-text-secondary">支持多张图片批量识别 (JPG/PNG格式)</div>
          </div>
        </el-upload>
      </div>

      <div v-if="previewUrls.length > 0" class="preview-section">
        <div class="preview-grid">
          <div v-for="(url, index) in previewUrls" :key="index" class="preview-container">
            <el-image
              :src="url"
              fit="cover"
              class="preview-image-small"
            />
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
      </div>

      <div class="action-buttons">
        <el-button
          class="btn-secondary"
          :icon="Upload"
          @click="triggerFileUpload"
        >
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

    <!-- 识别结果列表 -->
    <div v-if="results.length > 0" class="results-list">
      <el-divider content-position="center">识别结果 ({{ results.length }})</el-divider>
      
      <el-card v-for="(res, idx) in results" :key="idx" class="result-card">
        <div class="result-layout">
          <!-- 左侧：原图展示区 -->
          <div class="result-left">
            <div class="image-container">
              <el-image
                :src="res.imagePreview || previewUrls[idx]"
                fit="contain"
                class="result-image"
              />
              <div class="confidence-badge">
                <el-icon class="badge-icon"><Check /></el-icon>
                <span>识别准确率：{{ res.confidence }}%</span>
              </div>
            </div>
          </div>

          <!-- 右侧：识别信息区 -->
          <div class="result-right">
            <!-- 一级信息 -->
            <div class="result-section-primary">
              <h2 class="flower-name">{{ res.name }}</h2>
              <p class="flower-family">{{ res.family }}</p>
            </div>

            <!-- 二级信息 -->
            <el-descriptions :column="1" border class="result-descriptions">
              <el-descriptions-item label="颜色特征">
                {{ res.color }}
              </el-descriptions-item>
              <el-descriptions-item label="花期">
                {{ res.bloomingPeriod }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- 三级信息 - 科普内容 -->
            <div class="result-section-content">
              <el-collapse accordion>
                <el-collapse-item title="特征描述" :name="'description' + idx">
                  <p class="content-text">{{ res.description }}</p>
                </el-collapse-item>
                <el-collapse-item title="养护方法" :name="'care' + idx">
                  <p class="content-text">{{ res.careGuide }}</p>
                </el-collapse-item>
                <el-collapse-item title="花语文化" :name="'language' + idx">
                  <p class="content-text">{{ res.flowerLanguage }}</p>
                </el-collapse-item>
              </el-collapse>
            </div>

            <!-- 操作按钮区 -->
            <div class="result-actions">
              <el-button class="action-btn" :icon="Star" circle @click="toggleFavorite(res)" />
              <el-button class="action-btn" :icon="Share" circle @click="shareResult(res)" />
              <el-button
                type="primary"
                class="btn-qa"
                :icon="ChatDotRound"
                @click="goToQA(res)"
              >
                发起问答
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
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
  name: string
  family: string
  color: string
  bloomingPeriod: string
  description: string
  careGuide: string
  flowerLanguage: string
  confidence: number
  imagePreview?: string
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

const toggleFavorite = (res: RecognitionResult) => {
  // 保存收藏到本地存储
  const favorites = JSON.parse(localStorage.getItem('favorites') || '[]')
  const favoriteItem = {
    id: Date.now(),
    ...res,
    timestamp: Date.now()
  }

  const index = favorites.findIndex((f: any) => f.name === res.name)
  if (index === -1) {
    favorites.push(favoriteItem)
    localStorage.setItem('favorites', JSON.stringify(favorites))
    ElMessage.success(`已将${res.name}添加到收藏`)
  } else {
    favorites.splice(index, 1)
    localStorage.setItem('favorites', JSON.stringify(favorites))
    ElMessage.success(`已取消${res.name}的收藏`)
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
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0;
}

.upload-card {
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

.header-icon {
  color: #4CAF50;
  cursor: pointer;
}

.upload-section {
  padding: 48px 24px;
}

.upload-demo {
  width: 100%;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 80px 48px;
}

.upload-icon {
  color: #4CAF50;
  font-size: 64px;
}

.upload-text-primary {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 20px;
  color: #333333;
}

.upload-text-secondary {
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 16px;
  color: #666666;
}

:deep(.el-upload-dragger) {
  background-color: #E8F5E8;
  border: 2px dashed #4CAF50;
  border-radius: 12px;
  transition: all 0.3s;
}

:deep(.el-upload-dragger:hover) {
  background-color: #C8E6C9;
  border-color: #43A047;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.preview-image-small {
  width: 100%;
  height: 150px;
  border-radius: 8px;
  object-fit: cover;
}

.delete-btn-small {
  position: absolute;
  top: -8px;
  right: -8px;
  z-index: 10;
}

.results-list {
  margin-top: 40px;
}

.result-card {
  margin-bottom: 24px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 32px;
  padding-top: 32px;
  border-top: 2px solid #E0E0E0;
  flex-wrap: wrap;
}

.btn-secondary {
  background-color: #E0E0E0;
  border-color: #E0E0E0;
  color: #333333;
  border-radius: 10px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 18px;
  padding: 14px 32px;
}

.btn-primary {
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

.btn-primary:hover {
  background-color: #43A047;
  border-color: #43A047;
  box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4);
}

.btn-primary:disabled {
  background-color: #E0E0E0;
  border-color: #E0E0E0;
  color: #999999;
  box-shadow: none;
}

/* 识别结果页样式 */
.result-card {
  margin-top: 32px;
}

.result-layout {
  display: flex;
  gap: 32px;
}

.result-left {
  flex: 0 0 42%;
  min-width: 0;
}

.result-right {
  flex: 1;
  min-width: 0;
}

.image-container {
  position: relative;
}

.result-image {
  width: 100%;
  max-height: 550px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 3px solid #4CAF50;
}

.confidence-badge {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background-color: rgba(76, 175, 80, 0.95);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.badge-icon {
  font-size: 20px;
}

.result-section-primary {
  margin-bottom: 28px;
}

.flower-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 32px;
  color: #4CAF50;
  margin: 0 0 12px 0;
}

.flower-family {
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 18px;
  color: #666666;
  margin: 0;
}

.result-descriptions {
  margin-bottom: 28px;
}

.result-section-content {
  margin-bottom: 28px;
}

.content-text {
  font-family: 'Roboto', sans-serif;
  font-weight: 400;
  font-size: 17px;
  color: #333333;
  line-height: 1.9;
  margin: 0;
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 20px;
  border-top: 2px solid #E0E0E0;
  flex-wrap: wrap;
}

.action-btn {
  background-color: #FFFFFF;
  border: 1px solid #E0E0E0;
  border-radius: 50%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 10px;
}

.action-btn:hover {
  background-color: #F5F5F5;
  border-color: #4CAF50;
  color: #4CAF50;
}

.btn-qa {
  margin-left: auto;
  background-color: #4CAF50;
  border-color: #4CAF50;
  color: white;
  border-radius: 10px;
  font-family: 'Roboto', sans-serif;
  font-weight: 700;
  font-size: 18px;
  padding: 14px 32px;
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
}

.btn-qa:hover {
  background-color: #43A047;
  border-color: #43A047;
  box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4);
}

/* 响应式布局 - 中等屏幕 (≤1400px) */
@media (max-width: 1400px) {
  .home-page {
    padding: 0;
  }

  .card-title {
    font-size: 26px;
  }

  .upload-content {
    padding: 70px 40px;
  }

  .upload-icon {
    font-size: 56px;
  }

  .upload-text-primary {
    font-size: 19px;
  }

  .upload-text-secondary {
    font-size: 15px;
  }

  .flower-name {
    font-size: 30px;
  }

  .flower-family {
    font-size: 17px;
  }

  .content-text {
    font-size: 16px;
  }

  .preview-image,
  .result-image {
    max-height: 480px;
  }

  .result-left {
    flex: 0 0 40%;
  }
}

/* 响应式布局 - 小屏幕 (≤1200px) */
@media (max-width: 1200px) {
  .card-title {
    font-size: 24px;
  }

  .upload-section {
    padding: 40px 20px;
  }

  .upload-content {
    padding: 60px 32px;
  }

  .upload-icon {
    font-size: 48px;
  }

  .upload-text-primary {
    font-size: 18px;
  }

  .upload-text-secondary {
    font-size: 14px;
  }

  .flower-name {
    font-size: 26px;
  }

  .flower-family {
    font-size: 16px;
  }

  .content-text {
    font-size: 16px;
  }

  .result-left {
    flex: 0 0 38%;
  }

  .preview-image,
  .result-image {
    max-height: 420px;
  }
}

/* 响应式布局 - 平板 (≤992px) */
@media (max-width: 992px) {
  .card-title {
    font-size: 22px;
  }

  .upload-content {
    padding: 50px 28px;
  }

  .upload-icon {
    font-size: 42px;
  }

  .upload-text-primary {
    font-size: 17px;
  }

  .upload-text-secondary {
    font-size: 14px;
  }

  .flower-name {
    font-size: 24px;
  }

  .flower-family {
    font-size: 15px;
  }

  .content-text {
    font-size: 15px;
  }

  .preview-image,
  .result-image {
    max-height: 380px;
  }

  .result-left {
    flex: 0 0 35%;
  }

  .confidence-badge {
    padding: 10px 16px;
    font-size: 14px;
  }
}

/* 响应式布局 - 移动端 (≤768px) */
@media (max-width: 768px) {
  .home-page {
    padding: 0;
  }

  .card-title {
    font-size: 20px;
  }

  .upload-section {
    padding: 32px 12px;
  }

  .upload-content {
    padding: 40px 20px;
  }

  .upload-icon {
    font-size: 36px;
  }

  .upload-text-primary {
    font-size: 16px;
  }

  .upload-text-secondary {
    font-size: 13px;
  }

  /* 左右分栏改为上下布局 */
  .result-layout {
    flex-direction: column;
    gap: 20px;
  }

  .result-left,
  .result-right {
    flex: 1;
  }

  .flower-name {
    font-size: 22px;
  }

  .flower-family {
    font-size: 14px;
  }

  .content-text {
    font-size: 14px;
  }

  .confidence-badge {
    padding: 8px 12px;
    font-size: 12px;
  }

  .badge-icon {
    font-size: 14px;
  }

  .preview-image,
  .result-image {
    max-height: 300px;
  }

  /* 按钮堆叠为全宽 */
  .action-buttons {
    flex-direction: column;
  }

  .btn-secondary,
  .btn-primary {
    width: 100%;
  }

  .result-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-qa {
    margin-left: 0;
    width: 100%;
  }
}

/* 小屏移动端 (≤480px) */
@media (max-width: 480px) {
  .card-title {
    font-size: 18px;
  }

  .upload-content {
    padding: 32px 16px;
  }

  .upload-icon {
    font-size: 32px;
  }

  .upload-text-primary {
    font-size: 15px;
  }

  .upload-text-secondary {
    font-size: 12px;
  }

  .flower-name {
    font-size: 20px;
  }

  .flower-family {
    font-size: 13px;
  }

  .content-text {
    font-size: 13px;
  }

  .preview-image,
  .result-image {
    max-height: 250px;
  }

  .btn-primary,
  .btn-secondary,
  .btn-qa {
    font-size: 16px;
    padding: 12px 24px;
  }
}
</style>
