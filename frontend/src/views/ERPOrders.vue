<template>
  <div>
    <h2>ERP订单</h2>
    <el-card style="margin-bottom: 20px">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap">
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap">
          <el-button type="primary" @click="showCreateDialog">添加订单</el-button>
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept=".csv,.xls,.xlsx"
            @change="handleUpload"
          >
            <el-button>上传文件</el-button>
          </el-upload>
          <el-button type="danger" :disabled="selectedOrders.length === 0" @click="batchDeleteOrders">批量删除</el-button>
        </div>
        <el-form :inline="true" :model="filters" style="margin-left: auto">
          <el-form-item label="店铺名称">
            <el-input v-model="filters.shop_name" placeholder="输入店铺名称" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applyFilters">查询</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-table :data="orders" style="width: 100%" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="shop_name" label="店铺" width="140" />
      <el-table-column prop="platform_type" label="平台类型" width="110" />
      <el-table-column prop="jd_order_no" label="平台订单号" width="180" show-overflow-tooltip />
      <el-table-column prop="express_no" label="快递单号" width="150" show-overflow-tooltip />
      <el-table-column prop="system_order_no" label="系统单号" width="150" show-overflow-tooltip />
      <el-table-column prop="order_status" label="订单状态" width="100" />
      <el-table-column prop="refund_status" label="退款状态" width="100" />
      <el-table-column prop="customer_note" label="客服备注" width="160" show-overflow-tooltip />
      <el-table-column prop="payment_time" label="付款时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.payment_time) }}</template>
      </el-table-column>
      <el-table-column prop="shipping_time" label="发货时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.shipping_time) }}</template>
      </el-table-column>
      <el-table-column prop="estimated_weight" label="预估总重量" width="110" />
      <el-table-column prop="actual_receipt" label="商家实收" width="110">
        <template #default="{ row }">{{ formatCurrency(row.actual_receipt) }}</template>
      </el-table-column>
      <el-table-column prop="express_company" label="快递公司" width="120" />
      <el-table-column prop="package_count" label="包裹个数" width="100" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteOrder(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="display: flex; justify-content: flex-end; margin-top: 16px">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        layout="total, sizes, prev, pager, next, jumper"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        @current-change="loadOrders"
        @size-change="handlePageSizeChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑订单' : '添加订单'" width="760px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="店铺">
          <el-input v-model="form.shop_name" />
        </el-form-item>
        <el-form-item label="平台类型">
          <el-input v-model="form.platform_type" />
        </el-form-item>
        <el-form-item label="平台订单号">
          <el-input v-model="form.jd_order_no" />
        </el-form-item>
        <el-form-item label="快递单号">
          <el-input v-model="form.express_no" />
        </el-form-item>
        <el-form-item label="系统单号">
          <el-input v-model="form.system_order_no" />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-input v-model="form.order_status" />
        </el-form-item>
        <el-form-item label="退款状态">
          <el-input v-model="form.refund_status" />
        </el-form-item>
        <el-form-item label="客服备注">
          <el-input v-model="form.customer_note" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="付款时间">
          <el-date-picker
            v-model="form.payment_time"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择付款时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="发货时间">
          <el-date-picker
            v-model="form.shipping_time"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择发货时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预估总重量">
          <el-input-number v-model="form.estimated_weight" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="商家实收">
          <el-input-number v-model="form.actual_receipt" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="快递公司">
          <el-input v-model="form.express_company" />
        </el-form-item>
        <el-form-item label="包裹个数">
          <el-input-number v-model="form.package_count" :precision="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveOrder">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { erpOrderApi } from '../api'

const createEmptyForm = () => ({
  shop_name: '',
  platform_type: '',
  jd_order_no: '',
  express_no: '',
  system_order_no: '',
  order_status: '',
  refund_status: '',
  customer_note: '',
  payment_time: '',
  shipping_time: '',
  estimated_weight: 0,
  actual_receipt: 0,
  express_company: '',
  package_count: 1
})

const orders = ref([])
const selectedOrders = ref([])
const filters = ref({ shop_name: '' })
const pagination = ref({ page: 1, page_size: 20, total: 0 })
const dialogVisible = ref(false)
const editing = ref(false)
const form = ref(createEmptyForm())
const editingId = ref(null)

const loadOrders = async () => {
  try {
    const res = await erpOrderApi.getOrders({
      ...filters.value,
      page: pagination.value.page,
      page_size: pagination.value.page_size
    })
    orders.value = res.data.items
    pagination.value.total = res.data.total
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
    shop_name: row.shop_name,
    platform_type: row.platform_type || '',
    jd_order_no: row.jd_order_no,
    express_no: row.express_no || '',
    system_order_no: row.system_order_no || '',
    order_status: row.order_status || '',
    refund_status: row.refund_status || '',
    customer_note: row.customer_note || '',
    payment_time: row.payment_time || '',
    shipping_time: row.shipping_time || '',
    estimated_weight: row.estimated_weight || 0,
    actual_receipt: row.actual_receipt || 0,
    express_company: row.express_company || '',
    package_count: row.package_count || 1
  }
  dialogVisible.value = true
}

const saveOrder = async () => {
  try {
    if (editing.value) {
      await erpOrderApi.updateOrder(editingId.value, form.value)
    } else {
      await erpOrderApi.createOrder(form.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadOrders()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteOrder = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除吗？', '提示', { type: 'warning' })
    await erpOrderApi.deleteOrder(id)
    ElMessage.success('删除成功')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const batchDeleteOrders = async () => {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedOrders.value.length} 条订单吗？`, '提示', { type: 'warning' })
    await Promise.all(selectedOrders.value.map((item) => erpOrderApi.deleteOrder(item.id)))
    ElMessage.success('批量删除成功')
    selectedOrders.value = []
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleUpload = async (file) => {
  try {
    await erpOrderApi.uploadOrders(file.raw)
    ElMessage.success('上传成功')
    pagination.value.page = 1
    loadOrders()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '上传失败')
  }
}

const formatDateTime = (value) => {
  if (!value) {
    return '-'
  }
  return new Date(value).toLocaleString()
}

const formatCurrency = (value) => {
  if (value === null || value === undefined || value === '') {
    return '-'
  }
  return `¥${Number(value).toFixed(2)}`
}

const handleSelectionChange = (selection) => {
  selectedOrders.value = selection
}

const applyFilters = () => {
  pagination.value.page = 1
  loadOrders()
}

const handlePageSizeChange = () => {
  pagination.value.page = 1
  loadOrders()
}

onMounted(() => {
  loadOrders()
})
</script>
