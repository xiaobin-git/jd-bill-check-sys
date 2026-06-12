import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import JDBills from '../views/JDBills.vue'
import JDBillDetail from '../views/JDBillDetail.vue'
import ERPOrders from '../views/ERPOrders.vue'
import ExpressBills from '../views/ExpressBills.vue'
import Costs from '../views/Costs.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/jd-bills', component: JDBills },
  { path: '/jd-bills/:id', component: JDBillDetail },
  { path: '/erp-orders', component: ERPOrders },
  { path: '/express-bills', component: ExpressBills },
  { path: '/costs', component: Costs }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
