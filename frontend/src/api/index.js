import axios from 'axios'
import { ElMessage } from 'element-plus'
// 创建axios实例
const http = axios.create({ baseURL: '/api', timeout: 10000 })

// 请求拦截：注入 Token
http.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = 'Bearer ' + token
  return cfg
})

// 响应拦截：统一处理 401
http.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    } else {
      ElMessage.error(err.response?.data?.msg || '网络错误')
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  login:         data => http.post('/auth/login', data),
  register:      data => http.post('/auth/register', data),
  me:            ()   => http.get('/auth/me'),
  updateProfile: data => http.put('/auth/update_profile', data),
}

export const surveyApi = {
  listQuestionnaires: ()         => http.get('/questionnaires'),
  getQuestionnaire:   id         => http.get(`/questionnaires/${id}`),
  startSurvey:        data       => http.post('/surveys', data),
  submitSurvey:       (rid, data)=> http.post(`/surveys/${rid}/submit`, data),
  myResults:          ()         => http.get('/results'),
  getResult:          id         => http.get(`/results/${id}`),
  myStats:            ()         => http.get('/stats/me'),
}

export const adminApi = {
  stats:        ()               => http.get('/admin/stats'),
  users:        (page, kw)       => http.get('/admin/users', { params: { page, q: kw } }),
  toggleUser:   uid              => http.put(`/admin/users/${uid}/toggle`),
  results:      (page, risk, code)=>http.get('/admin/results', { params: { page, risk, code } }),
  alerts:       (page, unread)   => http.get('/admin/alerts', { params: { page, unread } }),
  markRead:     id               => http.put(`/admin/alerts/${id}/read`),
  markUnread:   id               => http.put(`/admin/alerts/${id}/unread`),
  markAllRead:  ()               => http.put('/admin/alerts/read_all'),
  // 问卷管理
  listQuestionnaires:   (page=1, size=10) => http.get('/admin/questionnaires', { params: { page, size } }),
  createQuestionnaire:  data   => http.post('/admin/questionnaires', data),
  deleteQuestionnaire:  id     => http.delete(`/admin/questionnaires/${id}`),
}
