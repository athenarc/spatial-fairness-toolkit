import { createRouter, createWebHistory } from 'vue-router'
import routes from './app.routes'

const router = createRouter({
  history: createWebHistory(),
  routes: routes,
})

export default router
