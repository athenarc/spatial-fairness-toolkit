// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import history from 'connect-history-api-fallback'
import type { Connect } from 'vite'

export default defineConfig({
  plugins: [
    vue(),
    {
      name: 'spa-fallback',
      configureServer(server) {
        server.middlewares.use(
          history({
            disableDotRule: true,
            htmlAcceptHeaders: ['text/html', 'application/xhtml+xml'],
          }) as Connect.NextHandleFunction // 👈 cast to fix TS type mismatch
        )
      },
    },
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
