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
          <el-icon size="16" color="#fff"><Connection /></el-icon>
        </div>
        <span style="font-weight:700;font-size:15px;color:#0f172a;letter-spacing:-.3px">
          心理健康问卷系统
        </span>
      </div>

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
            <el-dropdown-item command="profile">
              <el-icon><Setting /></el-icon> 个人设置
            </el-dropdown-item>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon> 退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </el-header>

    <el-container style="flex:1;overflow:hidden">

      <!-- 侧边栏 -->
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/user'

const route  = useRoute()
const router = useRouter()
const store  = useUserStore()

const navItems = [
  { path: '/user/dashboard', icon: 'HomeFilled', label: '首页' },
  { path: '/user/history',   icon: 'DataLine',   label: '历史记录' },
  { path: '/user/profile',   icon: 'User',        label: '个人信息' },
]

async function handleCmd(cmd) {
  if (cmd === 'logout') {
    await ElMessageBox.confirm('确认退出登录？', '提示', { type: 'warning' })
    store.logout()
    router.push('/login')
  } else if (cmd === 'profile') {
    router.push('/user/profile')
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
</style>
