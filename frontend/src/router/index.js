import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  { path: '/',        redirect: '/login' },
  { path: '/login',   component: () => import('@/views/Login.vue'),     meta: { guest: true } },
  { path: '/register',component: () => import('@/views/Register.vue'),  meta: { guest: true } },

  {
    path: '/user',
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '',          redirect: '/user/dashboard' },
      { path: 'dashboard', component: () => import('@/views/user/Dashboard.vue') },
      { path: 'survey/:id',component: () => import('@/views/user/Survey.vue') },
      { path: 'result/:id',component: () => import('@/views/user/Result.vue') },
      { path: 'history',   component: () => import('@/views/user/History.vue') },
      { path: 'profile',   component: () => import('@/views/user/Profile.vue') },
    ]
  },

  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '',          redirect: '/admin/dashboard' },
      { path: 'dashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'users',     component: () => import('@/views/admin/Users.vue') },
      { path: 'results',   component: () => import('@/views/admin/Results.vue') },
      { path: 'alerts',         component: () => import('@/views/admin/Alerts.vue') },
      { path: 'questionnaires', component: () => import('@/views/admin/Questionnaires.vue') },
    ]
  },

  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const store = useUserStore()
  if (to.meta.requiresAuth && !store.isLoggedIn) return next('/login')
  if (to.meta.requiresAdmin && !store.isAdmin)    return next('/user/dashboard')
  if (to.meta.guest && store.isLoggedIn) {
    return next(store.isAdmin ? '/admin/dashboard' : '/user/dashboard')
  }
  next()
})

export default router
