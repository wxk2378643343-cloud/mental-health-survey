<template>
  <div>
    <div class="page-title-bar">
      <h2>风险预警</h2>
      <el-button type="primary" size="small" :disabled="!store.unreadAlerts" @click="markAll">
        全部标为已读
      </el-button>
    </div>

    <el-card>
      <template #header>
        <div style="display:flex;align-items:center;gap:16px">
          <el-checkbox v-model="onlyUnread" @change="loadAlerts(1)">仅显示未读</el-checkbox>
          <span v-if="store.unreadAlerts" style="
            background:#fef2f2;color:#dc2626;
            border-radius:6px;padding:2px 10px;
            font-size:12px;font-weight:600;
          ">{{ store.unreadAlerts }} 条未读</span>
          <span v-else style="font-size:12px;color:#94a3b8">暂无未读预警</span>
        </div>
      </template>

      <div v-loading="loading" style="min-height:80px">
        <el-empty v-if="!loading && !alerts.length" description="暂无风险预警记录" :image-size="80" />

        <div v-for="alert in alerts" :key="alert.id" class="alert-row"
             :class="{ unread: !alert.is_read }">
          <div class="alert-left">
            <div class="alert-header">
              <span class="alert-dot" :class="{ read: alert.is_read }" />
              <span class="alert-user">{{ alert.username }}</span>
              <span class="risk-tag">高风险</span>
              <el-tag v-if="!alert.is_read" type="danger" size="small" effect="plain">未读</el-tag>
            </div>
            <div class="alert-msg">{{ alert.message }}</div>
            <div class="alert-time">{{ alert.created_at }}</div>
          </div>

          <!-- 已读：显示"标记未读"；未读：显示"标为已读" -->
          <div style="display:flex;flex-direction:column;gap:6px;flex-shrink:0">
            <el-button v-if="!alert.is_read" size="small" plain @click="markRead(alert)">
              标为已读
            </el-button>
            <el-button v-else size="small" plain type="warning" @click="markUnread(alert)">
              标记未读
            </el-button>
          </div>
        </div>
      </div>

      <el-pagination v-if="total > 0"
                     style="margin-top:16px;justify-content:flex-end;display:flex"
                     v-model:current-page="page" :page-size="20" :total="total"
                     layout="total, prev, pager, next" @current-change="loadAlerts" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api'
import { useUserStore } from '@/store/user'

const store      = useUserStore()
const loading    = ref(false)
const alerts     = ref([])
const total      = ref(0)
const page       = ref(1)
const onlyUnread = ref(false)

async function loadAlerts(p = 1) {
  page.value = p
  loading.value = true
  try {
    const res = await adminApi.alerts(p, onlyUnread.value ? 1 : '')
    if (res.code === 200) { alerts.value = res.data; total.value = res.total }
    // 同步 store（侧边栏 & 铃铛同步更新）
    await store.fetchUnread()
  } finally {
    loading.value = false
  }
}

async function markRead(alert) {
  const res = await adminApi.markRead(alert.id)
  if (res.code !== 200) return
  alert.is_read = true
  store.unreadAlerts = Math.max(0, store.unreadAlerts - 1)
  if (onlyUnread.value) {
    alerts.value = alerts.value.filter(a => a.id !== alert.id)
    total.value  = Math.max(0, total.value - 1)
  }
}

async function markUnread(alert) {
  const res = await adminApi.markUnread(alert.id)
  if (res.code !== 200) return
  alert.is_read = false
  store.unreadAlerts += 1
  // 若在"仅未读"模式，该条已经在列表里，不需要额外操作
}

async function markAll() {
  const res = await adminApi.markAllRead()
  if (res.code === 200) {
    ElMessage.success('已全部标为已读')
    alerts.value.forEach(a => (a.is_read = true))
    store.unreadAlerts = 0
    if (onlyUnread.value) { alerts.value = []; total.value = 0 }
  }
}

onMounted(() => loadAlerts())
</script>

<style scoped>
.alert-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 16px;
  border-radius: 10px;
  margin-bottom: 8px;
  border: 1px solid #e2e8f0;
  background: #fafafa;
  transition: background .15s;
}
.alert-row.unread { background: #fffbeb; border-color: #fde68a; }
.alert-left { flex: 1; min-width: 0; }
.alert-header {
  display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
}
.alert-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #ef4444; flex-shrink: 0;
}
.alert-dot.read { background: #cbd5e1; }
.alert-user { font-weight: 600; color: #0f172a; font-size: 13px; }
.alert-msg  { color: #475569; font-size: 13px; line-height: 1.6; }
.alert-time { color: #94a3b8; font-size: 12px; margin-top: 4px; }
</style>
