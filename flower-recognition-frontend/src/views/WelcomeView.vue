<script setup>
import {ref, onMounted, onUnmounted} from 'vue'
import photo1 from '@/assets/image/1.jpg'
import photo2 from '@/assets/image/2.jpg'
import photo3 from '@/assets/image/3.jpg'
import photo4 from '@/assets/image/4.jpg'

// 定义图片数组
const images = ref([photo1, photo2, photo3, photo4])
const currentImageIndex = ref(Math.floor(Math.random() * images.value.length))
const showControls = ref(false) // 控制显示/隐藏
const isPlaying = ref(false) // 轮播状态，true表示正在播放,false表示暂停播放

let timer = null
let hideTimeout = null
let hoverTimer = null // 用于圆点悬停切换的定时器

// 切换到下一张图片
const nextImage = () => {
    currentImageIndex.value = (currentImageIndex.value + 1) % images.value.length
}

// 开始轮播
const startCarousel = () => {
  if (timer) clearInterval(timer)
  timer = setInterval(nextImage, 5000) //5s切换到下一张
  isPlaying.value = true
}

// 暂停轮播
const pauseCarousel = () => {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
  isPlaying.value = false
}

// 切换播放/暂停状态
const toggleCarousel = () => {
  if (isPlaying.value) {
    pauseCarousel()
  } else {
    startCarousel()
  }
}

// 跳转到指定图片
const goToImage = (index) => {
  currentImageIndex.value = index
}

// 鼠标悬停在圆点上时切换到对应图片
const onIndicatorHover = (index) => {
  // 清除之前的悬停定时器
  if (hoverTimer) {
    clearTimeout(hoverTimer)
    hoverTimer = null
  }

  // 立即切换到对应图片
  goToImage(index)

  // 可选：可以添加一个短暂延迟，避免快速划过时频繁切换
  // 这里为了更好的用户体验，选择立即切换
}

// 鼠标离开圆点时清理定时器
const onIndicatorLeave = () => {
  if (hoverTimer) {
    clearTimeout(hoverTimer)
    hoverTimer = null
  }
}

// 显示控制元素
const showCarouselControls = () => {
  showControls.value = true
  // 清除之前的隐藏定时器
  if (hideTimeout) {
    clearTimeout(hideTimeout)
    hideTimeout = null
  }
}

// 隐藏控制元素（0.5秒后）
const hideCarouselControls = () => {
  hideTimeout = setTimeout(() => {
    showControls.value = false
  }, 500)
}

// 鼠标进入控制区域
const onMouseEnterControls = () => {
  showCarouselControls()
}

// 鼠标离开控制区域
const onMouseLeaveControls = () => {
  hideCarouselControls()
}

// 生命周期钩子
onMounted(() => {
  hideCarouselControls()
})

onUnmounted(() => {
  pauseCarousel()
  if (hideTimeout) clearTimeout(hideTimeout)
  if (hoverTimer) clearTimeout(hoverTimer)
})
</script>

<template>
  <div class="login-container">
    <!-- 左侧图片轮播区域 -->
    <div class="left-section">
      <transition  mode="out-in" name="el-fade-in-linear">
        <el-image
            :key="currentImageIndex"
            class="background-image"
            fit="cover"
            :src="images[currentImageIndex]"
        />
      </transition>

      <!-- 左侧文字 -->
      <div class="welcome-title">
        <div class="title-main">欢迎来到花世界</div>
        <div class="title-sub">这是一个基于FastAPI+Vue3的花卉识别与科普平台</div>
        <div class="title-quote">——发现自然之美，探索植物奥秘</div>
      </div>

      <!-- 轮播控制区域（上方居中区域） -->
      <div
          class="controls-area"
          @mouseenter="onMouseEnterControls"
          @mouseleave="onMouseLeaveControls"
      >
        <!-- 轮播控制容器 -->
        <div class="carousel-controls" :class="{ show: showControls }">
          <!-- 轮播指示器（圆点） -->
          <div class="carousel-indicators">
            <div
                v-for="(image, index) in images"
                :key="index"
                class="indicator"
                :class="{ active: currentImageIndex === index }"
                @mouseenter="onIndicatorHover(index)"
                @mouseleave="onIndicatorLeave"
                @click="goToImage(index)"
            ></div>
          </div>

          <!-- 暂停/播放按钮 -->
          <div class="play-pause-control">
            <el-button @click="toggleCarousel" circle size="small" type="primary" plain class="control-btn">
              <el-icon>
                <component :is="isPlaying ? 'VideoPause' : 'VideoPlay'" />
              </el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧登录区域 -->
    <div class="right-section">
      <router-view v-slot="{ Component }">
        <transition mode="out-in" name="el-fade-in-linear">
          <component :is="Component"/>
        </transition>
      </router-view>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.left-section {
  background-color: antiquewhite;
  position: relative;
  overflow: hidden;
}

