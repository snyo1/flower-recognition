<script setup>
import {computed, reactive, ref} from "vue";
import {post} from "@/net/index";
import {ElMessage} from "element-plus";
import router from "@/router/index";

const form = reactive({
  password: "",
  password_repeat: "",
  email: '',
  code: ''
})

const active = ref(0)

//判断电子邮箱是否存在,邮箱通过才可获取验证码,获取验证码后一分钟后才能再次点击
const isEmailValid = ref(false)
const coldTime = ref(0);
const onValidate = (prop,isValid) =>{
  if(prop === 'email')
    isEmailValid.value = isValid
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
  email: [
    {required: true,message: '请输入电子邮件地址', trigger: ['blur']},
    {type: 'email', message: '请输入合法的电子邮件地址', trigger: ['blur', 'change']}
  ],
  code: [
    {required: true,message: '请输入获取的验证码', trigger: ['blur']}
  ],
  password: [
    { validator: validatePassword, trigger: ['blur', 'change'] }
  ],
  password_repeat: [
    { validator: validateConfirmPassword, trigger: ['blur', 'change'] }
  ]
}

//发送注册验证码请求
const validateEmail = () =>{
  coldTime.value = 60
  post('/api/auth/valid-reset-email',{
    email: form.email
  },(message) => {
    ElMessage.success(message)
    setInterval(()=>coldTime.value--, 1000)
  },(message)=>{
    ElMessage.warning(message)
    coldTime.value = 0
  })
}
const formRef = ref()
const startReset = ()=>{
  formRef.value.validate((isValid) => {
    if (isValid) {
      post('/api/auth/start-reset',{
        email: form.email,
        code: form.code
      },()=>{
        active.value++
      })
    }else {
      ElMessage.warning('请填写电子邮件地址和验证码')
    }
  })
}

const doReset = ()=>{
  formRef.value.validate((isValid) => {
    if (isValid) {
      post('/api/auth/do-reset',{
        email: form.email,
        code: form.code,
        password: form.password,
      },(message)=>{
        ElMessage.success(message)
        router.push('/')
      })
    }else {
      ElMessage.warning('请填写新的密码')
    }
  })
}
</script>

<template>
  <div>
    <div style="margin:30px 20px">
      <el-steps  align-center :active="active" finish-status="success">
        <el-step title="验证电子邮件" />
        <el-step title="重新设置密码" />
      </el-steps>
    </div>
    <transition  mode="out-in" name="el-fade-in-linear">
      <div style="text-align: center;margin: 0 40px;height: 100%" v-if="active === 0">
        <div style="margin-top: 100px">
          <div style="font-size: 25px ; font-weight: bold">重置密码</div>
          <div style="margin-top: 10px; font-size: 14px;color: gray">请输入需要重置密码的电子邮件地址</div>
        </div>
        <div style="margin-top: 50px">
          <el-form :model="form" :rules="rules" @validate="onValidate" ref="formRef">
            <el-form-item prop="email">
              <el-input prefix-icon="Message" v-model="form.email" type="email" placeholder="电子邮件地址"></el-input>
            </el-form-item>

            <el-form-item prop="code">
              <!-- 使用 flex 布局来对齐按钮 -->
              <div style="display: flex; gap: 10px; align-items: center">
                <div style="flex: 1">
                  <el-input prefix-icon="EditPen" v-model="form.code" :maxlength="6" type="text"
                            placeholder="请输入验证码" style="width: 100%"></el-input>
                </div>
                <div style="flex-shrink: 0">
                  <el-button @click="validateEmail" type="success" style="white-space: nowrap"
                             :disabled="!isEmailValid||coldTime>0">
                    {{coldTime > 0 ?'请稍等 '+coldTime+' 秒': '获取验证码'}}
                  </el-button>
                </div>
              </div>
            </el-form-item>
          </el-form>
        </div>
        <div style="margin-top: 120px">
          <el-button @click="startReset()" style="width: 200px;" type="danger" plain>开始重置密码</el-button>
        </div>
        <div style="margin-top: 20px">
          <el-link type="primary" style="translate: 0 -2px" @click="router.push('/')">返回登录</el-link>
        </div>
      </div>
    </transition>

    <transition  mode="out-in" name="el-fade-in-linear">
      <div style="text-align: center;margin: 0 40px;height: 100%" v-if="active === 1">
        <div style="margin-top: 100px">
          <div style="font-size: 25px ; font-weight: bold">重置密码</div>
          <div style="margin-top: 10px; font-size: 14px;color: gray">请填写您的新密码,务必牢记，防止丢失</div>
        </div>
        <div style="margin-top: 50px">
          <el-form :model="form" :rules="rules" @validate="onValidate" ref="formRef">
            <el-form-item prop="password">
              <!-- @focus/@blur事件：通过焦点事件控制强度提示的显示/隐藏 -->
              <el-input prefix-icon="Lock" v-model="form.password" :maxlength="16" type="password" placeholder="新密码"
                        @focus="showPasswordStrength = true" @blur="showPasswordStrength = false">
              </el-input>
              <!-- 密码强度提示（独立于验证） -->
              <!-- 使用v-if而非v-show，在隐藏时完全移出DOM，只有在输入框获得焦点且密码不为空时才显示提示 -->
              <div v-if="showPasswordStrength && form.password" style="margin-top: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span style="font-size: 12px; color: #666;">密码强度:</span>
                  <span
                      :style="{
                  color: passwordStrengthColors[currentPasswordStrength - 1] || '#666',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }">
                {{ passwordStrengthLabels[currentPasswordStrength - 1] || '未知' }}
              </span>
                </div>

                <!-- 进度条视觉反馈 -->
                <div style="margin-top: 4px;">
                  <!-- 隐藏文本显示(:show-text="false") -->
                  <el-progress
                      :percentage="(currentPasswordStrength / 5) * 100"
                      :show-text="false"
                      :color="passwordStrengthColors"
                      :stroke-width="4"
                  />
                </div>

                <!-- 具体改进建议 -->
                <div v-if="currentPasswordStrength < 3" style="margin-top: 4px; font-size: 11px; color: #999;">
                  <div>建议：包含大小写字母、数字或特殊字符</div>
                </div>
              </div>
            </el-form-item>
            <el-form-item prop="password_repeat">
              <el-input prefix-icon="Lock" v-model="form.password_repeat" :maxlength="16"
                        type="password" placeholder="确认新密码"></el-input>
            </el-form-item>
          </el-form>
        </div>
        <div style="margin-top: 120px">
          <el-button @click="doReset()" style="width: 200px;" type="danger" plain>立即重置密码</el-button>
        </div>
        <div style="margin-top: 20px">
          <el-link type="primary" style="translate: 0 -2px" @click="router.push('/')">返回登录</el-link>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>

</style>
