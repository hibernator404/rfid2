import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server:{
    host:'127.0.0.1' ,//ip地址
    port: 8089, // 设置服务启动端口号
    open: true, // 设置服务启动时是否自动打开浏览器
  }

})
