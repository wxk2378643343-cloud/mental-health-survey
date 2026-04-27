<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <el-icon size="48" color="#667eea"><UserFilled /></el-icon>
        <h2>创建账号</h2>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名（3-20位）" size="large" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码（至少6位）"
                    size="large" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item prop="gender">
              <el-select v-model="form.gender" placeholder="性别" size="large" style="width:100%">
                <el-option label="男" value="male" />
                <el-option label="女" value="female" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="age">
              <el-input-number v-model="form.age" :min="10" :max="100" placeholder="年龄"
                               size="large" style="width:100%" controls-position="right" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱（可选）" size="large" :prefix-icon="Message" />
        </el-form-item>
        <el-button type="success" size="large" style="width:100%" :loading="loading" @click="doRegister">
          注 册
        </el-button>
        <div style="text-align:center;margin-top:12px">
          <el-link @click="$router.push('/login')">已有账号？去登录</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { authApi } from '@/api'
import { useUserStore } from '@/store/user'

const router  = useRouter()
const store   = useUserStore()
const loading = ref(false)
const formRef = ref()

const form = reactive({
  username: '', password: '', gender: 'other', age: null, email: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度 3-20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
}

async function doRegister() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await authApi.register(form)
    if (res.code === 200) {
      store.setAuth(res.token, res.user)
      ElMessage.success('注册成功，欢迎！')
      router.push('/user/dashboard')
    } else {
      ElMessage.error(res.msg)
    }
  } finally {
    loading.value = false
  }
}
</script>
