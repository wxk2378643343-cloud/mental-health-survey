<template>
  <div>
    <!-- 欢迎区 -->
    <div style="margin-bottom:24px">
      <div style="font-size:1.2rem;font-weight:700;color:#0f172a">
        你好，{{ store.user?.username }} 👋
      </div>
      <div style="color:#64748b;font-size:13px;margin-top:4px">
        选择一项量表开始今天的心理健康自测
      </div>
    </div>

    <!-- 量表卡片 -->
    <el-row :gutter="16" v-loading="loading">
      <el-col :xs="24" :sm="12" :xl="6"
              v-for="q in questionnaires" :key="q.id"
              style="margin-bottom:16px">
        <div class="q-card" :style="{ '--accent': qColor(q.code) }" @click="startSurvey(q)">
          <div class="q-card__top">
            <div class="q-card__icon-box" :style="{ background: qBg(q.code) }">
              <el-icon size="22" :color="qColor(q.code)">
                <component :is="qIcon(q.code)" />
              </el-icon>
            </div>
            <div class="q-card__meta">
              <div class="q-card__tag" :style="{ background: qBg(q.code), color: qColor(q.code) }">
                {{ q.use_standard ? '标准分' : '原始分' }}
              </div>
            </div>
          </div>
          <div class="q-card__name">{{ q.name }}</div>
          <div class="q-card__desc">{{ q.description?.slice(0, 42) }}…</div>
          <div class="q-card__footer">
            <span class="q-card__count">{{ q.total_items }} 题</span>
            <el-button type="primary" size="small" round :loading="startingId === q.id"
                       :style="{ background: qColor(q.code), borderColor: qColor(q.code) }">
              开始测评
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 最近记录 -->
    <el-card style="margin-top:8px">
      <template #header>
        <div style="display:flex;align-items:center;justify-content:space-between">
          <span style="font-weight:600;color:#0f172a">最近测评记录</span>
          <el-button link type="primary" size="small" @click="$router.push('/user/history')">
            查看全部 →
          </el-button>
        </div>
      </template>
      <el-empty v-if="!recentResults.length" description="暂无记录，去完成一次测评吧" :image-size="80" />
      <el-table v-else :data="recentResults" size="small" :show-header="true">
        <el-table-column prop="questionnaire_name" label="量表" />
        <el-table-column label="得分" width="80">
          <template #default="{ row }">
            <span style="font-weight:700;color:#4f6ef7">{{ row.std_score ?? row.raw_score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="等级" width="100">
          <template #default="{ row }">
            <span class="level-badge" :class="'level-' + row.level">{{ row.level_label }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="165" />
        <el-table-column width="70" align="right">
          <template #default="{ row }">
            <el-button link size="small" @click="$router.push('/user/result/' + row.id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { surveyApi } from '@/api'
import { useUserStore } from '@/store/user'

const router        = useRouter()
const store         = useUserStore()
const loading       = ref(false)
const questionnaires= ref([])
const recentResults = ref([])
const startingId    = ref(null)

const iconMap  = { PHQ9: 'Sunny', GAD7: 'MostlyCloudy', SDS: 'Moon', SAS: 'WindPower' }
const colorMap = { PHQ9: '#4f6ef7', GAD7: '#10b981', SDS: '#f59e0b', SAS: '#ef4444' }
const bgMap    = { PHQ9: '#eef2ff', GAD7: '#ecfdf5', SDS: '#fffbeb', SAS: '#fef2f2' }

const qIcon  = c => iconMap[c]  || 'Document'
const qColor = c => colorMap[c] || '#64748b'
const qBg    = c => bgMap[c]    || '#f1f5f9'

async function loadData() {
  loading.value = true
  try {
    const [qRes, rRes] = await Promise.all([surveyApi.listQuestionnaires(), surveyApi.myResults()])
    if (qRes.code === 200) questionnaires.value = qRes.data
    if (rRes.code === 200) recentResults.value  = rRes.data.slice(0, 5)
  } finally {
    loading.value = false
  }
}

async function startSurvey(q) {
  startingId.value = q.id
  try {
    const res = await surveyApi.startSurvey({ questionnaire_id: q.id })
    if (res.code === 200) {
      sessionStorage.setItem('surveyData_' + res.response_id, JSON.stringify(res.questionnaire))
      router.push(`/user/survey/${res.response_id}`)
    } else {
      ElMessage.error(res.msg)
    }
  } finally {
    startingId.value = null
  }
}

onMounted(loadData)
</script>

<style scoped>
.q-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 20px;
  cursor: pointer;
  transition: transform .18s, box-shadow .18s, border-color .18s;
  height: 100%;
  box-sizing: border-box;
}
.q-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,.1);
  border-color: var(--accent);
}
.q-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.q-card__icon-box {
  width: 44px; height: 44px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.q-card__tag {
  font-size: 11px; font-weight: 600;
  padding: 2px 8px; border-radius: 20px;
}
.q-card__name {
  font-size: 14px; font-weight: 700;
  color: #0f172a; margin-bottom: 6px;
  line-height: 1.4;
}
.q-card__desc {
  font-size: 12px; color: #94a3b8;
  line-height: 1.6; margin-bottom: 16px;
}
.q-card__footer {
  display: flex; align-items: center; justify-content: space-between;
}
.q-card__count {
  font-size: 12px; color: #94a3b8; font-weight: 500;
}
</style>
