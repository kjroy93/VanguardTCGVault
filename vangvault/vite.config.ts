import path from 'node:path'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),

    // 👇 plugin custom
    {
      name: 'save-booster-json',

      configureServer(server) {
        server.middlewares.use(async (req, res, next) => {
          try {
            const reqUrl = new URL(req.url || '', 'http://localhost')

            if (reqUrl.pathname === '/save-booster-json' && req.method === 'POST') {
              const filename = (reqUrl.searchParams.get('filename') || 'boosterSets.json').trim()

              const valid = /^[\w\-.]+\.json$/.test(filename)
              if (!valid) {
                res.statusCode = 400
                res.setHeader('Content-Type', 'application/json')
                res.end(JSON.stringify({ ok: false, error: 'Invalid filename' }))
                return
              }

              let body = ''
              for await (const chunk of req) body += chunk

              const outDir = path.resolve(__dirname, 'src', 'assets')
              await fs.promises.mkdir(outDir, { recursive: true })

              const outPath = path.join(outDir, filename)
              await fs.promises.writeFile(outPath, body, 'utf8')

              res.statusCode = 200
              res.setHeader('Content-Type', 'application/json')
              res.end(JSON.stringify({ ok: true, path: path.relative(__dirname, outPath) }))
              return
            }

          } catch (err: any) {
            res.statusCode = 500
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ ok: false, error: String(err) }))
            return
          }

          next()
        })
      }
    }
  ],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  server: {
    proxy: {
      '^/wiki-api': {
        target: 'https://cardfight.fandom.com',
        changeOrigin: true,
        secure: true,
        rewrite: (p) => p.replace(/^\/wiki-api/, '/api.php'),
      },
    },
  },
})