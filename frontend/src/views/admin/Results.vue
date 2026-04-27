<template>
  <div>
    <div class="page-title">测评记录</div>

    <el-card>
      <template #header>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
          <el-select v-model="filterCode" placeholder="量表筛选" clearable style="width:140px"
                     @change="loadResults(1)">
            <el-option v-for="c in ['PHQ9','GAD7','SDS','SAS']" :key="c" :label="c" :value="c" />
          </el-select>
          <el-select v-model="filterRisk" placeholder="风险筛选" clearable style="width:130px"
                     @change="loadResults(1)">
            <el-option label="全部" value="" />
            <el-option label="高风险" value="1" />
            <el-option label="正常" value="0" />
          </el-select>
          <el-button type="primary" @click="loadResults(1)">查询</el-button>
        </div>
      </template>

      <el-table :data="results" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="questionnaire_name" label="量表" min-width="140" show-overflow-tooltip />
        <el-table-column label="得分" width="80">
          <template #default="{ row }">
            <span style="font-weight:700;color:#1677ff">{{ row.std_score ?? row.raw_score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="等级" width="110">
          <template #default="{ row }">
            <span class="level-badge" :class="'level-' + row.level">{{ row.level_label }}</span>
          </template>
        </el-table-column>
        <el-table-column label="风险" width="80" align="center">
          <template #default="{ row }">
            <span v-if="row.risk_flag" class="risk-tag">高风险</span>
            <el-text v-else type="success" size="small">正常</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="测评时间" width="170" />
      </el-table>

      <el-pagination style="margin-top:16px;justify-content:flex-end;display:flex"
                     v-model:current-page="page" :page-size="20" :total="total"
                     layout="total, prev, pager, next" @current-change="loadResults" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'

const loading    = ref(false)
const results    = ref([])
const total      = ref(0)
const page       = ref(1)
const filterCode = ref('')
const filterRisk = ref('')

async function loadResults(p = 1) {
  page.value = p
  loading.value = true
  try {
    const res = await adminApi.results(p, filterRisk.value, filterCode.value)
    if (res.code === 200) { results.value = res.data; total.value = res.total }
  } finally {
    loading.value = false
  }
}

onMounted(() => loadResults())
</script>
