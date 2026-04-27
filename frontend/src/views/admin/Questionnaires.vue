<template>
  <div>
    <div class="page-title">问卷管理</div>

    <!-- 问卷列表 -->
    <el-card style="margin-bottom:20px">
      <template #header>
        <div style="display:flex;align-items:center;justify-content:space-between">
          <span><el-icon><List /></el-icon> 全部问卷</span>
          <el-button type="primary" :icon="Plus" @click="showDialog = true">
            创建新问卷
          </el-button>
        </div>
      </template>

      <el-table :data="questionnaires" v-loading="listLoading" stripe>
        <el-table-column prop="id"   label="ID"   width="60" />
        <el-table-column prop="code" label="编码"  width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="builtinCodes.has(row.code) ? 'info' : 'success'">
              {{ row.code }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column label="题数" width="70" align="center">
          <template #default="{ row }">{{ row.total_items }}</template>
        </el-table-column>
        <el-table-column label="计分方式" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.use_standard ? 'warning' : 'primary'">
              {{ row.use_standard ? '标准分' : '原始分' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="测评次数" width="90" align="center">
          <template #default="{ row }">{{ row.result_count ?? 0 }}</template>
        </el-table-column>
        <el-table-column label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-text :type="builtinCodes.has(row.code) ? 'info' : 'success'" size="small">
              {{ builtinCodes.has(row.code) ? '内置' : '自定义' }}
            </el-text>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!builtinCodes.has(row.code)" type="danger" size="small" link
                       @click="deleteQ(row)">删除</el-button>
            <el-text v-else type="info" size="small">—</el-text>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top:16px;justify-content:flex-end;display:flex"
        v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @current-change="loadList" />
    </el-card>

    <!-- 创建问卷对话框 -->
    <el-dialog v-model="showDialog" title="创建新问卷" width="780px"
               :close-on-click-modal="false" destroy-on-close>
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="90px"
               style="max-height:70vh;overflow-y:auto;padding-right:8px">

        <!-- 基本信息 -->
        <el-divider content-position="left"><el-icon><InfoFilled /></el-icon> 基本信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="问卷名称" prop="name">
              <el-input v-model="form.name" placeholder="例：焦虑自测量表" maxlength="60" show-word-limit />
            </el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="问卷编码" prop="code">
              <el-input v-model="form.code" placeholder="例：MY_ANX" maxlength="20"
                        style="text-transform:uppercase"
                        @input="form.code = form.code.toUpperCase()" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="简介" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2"
                    placeholder="简短描述该量表的用途（可选）" maxlength="200" show-word-limit />
        </el-form-item>

        <el-form-item label="填写说明" prop="instructions">
          <el-input v-model="form.instructions" type="textarea" :rows="2"
                    placeholder="显示给用户的填写提示（可选）" maxlength="300" show-word-limit />
        </el-form-item>

        <el-form-item label="计分方式">
          <el-radio-group v-model="form.use_standard">
            <el-radio :value="false">原始分（直接累加）</el-radio>
            <el-radio :value="true">标准分（原始分 × 1.25，适合 SDS/SAS 类型）</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 题目列表 -->
        <el-divider content-position="left">
          <el-icon><EditPen /></el-icon> 题目设置（共 {{ form.questions.length }} 题）
        </el-divider>

        <div v-for="(q, qi) in form.questions" :key="qi"
             style="border:1px solid #e8e8e8;border-radius:8px;padding:14px 16px;margin-bottom:12px;background:#fafafa">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
            <el-tag type="primary" size="small">Q{{ qi + 1 }}</el-tag>
            <el-input v-model="q.content" placeholder="题目内容" style="flex:1" />
            <el-checkbox v-model="q.reverse" label="反向计分" />
            <el-button type="danger" link :icon="Delete" @click="removeQuestion(qi)"
                       :disabled="form.questions.length <= 1" />
          </div>

          <!-- 选项列表 -->
          <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">
            <div v-for="(opt, oi) in q.options" :key="oi"
                 style="display:flex;align-items:center;gap:4px">
              <el-tag size="small" type="info">{{ optLabel(oi, form.use_standard) }}</el-tag>
              <el-input v-model="q.options[oi]" size="small" style="width:110px"
                        :placeholder="`选项${oi+1}`" />
              <el-button v-if="q.options.length > 2" type="danger" link size="small"
                         :icon="Close" @click="q.options.splice(oi, 1)" />
            </div>
            <el-button v-if="q.options.length < 5" type="primary" link size="small"
                       :icon="Plus" @click="q.options.push('')">添加选项</el-button>
          </div>
        </div>

        <el-button type="primary" plain :icon="Plus" @click="addQuestion" style="width:100%;margin-bottom:16px">
          添加题目
        </el-button>

        <!-- 评分规则 -->
        <el-divider content-position="left">
          <el-icon><DataAnalysis /></el-icon> 评分分级规则
        </el-divider>
        <el-alert type="info" :closable="false" show-icon style="margin-bottom:12px"
                  :title="form.use_standard
                    ? '标准分 = 原始分 × 1.25，请填写标准分范围'
                    : '原始分 = 所有题目得分之和，请填写原始分范围'" />

        <el-table :data="form.scoring_rules" size="small" style="margin-bottom:10px">
          <el-table-column label="最低分" width="110">
            <template #default="{ row }">
              <el-input-number v-model="row.min" :min="0" :max="999" size="small"
                               controls-position="right" style="width:90px" />
            </template>
          </el-table-column>
          <el-table-column label="最高分" width="110">
            <template #default="{ row }">
              <el-input-number v-model="row.max" :min="0" :max="999" size="small"
                               controls-position="right" style="width:90px" />
            </template>
          </el-table-column>
          <el-table-column label="Level 键" width="160">
            <template #default="{ row }">
              <el-select v-model="row.level" size="small" placeholder="选择等级键">
                <el-option label="none（正常）"             value="none" />
                <el-option label="mild（轻度）"             value="mild" />
                <el-option label="moderate（中度）"         value="moderate" />
                <el-option label="moderately_severe（中重）"value="moderately_severe" />
                <el-option label="severe（重度）"           value="severe" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="显示名称" min-width="110">
            <template #default="{ row }">
              <el-input v-model="row.label" size="small" placeholder="如：轻度焦虑" />
            </template>
          </el-table-column>
          <el-table-column width="50" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link :icon="Delete"
                         :disabled="form.scoring_rules.length <= 1"
                         @click="form.scoring_rules.splice($index, 1)" />
            </template>
          </el-table-column>
        </el-table>

        <el-button type="primary" plain :icon="Plus" @click="addRule" style="width:100%">
          添加分级
        </el-button>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitCreate">
          确认创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Close } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

const builtinCodes  = new Set(['PHQ9', 'GAD7', 'SDS', 'SAS'])
const listLoading   = ref(false)
const questionnaires= ref([])
const total         = ref(0)
const page          = ref(1)
const pageSize      = 10
const showDialog    = ref(false)
const submitting    = ref(false)
const formRef       = ref()

// 初始表单
function initForm() {
  return {
    name: '', code: '',
    description: '', instructions: '',
    use_standard: false,
    questions: [
      { content: '', options: ['', '', '', ''], reverse: false }
    ],
    scoring_rules: [
      { min: 0,  max: 9,  level: 'none',     label: '正常' },
      { min: 10, max: 20, level: 'mild',     label: '轻度' },
      { min: 21, max: 999,level: 'severe',   label: '重度' },
    ]
  }
}

const form = reactive(initForm())

const formRules = {
  name: [{ required: true, message: '请输入问卷名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入问卷编码', trigger: 'blur' },
    { pattern: /^[A-Z0-9_]+$/, message: '编码只能含大写字母、数字、下划线', trigger: 'blur' },
  ],
}

// 选项标签（原始分从0开始，标准分从1开始）
function optLabel(index, useStandard) {
  return useStandard ? index + 1 : index
}

function addQuestion() {
  form.questions.push({ content: '', options: ['', '', '', ''], reverse: false })
}

function removeQuestion(idx) {
  form.questions.splice(idx, 1)
}

function addRule() {
  const last = form.scoring_rules[form.scoring_rules.length - 1]
  form.scoring_rules.push({ min: (last?.max ?? 0) + 1, max: 999, level: 'severe', label: '' })
}

async function loadList(p = page.value) {
  page.value = p
  listLoading.value = true
  try {
    const res = await adminApi.listQuestionnaires(p, pageSize)
    if (res.code === 200) { questionnaires.value = res.data; total.value = res.total }
  } finally {
    listLoading.value = false
  }
}

async function deleteQ(row) {
  await ElMessageBox.confirm(
    `确认删除问卷「${row.name}」？此操作不可恢复。`, '警告', { type: 'warning' }
  )
  const res = await adminApi.deleteQuestionnaire(row.id)
  if (res.code === 200) {
    ElMessage.success('删除成功')
    loadList()
  } else {
    ElMessage.error(res.msg)
  }
}

async function submitCreate() {
  await formRef.value.validate()

  // 前端额外校验
  for (let i = 0; i < form.questions.length; i++) {
    const q = form.questions[i]
    if (!q.content.trim()) {
      ElMessage.error(`第 ${i + 1} 题内容不能为空`)
      return
    }
    const validOpts = q.options.filter(o => o.trim())
    if (validOpts.length < 2) {
      ElMessage.error(`第 ${i + 1} 题至少需要2个有效选项`)
      return
    }
  }

  submitting.value = true
  try {
    const payload = {
      name:          form.name,
      code:          form.code,
      description:   form.description,
      instructions:  form.instructions,
      use_standard:  form.use_standard,
      scoring_rules: form.scoring_rules,
      questions: form.questions.map(q => ({
        content: q.content.trim(),
        options: q.options.filter(o => o.trim()),
        reverse: q.reverse,
      })),
    }
    const res = await adminApi.createQuestionnaire(payload)
    if (res.code === 200) {
      ElMessage.success('问卷创建成功！')
      showDialog.value = false
      Object.assign(form, initForm())
      loadList()
    } else {
      ElMessage.error(res.msg)
    }
  } finally {
    submitting.value = false
  }
}

onMounted(loadList)
</script>
