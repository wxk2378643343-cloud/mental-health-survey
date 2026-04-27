<template>
  <div class="login-page">

    <!-- 左侧品牌区 -->
    <div class="login-left">
      <div class="brand">
        <div class="brand-logo">
          <el-icon size="28" color="#fff"><Connection /></el-icon>
        </div>
        <span class="brand-name">MindSurvey</span>
      </div>

      <div class="hero">
        <h1 class="hero-title">关注心理健康<br />从一次自测开始</h1>
        <p class="hero-sub">科学量表 · 即时评分 · 专业解读</p>
      </div>

      <ul class="feature-list">
        <li v-for="f in features" :key="f.text">
          <span class="feat-icon">{{ f.icon }}</span>
          <span>{{ f.text }}</span>
        </li>
      </ul>

      <div class="left-footer">PHQ-9 · GAD-7 · SDS · SAS 标准量表</div>
    </div>

    <!-- 右侧表单区 -->
    <div class="login-right">
      <div class="form-wrap">
        <div style="margin-bottom:28px">
          <h2 class="form-title">欢迎回来</h2>
          <p class="form-sub">登录以继续使用心理健康问卷系统</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" size="large">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User"
                      autocomplete="username" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码"
                      :prefix-icon="Lock" show-password
                      autocomplete="current-password"
                      @keyup.enter="doLogin" />
          </el-form-item>

          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
            <el-checkbox v-model="remember" label="记住密码" />
            <el-text type="info" size="small">演示：admin / admin123</el-text>
          </div>

          <el-button type="primary" size="large" style="width:100%;font-size:15px;font-weight:600"
                     :loading="loading" @click="doLogin">
            登 录
          </el-button>
        </el-form>

        <el-divider>
          <span style="color:#94a3b8;font-size:12px">还没有账号？</span>
        </el-divider>

        <el-button size="large" style="width:100%" @click="$router.push('/register')">
          立即注册
        </el-button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { authApi } from '@/api'
import { useUserStore } from '@/store/user'

const STORAGE_KEY = 'mh_remember'

const router   = useRouter()
const store    = useUserStore()
const loading  = ref(false)
const remember = ref(false)
const formRef  = ref()

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码',   trigger: 'blur' }],
}

const features = [
  { icon: '🧠', text: '专业心理健康评估量表' },
  { icon: '📊', text: '即时自动评分与结果解读' },
  { icon: '📈', text: '历史趋势追踪与可视化' },
  { icon: '🔒', text: '数据安全，隐私保护' },
]

// 读取记住的账号密码
onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null')
    if (saved?.username) {
      form.username = saved.username
      form.password = saved.password
      remember.value = true
    }
  } catch {}
})

async function doLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await authApi.login(form)
    if (res.code === 200) {
      // 记住密码
      if (remember.value) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          username: form.username,
          password: form.password,
        }))
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }
      store.setAuth(res.token, res.user)
      ElMessage.success('登录成功')
      router.push(res.user.role === 'admin' ? '/admin/dashboard' : '/user/dashboard')
    } else {
      ElMessage.error(res.msg)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
}

/* ── 左侧 ── */
.login-left {
  width: 45%;
  background: linear-gradient(160deg, #1e2a5e 0%, #4f6ef7 55%, #818cf8 100%);
  display: flex;
  flex-direction: column;
  padding: 40px 48px;
  position: relative;
  overflow: hidden;
}
.login-left::before {
  content: '';
  position: absolute;
  width: 400px; height: 400px;
  border-radius: 50%;
  background: rgba(255,255,255,.04);
  top: -100px; right: -100px;
}
.login-left::after {
  content: '';
  position: absolute;
  width: 300px; height: 300px;
  border-radius: 50%;
  background: rgba(255,255,255,.05);
  bottom: -60px; left: -60px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 1;
}
.brand-logo {
  width: 40px; height: 40px;
  background: rgba(255,255,255,.15);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px);
}
.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  letter-spacing: .5px;
}

.hero { margin-top: auto; z-index: 1; }
.hero-title {
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.3;
  margin: 0 0 12px;
  letter-spacing: -.5px;
}
.hero-sub {
  color: rgba(255,255,255,.65);
  font-size: 14px;
  margin: 0 0 36px;
  letter-spacing: 2px;
}

.feature-list {
  list-style: none;
  padding: 0; margin: 0 0 auto;
  z-index: 1;
}
.feature-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(255,255,255,.8);
  font-size: 13px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.feature-list li:last-child { border-bottom: none; }
.feat-icon { font-size: 16px; }

.left-footer {
  color: rgba(255,255,255,.35);
  font-size: 11px;
  margin-top: 32px;
  z-index: 1;
  letter-spacing: 1px;
}

/* ── 右侧 ── */
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  padding: 40px 24px;
}
.form-wrap {
  width: 100%;
  max-width: 380px;
}
.form-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 6px;
  letter-spacing: -.5px;
}
.form-sub {
  color: #64748b;
  font-size: 13px;
  margin: 0;
}

/* 响应式：小屏隐藏左侧 */
@media (max-width: 768px) {
  .login-left { display: none; }
  .login-right { background: linear-gradient(160deg, #1e2a5e 0%, #4f6ef7 55%, #818cf8 100%); }
  .form-wrap {
    background: #fff;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 20px 60px rgba(0,0,0,.2);
  }
}
</style>
