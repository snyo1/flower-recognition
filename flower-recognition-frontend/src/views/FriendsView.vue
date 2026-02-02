<template>
  <div class="friends-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">好友</span>
          <el-input v-model="keyword" placeholder="搜索用户名或邮箱" style="width:300px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-button type="primary" @click="doSearch">搜索</el-button>
        </div>
      </template>
      <div class="results">
        <el-table :data="results" style="width: 100%">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column label="操作">
            <template #default="scope">
              <el-button size="small" @click="sendRequest(scope.row.id)">添加好友</el-button>
              <el-button size="small" type="primary" @click="viewInfo(scope.row.id)">查看信息</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-divider>我的好友</el-divider>
      <el-table :data="friends" style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" type="primary" @click="viewInfo(scope.row.user_id)">查看信息</el-button>
            <el-button size="small" type="danger" @click="removeFriend(scope.row.user_id)">删除好友</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="infoVisible" title="好友信息" width="500px">
      <div v-if="friendInfo">
        <p>用户名：{{ friendInfo.username }}</p>
        <p v-if="friendInfo.email">邮箱：{{ friendInfo.email }}</p>
        <p v-if="friendInfo.recognitionCount !== null">识别次数：{{ friendInfo.recognitionCount }}</p>
        <p v-if="friendInfo.favoritesCount !== null">收藏数：{{ friendInfo.favoritesCount }}</p>
        <p v-if="friendInfo.qaCount !== null">问答次数：{{ friendInfo.qaCount }}</p>
      </div>
      <template #footer>
        <el-button @click="infoVisible=false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const keyword = ref('')
const results = ref<any[]>([])
const friends = ref<any[]>([])
const infoVisible = ref(false)
const friendInfo = ref<any>(null)

const tokenHeader = () => {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const doSearch = () => {
  axios.get(`/api/friends/search?q=${encodeURIComponent(keyword.value)}`).then(({data}) => {
    results.value = data
  })
}

const loadFriends = () => {
  axios.get('/api/friends/list', { headers: tokenHeader() }).then(({data}) => {
    friends.value = data
  })
}

const sendRequest = (targetId: number) => {
  axios.post(`/api/friends/request/${targetId}`, {}, { headers: tokenHeader() }).then(() => {
    ElMessage.success('好友请求已发送')
  }).catch(err => {
    ElMessage.error(err?.response?.data?.detail || '发送失败')
  })
}

const viewInfo = (userId: number) => {
  axios.get(`/api/friends/info/${userId}`, { headers: tokenHeader() }).then(({data}) => {
    friendInfo.value = data
    infoVisible.value = true
  }).catch(err => {
    ElMessage.error(err?.response?.data?.detail || '查看失败')
  })
}

const removeFriend = (userId: number) => {
  axios.delete(`/api/friends/remove/${userId}`, { headers: tokenHeader() }).then(() => {
    ElMessage.success('好友已删除')
    loadFriends()
  }).catch(err => {
    ElMessage.error(err?.response?.data?.detail || '删除失败')
  })
}

onMounted(() => {
  loadFriends()
})
</script>

<style scoped>
.friends-page {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}
.card-header {
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>
