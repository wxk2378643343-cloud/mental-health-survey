<template>
  <el-container style="height:100vh;overflow:hidden;flex-direction:column">

    <!-- 顶栏 -->
    <el-header height="56px" style="
      background:#fff;
      border-bottom:1px solid #e2e8f0;
      display:flex;align-items:center;justify-content:space-between;
      padding:0 24px;flex-shrink:0;z-index:100;
    ">
      <div style="display:flex;align-items:center;gap:10px">
        <div style="
          width:30px;height:30px;border-radius:8px;
          background:linear-gradient(135deg,#4f6ef7,#818cf8);
          display:flex;align-items:center;justify-content:center;
        ">
          <el-icon size="16" color="#fff"><Monitor /></el-icon>
        </div>
        <span style="font-weight:700;font-size:15px;color:#0f172a;letter-spacing:-.3px">
          心理健康管理平台
        </span>
      </div>

      <div style="display:flex;align-items:center;gap:20px">
        <!-- 铃铛（使用 store.unreadAlerts 实时同步） -->
        <div style="position:relative;cursor:pointer" @click="router.push('/admin/alerts')">
          <el-icon size="18" color="#64748b"><Bell /></el-icon>
          <span v-if="store.unreadAlerts" style="
            position:absolute;top:-4px;right:-5px;
            background:#ef4444;color:#fff;
            border-radius:10px;padding:0 4px;
            font-size:10px;line-height:16px;height:16px;
            display:inline-flex;align-items:center;font-weight:700;
          ">{{ store.unreadAlerts > 99 ? '99+' : store.unreadAlerts }}</span>
        </div>

        <!-- 用户 -->
        <el-dropdown @command="handleCmd">
          <div style="display:flex;align-items:center;gap:8px;cursor:pointer">
            <div style="
              width:30px;height:30px;border-radius:50%;
              background:linear-gradient(135deg,#4f6ef7,#818cf8);
              display:flex;align-items:center;justify-content:center;
              color:#fff;font-size:13px;font-weight:700;
            ">{{ store.user?.username?.[0]?.toUpperCase() }}</div>
            <span style="font-size:13px;color:#334155;font-weight:500">{{ store.user?.username }}</span>
            <el-icon size="12" color="#94a3b8"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="user">
                <el-icon><User /></el-icon> 切换用户视图
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon> 退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <el-container style="flex:1;overflow:hidden">

      <!-- 侧边栏（badge 直接绑定 store.unreadAlerts） -->
      <el-aside width="200px" style="
        background:#fff;
        border-right:1px solid #e2e8f0;
        height:100%;overflow-y:auto;flex-shrink:0;
        padding:12px 10px;
      ">
        <nav>
          <router-link
            v-for="item in navItems" :key="item.path"
            :to="item.path" custom v-slot="{ isActive, navigate }"
          >
            <div @click="navigate" :class="['nav-item', isActive && 'nav-item--active']">
              <el-icon size="16"><component :is="item.icon" /></el-icon>
              <span>{{ item.label }}</span>
              <span v-if="item.showBadge && store.unreadAlerts" class="nav-badge">
                {{ store.unreadAlerts > 99 ? '99+' : store.unreadAlerts }}
              </span>
            </div>
          </router-link>
        </nav>
      </el-aside>

      <!-- 内容 -->
      <el-main style="background:#f8fafc;padding:28px;overflow-y:auto;height:100%">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'

const route  = useRoute()
const router = useRouter()
const store  = useUserStore()

const navItems = [
  { path: '/admin/dashboard',      icon: 'DataAnalysis', label: '数据概览' },
  { path: '/admin/users',          icon: 'UserFilled',   label: '用户管理' },
  { path: '/admin/results',        icon: 'List',         label: '测评记录' },
  { path: '/admin/questionnaires', icon: 'Document',     label: '问卷管理' },
  { path: '/admin/alerts',         icon: 'Warning',      label: '风险预警', showBadge: true },
]

// 进入管理端时立即拉一次，之后每 30s 自动刷新
store.fetchUnread()
const timer = setInterval(() => store.fetchUnread(), 30000)
onUnmounted(() => clearInterval(timer))

async function handleCmd(cmd) {
  if (cmd === 'logout') {
    await ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning' })
    store.logout()
    router.push('/login')
  } else if (cmd === 'user') {
    router.push('/user/dashboard')
  }
}
</script>

<style scoped>
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 2px;
  transition: background .15s, color .15s;
  user-select: none;
}
.nav-item:hover { background: #f1f5f9; color: #0f172a; }
.nav-item--active { background: #eef2ff; color: #4f6ef7; font-weight: 600; }

.nav-badge {
  margin-left: auto;
  background: #ef4444;
  color: #fff;
  border-radius: 10px;
  padding: 0 6px;
  font-size: 11px;
  line-height: 18px;
  height: 18px;
  display: inline-flex;
  align-items: center;
  font-weight: 700;
}
</style>
