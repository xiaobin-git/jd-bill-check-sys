<template>
  <div>
    <h2>利润仪表盘</h2>
    <el-card style="margin-bottom: 20px">
      <el-form :inline="true" :model="filters">
        <el-form-item label="店铺名称">
          <el-select v-model="filters.shop_name" placeholder="选择店铺名称" style="width: 220px">
            <el-option label="全部" value="全部" />
            <el-option
              v-for="item in shopOptions"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filters.date_range"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 320px"
          />
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
              <template #default="{ row }">{{ row.percent?.toFixed(3) }}%</template>
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
              <template #default="{ row }">{{ row.percent?.toFixed(3) }}%</template>
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
import { dashboardApi, jdBillApi } from '../api'

const filters = ref({ shop_name: '全部', date_range: [] })
const data = ref({})
const shopOptions = ref([])

const buildQueryParams = () => {
  const [startDate, endDate] = filters.value.date_range || []
  return {
    shop_name: filters.value.shop_name === '全部' ? undefined : filters.value.shop_name,
    start_date: startDate || undefined,
    end_date: endDate || undefined
  }
}

const loadShopOptions = async () => {
  try {
    const res = await jdBillApi.getShopNames()
    shopOptions.value = res.data || []
  } catch (e) {
    ElMessage.error('店铺名称加载失败')
  }
}

const loadData = async () => {
  try {
    const res = await dashboardApi.getProfit(buildQueryParams())
    data.value = res.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
}

const exportData = () => {
  dashboardApi.exportDetail(buildQueryParams())
}

onMounted(() => {
  loadShopOptions()
  loadData()
})
</script>
