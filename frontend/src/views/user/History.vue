<template>
  <div>
    <div class="page-title">历史测评记录</div>

    <!-- 趋势图 -->
    <el-card style="margin-bottom:20px">
      <template #header>
        <span><el-icon><TrendCharts /></el-icon> 历史得分趋势</span>
      </template>
      <el-empty v-if="!chartReady" description="暂无足够数据生成趋势图" />
      <v-chart v-else class="chart-container" :option="chartOption" autoresize />
    </el-card>

    <!-- 筛选 + 列表 -->
    <el-card>
      <template #header>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
          <span><el-icon><List /></el-icon> 测评记录</span>
          <el-select v-model="filterCode" placeholder="按量表筛选" clearable size="small" style="width:160px">
            <el-option v-for="c in codes" :key="c" :label="c" :value="c" />
          </el-select>
        </div>
      </template>

      <el-empty v-if="!filteredResults.length" description="暂无测评记录" />
      <el-table v-else :data="filteredResults" stripe>
        <el-table-column prop="questionnaire_name" label="量表名称" min-width="160" />
        <el-table-column label="得分" width="90">
          <template #default="{ row }">
            <span style="font-weight:700;color:#1677ff;font-size:15px">
              {{ row.std_score ?? row.raw_score }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="等级" width="110">
          <template #default="{ row }">
            <span class="level-badge" :class="'level-' + row.level">{{ row.level_label }}</span>
          </template>
        </el-table-column>
        <el-table-column label="风险" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.risk_flag" type="danger" size="small">预警</el-tag>
            <el-text v-else type="success" size="small">正常</el-text>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="测评时间" width="170" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-link type="primary" @click="$router.push('/user/result/' + row.id)">详情</el-link>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { surveyApi } from '@/api'

const loading     = ref(true)
const results     = ref([])
const statsData   = ref({})
const filterCode  = ref('')

const codes = computed(() => [...new Set(results.value.map(r => r.questionnaire_code))])

const filteredResults = computed(() =>
  filterCode.value
    ? results.value.filter(r => r.questionnaire_code === filterCode.value)
    : results.value
)

// ECharts 折线图：各量表历史得分趋势
const chartReady = computed(() => Object.keys(statsData.value).length > 0)

const colorMap = { PHQ9: '#1677ff', GAD7: '#52c41a', SDS: '#faad14', SAS: '#ff4d4f' }

const chartOption = computed(() => {
  const series = Object.entries(statsData.value).map(([code, info]) => ({
    name: info.name,
    type: 'line',
    smooth: true,
    data: info.history.map(h => [h.date, h.score]),
    itemStyle: { color: colorMap[code] || '#666' },
    markPoint: {
      data: [{ type: 'max', name: '最高' }, { type: 'min', name: '最低' }]
    }
  }))
  return {
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    xAxis: { type: 'time', boundaryGap: false },
    yAxis: { type: 'value', name: '得分', min: 0 },
    series,
    grid: { top: 40, bottom: 30, left: 50, right: 20 }
  }
})

onMounted(async () => {
  try {
    const [rRes, sRes] = await Promise.all([surveyApi.myResults(), surveyApi.myStats()])
    if (rRes.code === 200) results.value = rRes.data
    if (sRes.code === 200) statsData.value = sRes.data
  } finally {
    loading.value = false
  }
})
</script>
