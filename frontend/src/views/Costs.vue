<template>
  <div>
    <h2>成本管理</h2>
    <el-card style="margin-bottom: 20px">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap">
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap">
          <el-button type="primary" @click="showCreateDialog">添加成本</el-button>
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept=".csv,.xls,.xlsx"
            @change="handleUpload"
          >
            <el-button>上传文件</el-button>
          </el-upload>
          <el-button type="success" @click="syncCosts">从京东账单同步</el-button>
          <el-button type="danger" :disabled="selectedCosts.length === 0" @click="batchDeleteCosts">批量删除</el-button>
        </div>
        <el-form :inline="true" :model="filters" style="margin-left: auto">
          <el-form-item label="店铺名称">
            <el-input v-model="filters.shop_name" placeholder="输入店铺名称" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadCosts">查询</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-table :data="costs" style="width: 100%" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="shop_name" label="店铺名称" width="150" />
      <el-table-column prop="sku" label="SKU" width="150" />
      <el-table-column prop="product_name" label="商品名称" show-overflow-tooltip />
      <el-table-column prop="cost" label="成本" width="120">
        <template #default="{ row }">¥{{ row.cost?.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteCost(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑成本' : '添加成本'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="店铺名称">
          <el-input v-model="form.shop_name" />
        </el-form-item>
        <el-form-item label="SKU">
          <el-input v-model="form.sku" />
        </el-form-item>
        <el-form-item label="商品名称">
          <el-input v-model="form.product_name" />
        </el-form-item>
        <el-form-item label="成本">
          <el-input-number v-model="form.cost" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCost">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { costApi } from '../api'

const costs = ref([])
const selectedCosts = ref([])
const filters = ref({ shop_name: '' })
const dialogVisible = ref(false)
const editing = ref(false)
const form = ref({ shop_name: '', sku: '', product_name: '', cost: 0 })
const editingId = ref(null)

const loadCosts = async () => {
  try {
    const res = await costApi.getCosts(filters.value)
    costs.value = res.data
  } catch (e) {
    ElMessage.error('加载失败')
  }
}

const showCreateDialog = () => {
  editing.value = false
  form.value = { shop_name: '', sku: '', product_name: '', cost: 0 }
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  editing.value = true
  editingId.value = row.id
  form.value = {
    shop_name: row.shop_name,
    sku: row.sku,
    product_name: row.product_name,
    cost: row.cost || 0
  }
  dialogVisible.value = true
}

const saveCost = async () => {
  try {
    if (editing.value) {
      await costApi.updateCost(editingId.value, form.value)
    } else {
      await costApi.createCost(form.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadCosts()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteCost = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除吗？', '提示', { type: 'warning' })
    await costApi.deleteCost(id)
    ElMessage.success('删除成功')
    loadCosts()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const batchDeleteCosts = async () => {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedCosts.value.length} 条成本数据吗？`, '提示', { type: 'warning' })
    await Promise.all(selectedCosts.value.map((item) => costApi.deleteCost(item.id)))
    ElMessage.success('批量删除成功')
    selectedCosts.value = []
    loadCosts()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleUpload = async (file) => {
  try {
    await costApi.uploadCosts(file.raw)
    ElMessage.success('上传成功')
    loadCosts()
  } catch (e) {
    ElMessage.error('上传失败')
  }
}

const handleSelectionChange = (selection) => {
  selectedCosts.value = selection
}

const syncCosts = async () => {
  try {
    const res = await costApi.syncCosts(filters.value.shop_name)
    ElMessage.success(res.data.message)
    loadCosts()
  } catch (e) {
    ElMessage.error('同步失败')
  }
}

onMounted(() => {
  loadCosts()
})
</script>
