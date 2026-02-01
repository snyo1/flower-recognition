import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  base: './', // 使用相对路径，确保在任何域名下都能正常访问
  mode: 'production', // 强制使用生产模式
  plugins: [
    vue(),
    // 生产环境不加载开发工具
    process.env.NODE_ENV === 'development' ? vueDevTools() : null,
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // 使用默认的esbuild压缩，不需要安装terser
    minify: 'esbuild',
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    },
    hmr: {
      // 开发环境HMR配置
      protocol: 'ws',
      host: 'localhost',
    },
  },
})
