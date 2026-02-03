<script setup>
import router from "@/router";
import {reactive, ref, computed} from "vue";
import {ElMessage} from "element-plus";
import {post, get} from "@/net";

//定义表单
const form = reactive({
  username: "",
  password: "",
  password_repeat: "",
  email: "",
  code: ''
})

//用户名校验函数
const validateUsername = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入用户名'))
    return
  }
  if (!/^[\u4e00-\u9fa5a-zA-Z0-9_]+$/.test(value)) {
    callback(new Error('用户名不能包含特殊字符，仅支持中文、英文、数字、_'))
    return
  }
  const length = calculateStringLength(value)
  if (length < 3 || length > 12) {
    callback(new Error('用户名长度需在3-12个字符之间（中文算2个字符）'))
    return
  }
  get('api/auth/check-username?username=' + encodeURIComponent(value),
      () => {
        callback()
      },
      (message) => {
        callback(new Error(message || '此用户名已被他人注册'))
      })
}

// 计算字符长度（中文算2个，英文/数字算1个）
const calculateStringLength = (str) => {
  let length = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charAt(i)
    // 判断是否为中文
    if (/[\u4e00-\u9fa5]/.test(char)) {
      length += 2
    } else {
      length += 1
    }
  }
  return length
}

// 密码校验函数
const validatePassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'))
    return
  }
  if (/[\u4e00-\u9fa5]/.test(value)) {
    callback(new Error('密码不能包含中文'))
    return
  }
  if (value.length < 6 || value.length > 16) {
    callback(new Error('密码长度需在6-16个字符之间'))
    return
  }
  callback()
}

// 密码强度相关状态
const showPasswordStrength = ref(false)
const passwordStrengthLabels = ['非常弱', '弱', '一般', '强', '非常强']
const passwordStrengthColors = ['#ff4d4f', '#ff7a45', '#faad14', '#52c41a', '#389e0d']

// 密码强度计算（用于UI展示，不影响验证）
const calculatePasswordStrength = (password) => {
  if (!password || password.length === 0) return 0
  let strength = 0
  if (password.length >= 6) strength += 1
  if (/[a-z]/.test(password)) strength += 1
  if (/[A-Z]/.test(password)) strength += 1
  if (/[0-9]/.test(password)) strength += 1
  if (/[^a-zA-Z0-9]/.test(password)) strength += 1
  return Math.min(strength, 5)
}

// 实时计算密码强度
const currentPasswordStrength = computed(() => {
  return calculatePasswordStrength(form.password)
})

// 确认密码校验函数
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
    return
  }
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
    return
  }
  callback()
}

const rules = {
  username: [
    { validator: validateUsername, trigger: ['blur', 'change'] }
  ],
  password: [
    { validator: validatePassword, trigger: ['blur', 'change'] }
  ],
  password_repeat: [
    { validator: validateConfirmPassword, trigger: ['blur', 'change'] }
  ],
  email: [
    { required: true, message: '请输入电子邮件地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ]
}

const formRef = ref()
const isEmailValid = ref(false)
const coldTime = ref(0)

const onValidate = (prop, isValid) => {
  if (prop === 'email')
    isEmailValid.value = isValid
}

const validateEmail = () => {
  coldTime.value = 60
  post('api/auth/valid-register-email', {
    email: form.email
  }, (message) => {
    ElMessage.success(message)
    setInterval(() => coldTime.value--, 1000)
  }, (message) => {
    ElMessage.warning(message)
    coldTime.value = 0
  })
}

const register = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      post('api/auth/register', {
        username: form.username,
        password: form.password,
        email: form.email,
        code: form.code
      }, (message) => {
        ElMessage.success(message)
        router.push("/hua-shi-jie/")
      })
    } else {
      ElMessage.warning('请完整填写注册表单内容！')
    }
  })
}
</script>

<template>
  <div style="text-align: center;margin: 0 20px">
    <div style="margin-top: 100px">
      <div style="font-size: 25px;font-weight: bold">注册新用户</div>
      <div style="font-size: 14px;color: gray">欢迎注册我们的学习平台，请在下方填写相关信息</div>
    </div>
    <div style="margin-top: 50px">
      <el-form :model="form" :rules="rules" @validate="onValidate" ref="formRef">
        <el-form-item prop="username">
          <el-input v-model="form.username" prefix-icon="User" type="text" placeholder="用户名" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" prefix-icon="Lock" type="password" placeholder="密码"
            @focus="showPasswordStrength = true" @blur="showPasswordStrength = false" />
        </el-form-item>
        
        <!-- 密码强度显示条 -->
        <div v-if="showPasswordStrength" style="margin-bottom: 18px; text-align: left;">
          <div style="display: flex; gap: 4px; height: 4px; margin-bottom: 4px;">
            <div v-for="i in 5" :key="i" :style="{
              flex: 1,
              backgroundColor: i <= currentPasswordStrength ? passwordStrengthColors[currentPasswordStrength - 1] : '#ebeef5',
              borderRadius: '2px',
              transition: 'background-color 0.3s'
            }"></div>
          </div>
          <div style="font-size: 12px; color: #909399;">
            密码强度：<span :style="{ color: passwordStrengthColors[currentPasswordStrength - 1] }">
              {{ passwordStrengthLabels[currentPasswordStrength - 1] || '无' }}
            </span>
          </div>
        </div>

        <el-form-item prop="password_repeat">
          <el-input v-model="form.password_repeat" prefix-icon="Lock" type="password" placeholder="重复密码" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" prefix-icon="Message" type="email" placeholder="电子邮件地址" />
        </el-form-item>
        <el-form-item prop="code">
          <el-row :gutter="10" style="width: 100%">
            <el-col :span="17">
              <el-input v-model="form.code" prefix-icon="EditPen" type="text" placeholder="请输入验证码" />
            </el-col>
            <el-col :span="5">
              <el-button type="success" plain @click="validateEmail"
                :disabled="!isEmailValid || coldTime > 0">
                {{ coldTime > 0 ? '请稍后 ' + coldTime + '秒' : '获取验证码' }}
              </el-button>
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
    </div>
    <div style="margin-top: 80px">
      <el-button style="width: 180px" type="warning" plain @click="register">立即注册</el-button>
    </div>
    <div style="margin-top: 20px">
      <span style="font-size: 14px;line-height: 15px;color: gray">已有账号? </span>
      <el-link type="primary" style="translate: 0 -2px" @click="router.push('/')">立即登录</el-link>
    </div>
  </div>
</template>

<style scoped>
</style>
