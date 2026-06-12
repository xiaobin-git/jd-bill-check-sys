<template>
  <div>
    <el-page-header @back="goBack" title="返回账单列表" :content="pageTitle" />
    <h2>账单明细</h2>
    <el-card style="margin-bottom: 20px">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap">
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap">
          <el-button type="primary" @click="showCreateDialog">添加</el-button>
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept=".csv,.xls,.xlsx"
            @change="handleUpload"
          >
            <el-button>导入文件</el-button>
          </el-upload>
          <el-button type="danger" :disabled="selectedItems.length === 0" @click="batchDeleteItems">批量删除</el-button>
        </div>
        <el-form :inline="true" :model="filters" style="margin-left: auto">
          <el-form-item label="订单号">
            <el-input v-model="filters.order_no" placeholder="输入订单号" clearable style="width: 180px" />
          </el-form-item>
          <el-form-item label="商品编号">
            <el-input v-model="filters.product_no" placeholder="输入商品编号" clearable style="width: 180px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applyFilters">查询</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-table :data="displayItems" style="width: 100%" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="order_no" label="订单号" width="170" show-overflow-tooltip />
      <el-table-column prop="order_time" label="下单时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.order_time) }}</template>
      </el-table-column>
      <el-table-column prop="product_no" label="商品编号" width="150" show-overflow-tooltip />
      <el-table-column prop="product_name" label="商品名称" show-overflow-tooltip />
      <el-table-column prop="fee_name" label="费用名称" width="150" show-overflow-tooltip />
      <el-table-column prop="direction" label="收支方向" width="100" />
      <el-table-column prop="fee_meaning" label="费用项含义" width="160" show-overflow-tooltip />
      <el-table-column prop="quantity" label="数量" width="80" />
      <el-table-column prop="settlement_amount" label="应结金额" width="120">
        <template #default="{ row }">¥{{ row.settlement_amount?.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteItem(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑明细' : '添加明细'" width="760px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="订单号">
          <el-input v-model="form.order_no" />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-input v-model="form.order_status" />
        </el-form-item>
        <el-form-item label="下单时间">
          <el-date-picker
            v-model="form.order_time"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择下单时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="商品编号">
          <el-input v-model="form.product_no" />
        </el-form-item>
        <el-form-item label="商品名称">
          <el-input v-model="form.product_name" />
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="form.quantity" style="width: 100%" />
        </el-form-item>
        <el-form-item label="扣点类型">
          <el-input v-model="form.commission_type" />
        </el-form-item>
        <el-form-item label="佣金比例">
          <el-input-number v-model="form.commission_rate" :precision="4" style="width: 100%" />
        </el-form-item>
        <el-form-item label="应结金额">
          <el-input-number v-model="form.settlement_amount" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="费用名称">
          <el-input v-model="form.fee_name" />
        </el-form-item>
        <el-form-item label="币种">
          <el-input v-model="form.currency" />
        </el-form-item>
        <el-form-item label="收支方向">
          <el-input v-model="form.direction" />
        </el-form-item>
        <el-form-item label="结算状态">
          <el-input v-model="form.settlement_status" />
        </el-form-item>
        <el-form-item label="费用项含义">
          <el-input v-model="form.fee_meaning" />
        </el-form-item>
        <el-form-item label="费用说明">
          <el-input v-model="form.fee_description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { jdBillApi } from '../api'

const router = useRouter()
const route = useRoute()
const billId = route.params.id
const bill = ref(null)
const items = ref([])
const selectedItems = ref([])
const dialogVisible = ref(false)
const editing = ref(false)
const filters = ref({ order_no: '', product_no: '' })
const appliedFilters = ref({ order_no: '', product_no: '' })
const createEmptyForm = () => ({
  order_no: '',
  order_status: '',
  order_time: '',
  product_no: '',
  product_name: '',
  quantity: 1,
  commission_type: '',
  commission_rate: 0,
  fee_name: '',
  settlement_amount: 0,
  currency: '',
  direction: '',
  settlement_status: '',
  fee_meaning: '',
  fee_description: ''
})
const form = ref(createEmptyForm())
const editingId = ref(null)
const pageTitle = computed(() => {
  if (!bill.value) {
    return `账单 #${billId}`
  }
  return `${bill.value.shop_name} ${bill.value.date_range}`
})
const displayItems = computed(() => {
  return items.value.filter((item) => {
    const matchOrder =
      !appliedFilters.value.order_no ||
      item.order_no?.toLowerCase().includes(appliedFilters.value.order_no.trim().toLowerCase())
    const matchProduct =
      !appliedFilters.value.product_no ||
      item.product_no?.toLowerCase().includes(appliedFilters.value.product_no.trim().toLowerCase())
    return matchOrder && matchProduct
  })
})

const goBack = () => {
  router.push('/jd-bills')
}

const loadBill = async () => {
  try {
    const res = await jdBillApi.getBill(billId)
    bill.value = res.data
  } catch (e) {
    ElMessage.error('账单信息加载失败')
  }
}

const loadItems = async () => {
  try {
    const res = await jdBillApi.getItems(billId)
    items.value = res.data
  } catch (e) {
    ElMessage.error('加载失败')
  }
}

const showCreateDialog = () => {
  editing.value = false
  form.value = createEmptyForm()
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  editing.value = true
  editingId.value = row.id
  form.value = {
    order_no: row.order_no,
    order_status: row.order_status || '',
    order_time: row.order_time || '',
    product_no: row.product_no || '',
    product_name: row.product_name,
    quantity: row.quantity || 1,
    commission_type: row.commission_type || '',
    commission_rate: row.commission_rate || 0,
    settlement_amount: row.settlement_amount || 0,
    fee_name: row.fee_name || '',
    currency: row.currency || '',
    direction: row.direction || '',
    settlement_status: row.settlement_status || '',
    fee_meaning: row.fee_meaning || '',
    fee_description: row.fee_description || ''
  }
  dialogVisible.value = true
}

const saveItem = async () => {
  try {
    if (editing.value) {
      await jdBillApi.updateItem(editingId.value, form.value)
    } else {
      await jdBillApi.createItem(billId, form.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadItems()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const formatDateTime = (value) => {
  if (!value) {
    return '-'
  }
  return new Date(value).toLocaleString()
}

const deleteItem = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除吗？', '提示', { type: 'warning' })
    await jdBillApi.deleteItem(id)
    ElMessage.success('删除成功')
    loadItems()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const batchDeleteItems = async () => {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedItems.value.length} 条明细吗？`, '提示', { type: 'warning' })
    await Promise.all(selectedItems.value.map((item) => jdBillApi.deleteItem(item.id)))
    ElMessage.success('批量删除成功')
    selectedItems.value = []
    loadItems()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleUpload = async (file) => {
  try {
    await jdBillApi.uploadItems(billId, file.raw)
    ElMessage.success('上传成功')
    loadItems()
    loadBill()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '上传失败')
  }
}

const applyFilters = () => {
  appliedFilters.value = {
    order_no: filters.value.order_no.trim(),
    product_no: filters.value.product_no.trim()
  }
}

const handleSelectionChange = (selection) => {
  selectedItems.value = selection
}

onMounted(() => {
  loadBill()
  loadItems()
})
</script>
