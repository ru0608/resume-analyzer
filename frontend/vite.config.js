import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [react()],
  // 开发模式用 '/'，GitHub Pages 构建用仓库名
  base: command === 'build' ? '/resume-analyzer/' : '/',
}))
