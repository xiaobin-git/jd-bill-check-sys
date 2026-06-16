<template>
  <el-container style="height: 100vh">
    <el-aside width="200px" style="background-color: #2c3e50; color: white">
      <div style="padding: 20px; text-align: center; font-size: 18px; font-weight: bold">
        账单系统
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#2c3e50"
        text-color="#fff"
        active-text-color="#ffd04b"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/jd-bills">
          <el-icon><Document /></el-icon>
          <span>京东账单</span>
        </el-menu-item>
        <el-menu-item index="/erp-orders">
          <el-icon><Tickets /></el-icon>
          <span>ERP订单</span>
        </el-menu-item>
        <el-menu-item index="/express-bills">
          <el-icon><Van /></el-icon>
          <span>快递账单</span>
        </el-menu-item>
        <el-menu-item index="/costs">
          <el-icon><Money /></el-icon>
          <span>商品成本</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { House, Document, Tickets, Van, Money } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
html, body, #app {
  height: 100%;
}
</style>
