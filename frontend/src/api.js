/**
 * API 服务模块
 * 封装与后端的所有 HTTP 请求
 *
 * 后端地址优先级：
 * 1. 构建时指定：VITE_API_BASE=https://xxx npm run build
 * 2. 开发环境默认：http://localhost:8000
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

/**
 * 上传简历 PDF 文件
 * @param {File} file - PDF 格式的简历文件
 * @returns {Promise<Object>} 解析结果和提取信息
 */
export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/api/resume/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '上传失败' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * 简历与岗位匹配度评分
 * @param {string} resumeId - 简历 ID
 * @param {string} jobDescription - 岗位需求描述
 * @returns {Promise<Object>} 匹配评分结果
 */
export async function matchResume(resumeId, jobDescription) {
  const response = await fetch(`${API_BASE}/api/match/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_id: resumeId, job_description: jobDescription }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '匹配失败' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * 获取简历信息
 * @param {string} resumeId - 简历 ID
 * @returns {Promise<Object>} 简历信息
 */
export async function getResumeInfo(resumeId) {
  const response = await fetch(`${API_BASE}/api/resume/${resumeId}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '获取失败' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * 健康检查
 * @returns {Promise<Object>}
 */
export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
