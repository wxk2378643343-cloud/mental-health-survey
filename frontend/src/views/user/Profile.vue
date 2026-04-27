<template>
  <div style="max-width:560px;margin:0 auto">
    <el-card>
      <template #header><span><el-icon><User /></el-icon> 个人信息</span></template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名">
          <el-input :value="store.user?.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="年龄" prop="age">
          <el-input-number v-model="form.age" :min="10" :max="100" style="width:100%" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="form.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
            <el-radio value="other">其他</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-divider>修改密码（不修改则留空）</el-divider>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="form.new_password" type="password" placeholder="留空则不修改" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="save">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'
import { useUserStore } from '@/store/user'

const store  = useUserStore()
const formRef = ref()
const saving  = ref(false)

const form = reactive({ email: '', phone: '', age: null, gender: 'other', new_password: '' })

const rules = {
  new_password: [{ min: 6, message: '密码至少6位', trigger: 'blur' }],
}

onMounted(() => {
  const u = store.user
  if (u) {
    form.email  = u.email  || ''
    form.phone  = u.phone  || ''
    form.age    = u.age    || null
    form.gender = u.gender || 'other'
  }
})

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    const res = await authApi.updateProfile(form)
    if (res.code === 200) {
      store.setAuth(store.token, res.user)
      ElMessage.success('保存成功')
      form.new_password = ''
    } else {
      ElMessage.error(res.msg)
    }
  } finally {
    saving.value = false
  }
}
</script>
