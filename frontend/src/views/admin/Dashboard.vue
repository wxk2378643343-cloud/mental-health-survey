<template>
  <div v-loading="loading">
    <div class="page-title">数据概览</div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :xs="12" :md="6" v-for="item in statCards" :key="item.label" style="margin-bottom:16px">
        <el-card>
          <div class="stat-card">
            <div class="stat-icon-box" :style="{ background: item.bg }">
              <el-icon size="20" :color="item.color"><component :is="item.icon" /></el-icon>
            </div>
            <div class="stat-body">
              <div class="stat-num" :style="{ color: item.color }">{{ item.value }}</div>
              <div class="stat-lbl">{{ item.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- 趋势折线 -->
      <el-col :xs="24" :md="14" style="margin-bottom:16px">
        <el-card>
          <template #header>近 7 天测评趋势</template>
          <v-chart class="chart-container" :option="trendOption" autoresize />
        </el-card>
      </el-col>

      <!-- 等级饼图 -->
      <el-col :xs="24" :md="10" style="margin-bottom:16px">
        <el-card>
          <template #header>结果等级分布</template>
          <v-chart class="chart-container" :option="pieOption" autoresize />
        </el-card>
      </el-col>

      <!-- 量表柱图 -->
      <el-col :span="24">
        <el-card>
          <template #header>各量表测评次数</template>
          <v-chart class="chart-container" :option="barOption" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'

const loading = ref(true)
const stats   = ref({})

const statCards = computed(() => [
  { label: '注册用户',  value: stats.value.total_users   ?? 0,
    color: '#4f6ef7', bg: '#eef2ff', icon: 'UserFilled' },
  { label: '总测评次数', value: stats.value.total_results ?? 0,
    color: '#0ea96a', bg: '#ecfdf5', icon: 'Document' },
  { label: '高风险记录', value: stats.value.risk_count    ?? 0,
    color: '#ef4444', bg: '#fef2f2', icon: 'Warning' },
  { label: '未读预警',  value: stats.value.unread_alerts  ?? 0,
    color: '#f59e0b', bg: '#fffbeb', icon: 'Bell' },
])

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#e2e8f0',
             textStyle: { color: '#334155', fontSize: 12 } },
  xAxis: { type: 'category', data: (stats.value.trend || []).map(t => t.date.slice(5)),
           axisLine: { lineStyle: { color: '#e2e8f0' } },
           axisLabel: { color: '#94a3b8', fontSize: 12 } },
  yAxis: { type: 'value', minInterval: 1,
           splitLine: { lineStyle: { color: '#f1f5f9' } },
           axisLabel: { color: '#94a3b8', fontSize: 12 } },
  series: [{
    data: (stats.value.trend || []).map(t => t.count),
    type: 'line', smooth: true,
    lineStyle: { color: '#4f6ef7', width: 2 },
    itemStyle: { color: '#4f6ef7' },
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                  colorStops: [{ offset: 0, color: 'rgba(79,110,247,.2)' },
                               { offset: 1, color: 'rgba(79,110,247,0)' }] } },
    symbol: 'circle', symbolSize: 6,
  }],
  grid: { top: 16, bottom: 28, left: 36, right: 16 }
}))

const levelColors = {
  '正常': '#10b981','无抑郁': '#10b981','无焦虑': '#10b981',
  '轻度抑郁': '#f59e0b','轻度焦虑': '#f59e0b',
  '中度抑郁': '#f97316','中度焦虑': '#f97316',
  '重度抑郁': '#ef4444','重度焦虑': '#ef4444','中重度抑郁': '#ef4444',
}
const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}：{c} 次 ({d}%)',
             backgroundColor: '#fff', borderColor: '#e2e8f0',
             textStyle: { color: '#334155', fontSize: 12 } },
  legend: { bottom: 0, textStyle: { color: '#64748b', fontSize: 12 } },
  series: [{
    type: 'pie', radius: ['38%', '62%'], center: ['50%', '45%'],
    data: (stats.value.by_level || []).map(l => ({
      name: l.label, value: l.count,
      itemStyle: { color: levelColors[l.label] || '#94a3b8' }
    })),
    label: { show: false },
    emphasis: { label: { show: true, fontSize: 13, fontWeight: '700' } }
  }]
}))

const barOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#e2e8f0',
             textStyle: { color: '#334155', fontSize: 12 } },
  xAxis: { type: 'category', data: (stats.value.by_questionnaire || []).map(q => q.name),
           axisLabel: { color: '#64748b', fontSize: 12 } },
  yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#f1f5f9' } },
           axisLabel: { color: '#94a3b8', fontSize: 12 } },
  series: [{
    type: 'bar', barMaxWidth: 52,
    data: (stats.value.by_questionnaire || []).map((q, i) => ({
      value: q.count,
      itemStyle: { color: ['#4f6ef7','#10b981','#f59e0b','#ef4444'][i % 4],
                   borderRadius: [5, 5, 0, 0] }
    })),
    label: { show: true, position: 'top', color: '#64748b', fontSize: 12 }
  }],
  grid: { top: 28, bottom: 36, left: 40, right: 16 }
}))

onMounted(async () => {
  try {
    const res = await adminApi.stats()
    if (res.code === 200) stats.value = res.data
  } finally {
    loading.value = false
  }
})
</script>
