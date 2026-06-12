<template>
  <div>
    <h2>京东账单</h2>
    <el-card style="margin-bottom: 20px">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap">
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap">
          <el-button type="primary" @click="showCreateDialog">创建账单</el-button>
          <el-button type="danger" :disabled="selectedBills.length === 0" @click="batchDeleteBills">批量删除</el-button>
        </div>
        <el-form :inline="true" :model="filters" style="margin-left: auto">
          <el-form-item label="账单月份">
            <el-date-picker
              v-model="filters.date_range"
              type="month"
              value-format="YYYY-MM"
              format="YYYY-MM"
              placeholder="选择账单月份"
              clearable
              style="width: 160px"
            />
          </el-form-item>
          <el-form-item label="店铺名称">
            <el-autocomplete
              v-model="filters.shop_name"
              :fetch-suggestions="queryShopSuggestions"
              placeholder="输入店铺名称"
              clearable
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applyFilters">查询</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-table :data="bills" style="width: 100%" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="date_range" label="账单月份" />
      <el-table-column prop="shop_name" label="店铺名称" />
      <el-table-column prop="created_at" label="创建时间">
        <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
      </el-table-column>
      <el-table-column label="操作" width="280">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="goToDetail(row.id)">查看明细</el-button>
          <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteBill(row.id)">删除</el-button>
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
        @current-change="loadBills"
        @size-change="handlePageSizeChange"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑账单' : '创建账单'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="账单月份" prop="date_range">
          <el-date-picker
            v-model="form.date_range"
            type="month"
            value-format="YYYY-MM"
            format="YYYY-MM"
            placeholder="选择账单月份"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="店铺名称" prop="shop_name">
          <el-autocomplete
            v-model="form.shop_name"
            :fetch-suggestions="queryShopSuggestions"
            placeholder="输入或选择店铺名称"
            clearable
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBill">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { jdBillApi } from '../api'

const router = useRouter()
const bills = ref([])
const selectedBills = ref([])
const shopOptions = ref([])
const dialogVisible = ref(false)
const editing = ref(false)
const formRef = ref(null)
const form = ref({ date_range: '', shop_name: '' })
const filters = ref({ date_range: '', shop_name: '' })
const editingId = ref(null)
const pagination = ref({ page: 1, page_size: 20, total: 0 })
const rules = {
  date_range: [{ required: true, message: '请选择账单月份', trigger: 'change' }],
  shop_name: [{ required: true, message: '请输入店铺名称', trigger: 'blur' }]
}

const loadBills = async () => {
  try {
    const res = await jdBillApi.getBills({
      page: pagination.value.page,
      page_size: pagination.value.page_size,
      date_range: filters.value.date_range || undefined,
      shop_name: filters.value.shop_name.trim() || undefined
    })
    bills.value = res.data.items
    pagination.value.total = res.data.total
  } catch (e) {
    ElMessage.error('加载失败')
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

const showCreateDialog = () => {
  editing.value = false
  editingId.value = null
  form.value = { date_range: '', shop_name: '' }
  formRef.value?.resetFields()
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  editing.value = true
  editingId.value = row.id
  form.value = { date_range: row.date_range, shop_name: row.shop_name }
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

const saveBill = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) {
    return
  }

  const payload = {
    date_range: form.value.date_range,
    shop_name: form.value.shop_name.trim()
  }

  try {
    if (editing.value) {
      await jdBillApi.updateBill(editingId.value, payload)
    } else {
      await jdBillApi.createBill(payload)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadBills()
    loadShopOptions()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteBill = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除吗？', '提示', { type: 'warning' })
    await jdBillApi.deleteBill(id)
    ElMessage.success('删除成功')
    loadBills()
    loadShopOptions()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const batchDeleteBills = async () => {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedBills.value.length} 条账单吗？`, '提示', { type: 'warning' })
    await Promise.all(selectedBills.value.map((item) => jdBillApi.deleteBill(item.id)))
    ElMessage.success('批量删除成功')
    selectedBills.value = []
    loadBills()
    loadShopOptions()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const queryShopSuggestions = (queryString, cb) => {
  const normalizedQuery = queryString.trim().toLowerCase()
  const results = shopOptions.value
    .filter((shop) => !normalizedQuery || shop.toLowerCase().includes(normalizedQuery))
    .map((shop) => ({ value: shop }))
  cb(results)
}

const applyFilters = () => {
  pagination.value.page = 1
  loadBills()
}

const handleSelectionChange = (selection) => {
  selectedBills.value = selection
}

const goToDetail = (id) => {
  router.push(`/jd-bills/${id}`)
}

const handlePageSizeChange = () => {
  pagination.value.page = 1
  loadBills()
}

onMounted(() => {
  loadBills()
  loadShopOptions()
})
</script>
