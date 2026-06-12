<template>
  <div>
    <h2>快递账单</h2>
    <el-card style="margin-bottom: 20px">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap">
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap">
          <el-button type="primary" @click="showCreateDialog">添加账单</el-button>
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            accept=".csv,.xls,.xlsx"
            @change="handleUpload"
          >
            <el-button>上传文件</el-button>
          </el-upload>
          <el-button type="danger" :disabled="selectedBills.length === 0" @click="batchDeleteBills">批量删除</el-button>
        </div>
        <el-form :inline="true" :model="filters" style="margin-left: auto">
          <el-form-item label="承运商">
            <el-input v-model="filters.carrier" placeholder="输入承运商" clearable />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadBills">查询</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-table :data="bills" style="width: 100%" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="express_no" label="快递单号" width="180" />
      <el-table-column prop="address" label="收货地址" show-overflow-tooltip />
      <el-table-column prop="weight" label="重量" width="100" />
      <el-table-column prop="freight" label="运费" width="100">
        <template #default="{ row }">¥{{ row.freight?.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="carrier" label="承运商" width="120" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteBill(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑账单' : '添加账单'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="快递单号">
          <el-input v-model="form.express_no" />
        </el-form-item>
        <el-form-item label="收货地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="重量">
          <el-input-number v-model="form.weight" :precision="2" />
        </el-form-item>
        <el-form-item label="运费">
          <el-input-number v-model="form.freight" :precision="2" />
        </el-form-item>
        <el-form-item label="承运商">
          <el-input v-model="form.carrier" />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { expressBillApi } from '../api'

const bills = ref([])
const selectedBills = ref([])
const filters = ref({ carrier: '' })
const dialogVisible = ref(false)
const editing = ref(false)
const form = ref({ express_no: '', address: '', weight: 0, freight: 0, carrier: '' })
const editingId = ref(null)

const loadBills = async () => {
  try {
    const res = await expressBillApi.getBills(filters.value)
    bills.value = res.data
  } catch (e) {
    ElMessage.error('加载失败')
  }
}

const showCreateDialog = () => {
  editing.value = false
  form.value = { express_no: '', address: '', weight: 0, freight: 0, carrier: '' }
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  editing.value = true
  editingId.value = row.id
  form.value = {
    express_no: row.express_no,
    address: row.address,
    weight: row.weight || 0,
    freight: row.freight || 0,
    carrier: row.carrier
  }
  dialogVisible.value = true
}

const saveBill = async () => {
  try {
    if (editing.value) {
      await expressBillApi.updateBill(editingId.value, form.value)
    } else {
      await expressBillApi.createBill(form.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadBills()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteBill = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除吗？', '提示', { type: 'warning' })
    await expressBillApi.deleteBill(id)
    ElMessage.success('删除成功')
    loadBills()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const batchDeleteBills = async () => {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedBills.value.length} 条账单吗？`, '提示', { type: 'warning' })
    await Promise.all(selectedBills.value.map((item) => expressBillApi.deleteBill(item.id)))
    ElMessage.success('批量删除成功')
    selectedBills.value = []
    loadBills()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const handleUpload = async (file) => {
  try {
    await expressBillApi.uploadBills(file.raw)
    ElMessage.success('上传成功')
    loadBills()
  } catch (e) {
    ElMessage.error('上传失败')
  }
}

const handleSelectionChange = (selection) => {
  selectedBills.value = selection
}

onMounted(() => {
  loadBills()
})
</script>
