<template>
  <div v-loading="loading" style="max-width:800px;margin:0 auto">
    <el-empty v-if="!loading && !questionnaire" description="问卷数据加载失败，请返回重新开始">
      <template #extra>
        <el-button @click="$router.push('/user/dashboard')">返回首页</el-button>
      </template>
    </el-empty>

    <el-card v-if="questionnaire">
      <!-- 头部进度 -->
      <template #header>
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
          <span style="font-size:16px;font-weight:700">{{ questionnaire.name }}</span>
          <el-tag type="primary">已完成 {{ answeredCount }} / {{ questionnaire.total_items }} 题</el-tag>
        </div>
        <el-progress :percentage="progress" :stroke-width="8" style="margin-top:10px"
                     :status="progress === 100 ? 'success' : ''" />
      </template>

      <!-- 填写说明 -->
      <el-alert :title="questionnaire.instructions" type="info" show-icon :closable="false"
                style="margin-bottom:20px" />

      <!-- 题目列表 -->
      <div v-for="q in questionnaire.questions" :key="q.id"
           class="question-item" :class="{ answered: answers[q.id] !== undefined }">
        <div style="margin-bottom:10px;font-size:14px">
          <span class="question-no">Q{{ q.question_no }}.</span>
          <span>{{ q.content }}</span>
          <el-tag v-if="q.reverse" size="small" type="warning" style="margin-left:8px">反向计分</el-tag>
        </div>
        <el-radio-group v-model="answers[q.id]">
          <el-space wrap>
            <el-radio
              v-for="(label, val) in q.options"
              :key="val" :value="parseInt(val)"
              border size="small"
            >{{ label }}</el-radio>
          </el-space>
        </el-radio-group>
      </div>

      <!-- 提交按钮 -->
      <el-divider />
      <div style="text-align:center">
        <el-button type="primary" size="large" :loading="submitting"
                   :disabled="answeredCount < questionnaire.total_items"
                   @click="submitSurvey">
          <el-icon><CircleCheck /></el-icon>
          &nbsp;提交问卷（{{ answeredCount }}/{{ questionnaire.total_items }} 题已作答）
        </el-button>
        <div style="color:#aaa;font-size:12px;margin-top:10px">
          请完整填写所有题目后方可提交
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { surveyApi } from '@/api'

const route       = useRoute()
const router      = useRouter()
const responseId  = parseInt(route.params.id)
const loading     = ref(true)
const submitting  = ref(false)
const questionnaire = ref(null)
const answers     = reactive({})

const answeredCount = computed(() =>
  questionnaire.value
    ? questionnaire.value.questions.filter(q => answers[q.id] !== undefined).length
    : 0
)
const progress = computed(() =>
  questionnaire.value
    ? Math.round(answeredCount.value / questionnaire.value.total_items * 100)
    : 0
)

onMounted(() => {
  const stored = sessionStorage.getItem('surveyData_' + responseId)
  if (stored) {
    try { questionnaire.value = JSON.parse(stored) } catch {}
  }
  loading.value = false
})

async function submitSurvey() {
  submitting.value = true
  try {
    const res = await surveyApi.submitSurvey(responseId, { answers })
    if (res.code === 200) {
      ElMessage.success('提交成功！')
      sessionStorage.removeItem('surveyData_' + responseId)
      router.push('/user/result/' + res.result.id)
    } else {
      ElMessage.error(res.msg)
    }
  } finally {
    submitting.value = false
  }
}
</script>