.background-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.right-section {
  background-color: white;
  height: 100vh;
  overflow-y: auto;
  position: relative;
  z-index: 10;
}

.welcome-title {
  position: absolute;
  bottom: 30px;
  left: 30px;
  color: white;
  text-shadow: 0 0 10px black;
  max-width: calc(100% - 400px - 60px);
  pointer-events: none;
  z-index: 2;
}

.title-main {
  font-size: 30px;
  font-weight: bold;
  line-height: 1.3;
}

.title-sub, .title-quote {
  margin-top: 10px;
  font-size: 16px;
  line-height: 1.4;
}

/* 轮播控制区域（透明区域，用于捕获鼠标事件） */
.controls-area {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 300px;
  height: 60px;
  z-index: 5;
  background-color: transparent; /* 完全透明 */
}

/* 轮播控制容器 */
.carousel-controls {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 8px 15px;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
  background-color: transparent !important; /* 完全透明背景 */
  box-shadow: none !important; /* 去除所有阴影 */
  border-radius: 0; /* 去除圆角 */
  z-index: 2;
}

.carousel-controls.show {
  opacity: 1;
  visibility: visible;
}

/* 轮播指示器样式 */
.carousel-indicators {
  display: flex;
  gap: 8px;
}

.indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator:hover {
  background-color: rgba(255, 255, 255, 0.9);
  transform: scale(1.1);
}

.indicator.active {
  background-color: rgba(255, 255, 255, 1);
  transform: scale(1.1);
}

/* 播放/暂停按钮样式 */
.play-pause-control {
  display: flex;
  align-items: center;
}

.control-btn {
  width: 32px !important;
  height: 32px !important;
  padding: 0 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  background-color: transparent !important;
  border-color: rgba(255, 255, 255, 0.6) !important;
}

.control-btn:hover {
  border-color: rgba(255, 255, 255, 0.9) !important;
  background-color: rgba(255, 255, 255, 0.1) !important;
}

.control-btn .el-icon {
  font-size: 16px !important;
  color: rgba(255, 255, 255, 0.8) !important;
}

.control-btn:hover .el-icon {
  color: rgba(255, 255, 255, 1) !important;
}

/* 响应式调整 */
@media (max-width: 1400px) {
  .title-main {
    font-size: 24px;
  }
  .title-sub, .title-quote {
    font-size: 14px;
  }
}

@media (max-width: 1100px) {
  .title-main {
    font-size: 20px;
  }
  .title-sub, .title-quote {
    font-size: 12px;
  }
  .controls-area {
    width: 250px;
    height: 50px;
  }
  .carousel-controls {
    top: 15px;
    gap: 12px;
  }
  .indicator {
    width: 8px;
    height: 8px;
  }
  .control-btn {
    width: 28px !important;
    height: 28px !important;
  }
}

@media (max-width: 900px) {
  .welcome-title {
    display: none;
  }
  .login-container {
    grid-template-columns: 1fr;
  }
  .right-section {
    width: 100%;
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
  }
}
</style>
