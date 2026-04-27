<template>
  <div v-loading="loading" style="max-width:720px;margin:0 auto">
    <el-card v-if="result">
      <!-- 顶部操作 -->
      <template #header>
        <div style="display:flex;align-items:center;justify-content:space-between">
          <el-button link @click="$router.push('/user/dashboard')">
            <el-icon><ArrowLeft /></el-icon> 返回首页
          </el-button>
          <el-button link @click="$router.push('/user/history')">历史记录</el-button>
        </div>
      </template>

      <!-- 主要结果展示 -->
      <div style="text-align:center;padding:24px 0 16px">
        <div style="font-size:14px;color:#888;margin-bottom:8px">{{ result.questionnaire_name }}</div>
        <div class="result-score">{{ result.std_score ?? result.raw_score }}</div>
        <div style="color:#aaa;font-size:12px;margin-top:4px">
          {{ result.std_score ? '标准分' : '原始分' }}（满分 {{ maxScore(result.questionnaire_code) }}）
        </div>
        <div style="margin-top:16px">
          <span class="level-badge" :class="'level-' + result.level" style="font-size:15px;padding:6px 20px">
            {{ result.level_label }}
          </span>
          <el-tag v-if="result.risk_flag" type="danger" style="margin-left:10px">
            <el-icon><Warning /></el-icon> 高风险预警
          </el-tag>
        </div>
      </div>

      <el-divider />

      <!-- 得分详解 -->
      <el-row :gutter="20" style="margin-bottom:20px">
        <el-col :span="8" v-for="item in scoreLevels(result.questionnaire_code)" :key="item.label">
          <div style="text-align:center;padding:12px;border-radius:8px;border:1px solid #f0f0f0"
               :style="item.level === result.level ? 'border-color:#1677ff;background:#f0f7ff' : ''">
            <div :style="{ color: item.color, fontWeight: '700', fontSize: '13px' }">{{ item.label }}</div>
            <div style="color:#aaa;font-size:11px;margin-top:2px">{{ item.range }}</div>
          </div>
        </el-col>
      </el-row>

      <!-- 文字解读 -->
      <div class="interpretation-box">
        <div style="font-weight:700;color:#1677ff;margin-bottom:8px">
          <el-icon><ChatLineSquare /></el-icon> 结果解读
        </div>
        {{ result.interpretation }}
      </div>

      <!-- 原始分 / 标准分 -->
      <el-row :gutter="20" style="margin-top:20px">
        <el-col :span="12">
          <el-statistic title="原始总分" :value="result.raw_score" />
        </el-col>
        <el-col :span="12" v-if="result.std_score">
          <el-statistic title="标准分（×1.25）" :value="result.std_score" />
        </el-col>
      </el-row>

      <el-divider />
      <div style="color:#aaa;font-size:12px;text-align:right">
        测评时间：{{ result.created_at }}
      </div>

      <!-- 危机提示 -->
      <el-alert v-if="result.risk_flag" type="error" show-icon :closable="false" style="margin-top:16px"
                title="重要提示：您的测评结果显示存在较高心理健康风险，建议尽快寻求专业心理援助或医疗帮助。
                       心理援助热线：400-161-9995（全国）" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { surveyApi } from '@/api'

const route   = useRoute()
const loading = ref(true)
const result  = ref(null)

const maxScoreMap = { PHQ9: 27, GAD7: 21, SDS: 100, SAS: 100 }
const maxScore = code => maxScoreMap[code] || '—'

const levelConfig = {
  PHQ9: [
    { level: 'none',              label: '无抑郁',   range: '0-4',   color: '#52c41a' },
    { level: 'mild',              label: '轻度',     range: '5-9',   color: '#d48806' },
    { level: 'moderate',          label: '中度',     range: '10-14', color: '#d46b08' },
    { level: 'moderately_severe', label: '中重度',   range: '15-19', color: '#cf1322' },
    { level: 'severe',            label: '重度',     range: '20-27', color: '#a8071a' },
  ],
  GAD7: [
    { level: 'none',     label: '无焦虑', range: '0-4',  color: '#52c41a' },
    { level: 'mild',     label: '轻度',   range: '5-9',  color: '#d48806' },
    { level: 'moderate', label: '中度',   range: '10-14',color: '#d46b08' },
    { level: 'severe',   label: '重度',   range: '15-21',color: '#cf1322' },
  ],
  SDS: [
    { level: 'none',     label: '正常',   range: '<53',  color: '#52c41a' },
    { level: 'mild',     label: '轻度',   range: '53-62',color: '#d48806' },
    { level: 'moderate', label: '中度',   range: '63-72',color: '#d46b08' },
    { level: 'severe',   label: '重度',   range: '>72',  color: '#cf1322' },
  ],
  SAS: [
    { level: 'none',     label: '正常',   range: '<50',  color: '#52c41a' },
    { level: 'mild',     label: '轻度',   range: '50-59',color: '#d48806' },
    { level: 'moderate', label: '中度',   range: '60-69',color: '#d46b08' },
    { level: 'severe',   label: '重度',   range: '≥70',  color: '#cf1322' },
  ],
}
const scoreLevels = code => levelConfig[code] || []

onMounted(async () => {
  try {
    const res = await surveyApi.getResult(route.params.id)
    if (res.code === 200) result.value = res.data
  } finally {
    loading.value = false
  }
})
</script>
