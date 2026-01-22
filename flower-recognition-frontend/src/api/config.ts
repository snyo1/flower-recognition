// API配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

export const api = {
  // 花卉识别
  identify: `${API_BASE_URL}/flower/identify`,

  // 智能问答
  chat: `${API_BASE_URL}/qa/chat`,

  // 知识库
  getKnowledge: (keyword: string = '') => `${API_BASE_URL}/knowledge/${keyword ? `?keyword=${keyword}` : ''}`,
  createKnowledge: `${API_BASE_URL}/knowledge/`,
  updateKnowledge: (id: number) => `${API_BASE_URL}/knowledge/${id}`,
  deleteKnowledge: (id: number) => `${API_BASE_URL}/knowledge/${id}`,
}

export const API_BASE_URL_FULL = API_BASE_URL
