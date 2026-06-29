import { useState } from 'react';
import { uploadResume, matchResume } from './api';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [resumeId, setResumeId] = useState(null);
  const [extractedInfo, setExtractedInfo] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [matchResult, setMatchResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState('upload'); // upload | match | result

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type !== 'application/pdf') {
      setError('请选择 PDF 格式的文件');
      setFile(null);
      return;
    }
    setFile(selected);
    setError('');
  };

  const handleUpload = async () => {
    if (!file) {
      setError('请先选择简历文件');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await uploadResume(file);
      setResumeId(data.resume_id);
      setExtractedInfo(data.extracted_info);
      setStep('match');
    } catch (err) {
      setError(err.message || '上传或解析失败');
    } finally {
      setLoading(false);
    }
  };

  const handleMatch = async () => {
    if (!jobDescription.trim()) {
      setError('请输入岗位需求描述');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await matchResume(resumeId, jobDescription);
      setMatchResult(data);
      setStep('result');
    } catch (err) {
      setError(err.message || '匹配评分失败');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResumeId(null);
    setExtractedInfo(null);
    setJobDescription('');
    setMatchResult(null);
    setError('');
    setStep('upload');
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#eab308';
    return '#ef4444';
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📄 智能简历分析系统</h1>
        <p>AI 赋能的简历解析、信息提取与岗位匹配评分</p>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={() => setError('')}>✕</button>
          </div>
        )}

        {/* 步骤指示器 */}
        <div className="steps">
          <div className={`step ${step === 'upload' ? 'active' : 'completed'}`}>
            <span className="step-number">1</span>
            <span className="step-label">上传简历</span>
          </div>
          <div className="step-line" />
          <div className={`step ${step === 'match' ? 'active' : step === 'result' ? 'completed' : ''}`}>
            <span className="step-number">2</span>
            <span className="step-label">岗位匹配</span>
          </div>
          <div className="step-line" />
          <div className={`step ${step === 'result' ? 'active' : ''}`}>
            <span className="step-number">3</span>
            <span className="step-label">查看结果</span>
          </div>
        </div>

        {/* 步骤 1: 上传简历 */}
        {step === 'upload' && (
          <div className="card upload-card">
            <h2>上传简历文件</h2>
            <p className="hint">支持 PDF 格式，最大 10MB</p>

            <div className="file-upload-area">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                id="file-input"
                className="file-input"
              />
              <label htmlFor="file-input" className="file-label">
                {file ? (
                  <span className="file-selected">📎 {file.name}</span>
                ) : (
                  <span className="file-placeholder">
                    点击选择 PDF 简历文件
                  </span>
                )}
              </label>
            </div>

            <button
              className="btn btn-primary"
              onClick={handleUpload}
              disabled={loading || !file}
            >
              {loading ? '解析中...' : '上传并解析'}
            </button>
          </div>
        )}

        {/* 步骤 2: 输入岗位需求 */}
        {step === 'match' && (
          <div className="card match-card">
            <h2>简历信息已提取</h2>

            {extractedInfo && (
              <div className="info-preview">
                <div className="info-grid">
                  {extractedInfo.basic_info?.name && (
                    <div className="info-item">
                      <span className="info-label">姓名</span>
                      <span className="info-value">{extractedInfo.basic_info.name}</span>
                    </div>
                  )}
                  {extractedInfo.basic_info?.phone && (
                    <div className="info-item">
                      <span className="info-label">电话</span>
                      <span className="info-value">{extractedInfo.basic_info.phone}</span>
                    </div>
                  )}
                  {extractedInfo.basic_info?.email && (
                    <div className="info-item">
                      <span className="info-label">邮箱</span>
                      <span className="info-value">{extractedInfo.basic_info.email}</span>
                    </div>
                  )}
                  {extractedInfo.basic_info?.address && (
                    <div className="info-item">
                      <span className="info-label">地址</span>
                      <span className="info-value">{extractedInfo.basic_info.address}</span>
                    </div>
                  )}
                </div>
                {extractedInfo.job_intention && (
                  <div className="extra-info">
                    <span className="info-label">求职意向</span>
                    <span className="info-value">{extractedInfo.job_intention.job_intention || '未提及'}</span>
                    {extractedInfo.job_intention.expected_salary && (
                      <>
                        <span className="info-label" style={{ marginLeft: 16 }}>期望薪资</span>
                        <span className="info-value">{extractedInfo.job_intention.expected_salary}</span>
                      </>
                    )}
                  </div>
                )}
                {extractedInfo.background_info?.education && (
                  <div className="extra-info">
                    <span className="info-label">学历</span>
                    <span className="info-value">{extractedInfo.background_info.education}</span>
                  </div>
                )}
              </div>
            )}

            <div className="jd-section" style={{ marginTop: 24 }}>
              <h2>输入岗位需求</h2>
              <p className="hint">粘贴岗位描述（JD），系统将自动进行匹配评分</p>
              <textarea
                className="jd-input"
                rows={6}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder={`例如：
职位名称：高级前端工程师

岗位职责：
1. 负责公司核心产品的前端架构设计与开发
2. 优化页面性能和用户体验

任职要求：
- 5 年以上前端开发经验
- 精通 React/Vue 等主流框架
- 熟悉 TypeScript、Webpack/Vite`}
              />
            </div>

            <div className="btn-group">
              <button className="btn btn-secondary" onClick={handleReset}>
                重新上传
              </button>
              <button
                className="btn btn-primary"
                onClick={handleMatch}
                disabled={loading || !jobDescription.trim()}
              >
                {loading ? '评分中...' : '开始匹配评分'}
              </button>
            </div>
          </div>
        )}

        {/* 步骤 3: 查看结果 */}
        {step === 'result' && matchResult && (
          <div className="card result-card">
            <h2>匹配评分结果</h2>

            <div className="score-overview">
              <div
                className="score-ring"
                style={{
                  '--score-color': getScoreColor(matchResult.overall_score),
                }}
              >
                <svg viewBox="0 0 120 120" className="score-ring-svg">
                  <circle cx="60" cy="60" r="54" fill="none" stroke="#e5e7eb" strokeWidth="8" />
                  <circle
                    cx="60" cy="60" r="54"
                    fill="none"
                    stroke="var(--score-color)"
                    strokeWidth="8"
                    strokeDasharray={`${(matchResult.overall_score / 100) * 339.292} 339.292`}
                    strokeLinecap="round"
                    transform="rotate(-90 60 60)"
                  />
                </svg>
                <div className="score-text">
                  <span className="score-value">{matchResult.overall_score}</span>
                  <span className="score-unit">分</span>
                </div>
              </div>
            </div>

            <div className="dimensions">
              <h3>各维度评分</h3>
              {matchResult.dimensions && (
                <div className="dimension-list">
                  <DimensionBar
                    label="技能匹配度"
                    value={matchResult.dimensions.skill_match}
                    color="#3b82f6"
                  />
                  <DimensionBar
                    label="经验相关性"
                    value={matchResult.dimensions.experience_relevance}
                    color="#8b5cf6"
                  />
                  <DimensionBar
                    label="关键词匹配率"
                    value={matchResult.dimensions.keyword_match}
                    color="#f59e0b"
                  />
                  {matchResult.dimensions.ai_score != null && (
                    <DimensionBar
                      label="AI 综合评分"
                      value={matchResult.dimensions.ai_score}
                      color="#06b6d4"
                    />
                  )}
                </div>
              )}
            </div>

            {matchResult.analysis_summary && (
              <div className="analysis">
                <h3>AI 分析总结</h3>
                <p>{matchResult.analysis_summary}</p>
              </div>
            )}

            {matchResult.job_description_summary && (
              <div className="job-summary">
                <h3>岗位相关摘要</h3>
                <p>{matchResult.job_description_summary}</p>
              </div>
            )}

            <button className="btn btn-primary" onClick={handleReset} style={{ marginTop: 24 }}>
              重新开始
            </button>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>智能简历分析系统 · AI-Powered Resume Analyzer</p>
      </footer>
    </div>
  );
}

function DimensionBar({ label, value, color }) {
  return (
    <div className="dimension-bar">
      <div className="dimension-header">
        <span className="dimension-label">{label}</span>
        <span className="dimension-value" style={{ color }}>{Math.round(value)}分</span>
      </div>
      <div className="dimension-track">
        <div
          className="dimension-fill"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export default App;
