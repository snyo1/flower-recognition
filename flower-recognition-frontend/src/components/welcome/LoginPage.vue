<script setup>
import {reactive} from "vue";
import {ElMessage} from "element-plus";
import {get, post} from "@/net";
import router from "@/router";
import {useStore} from "@/stores";

const store = useStore()

const form = reactive({
  username: "",
  password: "",
  remember: false,
})

const login = () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码！')
  } else {
    post('/api/auth/login',{
      username: form.username,
      password: form.password,
      remember: form.remember,
    },(message)=>{
      ElMessage.success(message)
      get('api/user/me',(message)=>{
        store.auth.user = message
        router.push('/index')
      },()=>{
        store.auth.user = null
      })
    })
  }
}

</script>

<template>
  <div style="text-align: center;margin: 0 40px">
    <div style="margin-top: 150px">
      <div style="font-size: 25px ; font-weight: bold">登录</div>
      <div style="margin-top: 10px; font-size: 14px;color: gray">在进入系统之前请先输入用户名和密码进行登录</div>
    </div>

    <div style="margin-top: 50px">
      <el-input v-model="form.username" prefix-icon="User" type="text" placeholder="用户名/邮箱"></el-input>
      <el-input v-model="form.password" style="margin-top: 10px" prefix-icon="Lock" type="password" placeholder="密码"></el-input>
    </div>

    <el-row style="margin-top: 5px">
      <el-col :span="12" style="text-align: left">
        <el-checkbox v-model="form.remember" label="记住我" size="large" />
      </el-col>

      <el-col :span="12" style="text-align: right">
        <el-link @click="router.push('/forget')">忘记密码？</el-link>
      </el-col>
    </el-row>

    <div style="margin-top: 50px">
      <el-button @click="login()" style="width: 200px" type="success" plain>立即登录</el-button>
    </div>
    <el-divider>
      <span style="color: gray;font-size: 13px;background-color: antiquewhite;padding: 0">没有账号</span>
    </el-divider>
    <div>
      <el-button style="width: 200px" @click="router.push('/register')" type="warning" plain>注册账号</el-button>
    </div>
  </div>
</template>

<style scoped>
/* 覆盖 el-divider 文字部分的样式 */
:deep(.el-divider__text) {
  padding: 10px !important;
  background-color: antiquewhite !important;
}
</style>
