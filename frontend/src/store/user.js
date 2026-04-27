import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, adminApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token       = ref(localStorage.getItem('token') || '')
  const user        = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const unreadAlerts = ref(0)   // 全局未读预警数，所有组件共享

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin    = computed(() => user.value?.role === 'admin')

  function setAuth(t, u) {
    token.value = t
    user.value  = u
    localStorage.setItem('token', t)
    localStorage.setItem('user', JSON.stringify(u))
  }

  function logout() {
    token.value = ''
    user.value  = null
    unreadAlerts.value = 0
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function fetchMe() {
    try {
      const res = await authApi.me()
      if (res.code === 200) {
        user.value = res.user
        localStorage.setItem('user', JSON.stringify(res.user))
      }
    } catch {}
  }

  // 从服务端拉取最新未读数
  async function fetchUnread() {
    if (!isAdmin.value) return
    try {
      const res = await adminApi.alerts(1, 1)
      if (res.code === 200) unreadAlerts.value = res.total
    } catch {}
  }

  return { token, user, isLoggedIn, isAdmin, unreadAlerts, setAuth, logout, fetchMe, fetchUnread }
})
