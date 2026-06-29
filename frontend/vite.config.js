import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // GitHub Pages 部署时使用仓库名作为 base path
  // 如果部署到自定义域名，改为 base: '/'
  base: '/resume-analyzer/',
})
