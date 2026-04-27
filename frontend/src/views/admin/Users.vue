<template>
  <div>
    <div class="page-title">用户管理</div>

    <el-card>
      <template #header>
        <div style="display:flex;align-items:center;gap:12px">
          <el-input v-model="keyword" placeholder="搜索用户名" clearable style="width:220px"
                    :prefix-icon="Search" @keyup.enter="loadUsers(1)" />
          <el-button type="primary" :icon="Search" @click="loadUsers(1)">搜索</el-button>
        </div>
      </template>

      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="150" show-overflow-tooltip />
        <el-table-column label="性别" width="70">
          <template #default="{ row }">
            {{ { male: '男', female: '女', other: '其他' }[row.gender] || '—' }}
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="70" />
        <el-table-column label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '正常' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="170" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.role !== 'admin'"
                       :type="row.is_active ? 'warning' : 'success'"
                       size="small" link @click="toggleUser(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-text v-else type="info" size="small">—</el-text>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination style="margin-top:16px;justify-content:flex-end;display:flex"
                     v-model:current-page="page" :page-size="20" :total="total"
                     layout="total, prev, pager, next" @current-change="loadUsers" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

const loading = ref(false)
const users   = ref([])
const total   = ref(0)
const page    = ref(1)
const keyword = ref('')

async function loadUsers(p = 1) {
  page.value = p
  loading.value = true
  try {
    const res = await adminApi.users(p, keyword.value)
    if (res.code === 200) { users.value = res.data; total.value = res.total }
  } finally {
    loading.value = false
  }
}

async function toggleUser(row) {
  await ElMessageBox.confirm(
    `确认${row.is_active ? '禁用' : '启用'}用户 "${row.username}"？`, '确认', { type: 'warning' }
  )
  const res = await adminApi.toggleUser(row.id)
  if (res.code === 200) {
    row.is_active = res.is_active
    ElMessage.success('操作成功')
  }
}

onMounted(() => loadUsers())
</script>
