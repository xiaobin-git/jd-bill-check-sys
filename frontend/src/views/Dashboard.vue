<template>
  <div>
    <h2>利润仪表盘</h2>
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true" :model="filters">
        <el-form-item label="店铺名称">
          <el-input v-model="filters.shop_name" placeholder="输入店铺名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="exportData">导出明细</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover" style="text-align: center">
          <div style="font-size: 14px; color: #666; margin-bottom: 10px">利润</div>
          <div style="font-size: 28px; color: #67c23a; font-weight: bold">
            ¥{{ data.profit?.toFixed(2) || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" style="text-align: center">
          <div style="font-size: 14px; color: #666; margin-bottom: 10px">总收入</div>
          <div style="font-size: 28px; color: #409eff; font-weight: bold">
            ¥{{ data.total_income?.toFixed(2) || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" style="text-align: center">
          <div style="font-size: 14px; color: #666; margin-bottom: 10px">总支出</div>
          <div style="font-size: 28px; color: #f56c6c; font-weight: bold">
            ¥{{ data.total_expense?.toFixed(2) || 0 }}
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" style="text-align: center">
          <div style="font-size: 14px; color: #666; margin-bottom: 10px">订单数</div>
          <div style="font-size: 28px; color: #e6a23c; font-weight: bold">
            {{ data.order_count || 0 }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>收入明细</span>
            </div>
          </template>
          <el-table :data="data.income_detail || []" style="width: 100%">
            <el-table-column prop="name" label="项目" />
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">¥{{ row.amount?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="percent" label="占比">
              <template #default="{ row }">{{ row.percent?.toFixed(1) }}%</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>支出明细</span>
            </div>
          </template>
          <el-table :data="data.expense_detail || []" style="width: 100%">
            <el-table-column prop="name" label="项目" />
            <el-table-column prop="amount" label="金额">
              <template #default="{ row }">¥{{ row.amount?.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="percent" label="占比">
              <template #default="{ row }">{{ row.percent?.toFixed(1) }}%</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { dashboardApi } from '../api'

const filters = ref({ shop_name: '' })
const data = ref({})

const loadData = async () => {
  try {
    const res = await dashboardApi.getProfit(filters.value)
    data.value = res.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
}

const exportData = () => {
  dashboardApi.exportDetail(filters.value)
}

onMounted(() => {
  loadData()
})
</script>
