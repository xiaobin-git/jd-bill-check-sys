<template>
  <div>
    <h2>快递账单</h2>
    <el-card style="margin-bottom: 20px">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap">
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap">
          <el-button type="primary" @click="showCreateDialog">添加账单</el-button>
          <el-button @click="openImportDialog">导入文件</el-button>
          <el-button @click="openFieldMappingDialog">字段匹配</el-button>
          <el-button type="danger" :disabled="selectedBills.length === 0" @click="batchDeleteBills">批量删除</el-button>
        </div>
        <el-form :inline="true" :model="filters" style="margin-left: auto">
          <el-form-item label="承运商">
          <el-select
              v-model="filters.carrier"
            filterable
            allow-create
            default-first-option
              placeholder="输入承运商"
              clearable
              style="width: 180px"
          >
            <el-option
              v-for="carrier in filteredCarrierOptions(filters.carrier)"
              :key="carrier"
              :label="carrier"
              :value="carrier"
            />
          </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applyFilters">查询</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <el-table :data="bills" style="width: 100%" stripe @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="express_no" label="快递单号" width="180" show-overflow-tooltip />
      <el-table-column prop="address" label="收货地址" min-width="180" show-overflow-tooltip />
      <el-table-column prop="created_time" label="创建时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.created_time) }}</template>
      </el-table-column>
      <el-table-column prop="weight" label="重量" width="100" />
      <el-table-column prop="volume" label="体积" width="100" />
      <el-table-column prop="freight" label="运费" width="100">
        <template #default="{ row }">{{ formatCurrency(row.freight) }}</template>
      </el-table-column>
      <el-table-column prop="carrier" label="承运商" width="120" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
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

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑账单' : '添加账单'" width="560px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="承运商">
          <el-select
            v-model="form.carrier"
            filterable
            allow-create
            default-first-option
            placeholder="输入承运商"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="carrier in filteredCarrierOptions(form.carrier)"
              :key="carrier"
              :label="carrier"
              :value="carrier"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="快递单号">
          <el-input v-model="form.express_no" />
        </el-form-item>
        <el-form-item label="收货地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="form.created_time"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择创建时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="重量">
          <el-input-number v-model="form.weight" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="体积">
          <el-input-number v-model="form.volume" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="运费">
          <el-input-number v-model="form.freight" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBill">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" title="导入快递账单" width="560px">
      <el-form :model="importForm" label-width="100px">
        <el-form-item label="承运商">
          <el-select
            v-model="importForm.carrier"
            filterable
            allow-create
            default-first-option
            placeholder="输入承运商名称"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="carrier in filteredCarrierOptions(importForm.carrier)"
              :key="carrier"
              :label="carrier"
              :value="carrier"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="导入文件">
          <el-upload
            :auto-upload="false"
            :show-file-list="true"
            :limit="1"
            accept=".csv,.xls,.xlsx"
            @change="handleImportFileChange"
            @remove="handleImportFileRemove"
          >
            <el-button>选择文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitImport">确认导入</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="manualMappingDialogVisible" title="手动匹配字段" width="860px">
      <div style="display: flex; gap: 16px; min-height: 360px">
        <div style="width: 220px; border-right: 1px solid #ebeef5; padding-right: 16px">
          <div
            v-for="field in mappingSystemFields"
            :key="field.key"
            @click="selectedSystemFieldKey = field.key"
            style="padding: 10px; margin-bottom: 8px; cursor: pointer; border-radius: 4px"
            :style="selectedSystemFieldKey === field.key ? 'background:#ecf5ff;color:#409eff' : 'background:#f5f7fa'"
          >
            <div>{{ field.label }}</div>
            <div style="font-size: 12px; color: #909399; margin-top: 4px">
              {{ manualMapping[field.key] || '未匹配' }}
            </div>
          </div>
        </div>
        <div style="flex: 1">
          <div style="margin-bottom: 12px; font-weight: 600">
            请选择“{{ currentSystemFieldLabel }}”对应的上传字段
          </div>
          <el-radio-group v-model="manualMapping[selectedSystemFieldKey]" style="display: flex; flex-direction: column; gap: 10px">
            <el-radio
              v-for="column in importSourceColumns"
              :key="column"
              :label="column"
              :disabled="isColumnDisabled(column)"
            >
              {{ column }}
            </el-radio>
          </el-radio-group>
        </div>
      </div>
      <template #footer>
        <el-button @click="manualMappingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmManualMapping">确认导入</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="fieldMappingDialogVisible" title="字段匹配" width="860px">
      <div style="display: flex; gap: 16px; min-height: 360px">
        <div style="width: 220px; border-right: 1px solid #ebeef5; padding-right: 16px">
          <div
            v-for="field in fieldMappings"
            :key="field.key"
            @click="selectedAliasFieldKey = field.key"
            style="padding: 10px; margin-bottom: 8px; cursor: pointer; border-radius: 4px"
            :style="selectedAliasFieldKey === field.key ? 'background:#ecf5ff;color:#409eff' : 'background:#f5f7fa'"
          >
            {{ field.label }}
          </div>
        </div>
        <div style="flex: 1">
          <div style="margin-bottom: 12px; font-weight: 600">{{ currentAliasFieldLabel }} 已映射字段</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px">
            <el-tag
              v-for="alias in currentAliasList"
              :key="alias"
              closable
              @close="removeAlias(alias)"
            >
              {{ alias }}
            </el-tag>
          </div>
          <div style="display: flex; gap: 8px; align-items: center">
            <el-input v-model="newAlias" placeholder="输入新的上传字段名" />
            <el-button type="primary" @click="addAlias">添加</el-button>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="fieldMappingDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveFieldMappings">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { expressBillApi } from '../api'

const createEmptyForm = () => ({
  express_no: '',
  address: '',
  created_time: '',
  weight: 0,
  volume: 0,
  freight: 0,
  carrier: ''
})

const bills = ref([])
const selectedBills = ref([])
const carrierOptions = ref([])
const filters = ref({ carrier: '' })
const pagination = ref({ page: 1, page_size: 20, total: 0 })
const dialogVisible = ref(false)
const editing = ref(false)
const form = ref(createEmptyForm())
const editingId = ref(null)

const importDialogVisible = ref(false)
const importForm = ref({ carrier: '' })
const importFile = ref(null)
const importSourceColumns = ref([])
const mappingSystemFields = ref([])
const manualMappingDialogVisible = ref(false)
const manualMapping = ref({})
const selectedSystemFieldKey = ref('express_no')

const fieldMappingDialogVisible = ref(false)
const fieldMappings = ref([])
const selectedAliasFieldKey = ref('express_no')
const newAlias = ref('')

const currentSystemFieldLabel = computed(() => {
  return mappingSystemFields.value.find((item) => item.key === selectedSystemFieldKey.value)?.label || ''
})

const currentAliasFieldLabel = computed(() => {
  return fieldMappings.value.find((item) => item.key === selectedAliasFieldKey.value)?.label || ''
})

const currentAliasList = computed(() => {
  return fieldMappings.value.find((item) => item.key === selectedAliasFieldKey.value)?.aliases || []
})

const loadBills = async () => {
  try {
    const res = await expressBillApi.getBills({
      ...filters.value,
      page: pagination.value.page,
      page_size: pagination.value.page_size
    })
    bills.value = res.data.items
    pagination.value.total = res.data.total
  } catch (e) {
    ElMessage.error('加载失败')
  }
}

const loadCarriers = async () => {
  try {
    const res = await expressBillApi.getCarriers()
    carrierOptions.value = res.data || []
  } catch (e) {
    ElMessage.error('承运商加载失败')
  }
}

const loadFieldMappings = async () => {
  const res = await expressBillApi.getFieldMappings()
  fieldMappings.value = res.data.system_fields || []
  if (!selectedAliasFieldKey.value && fieldMappings.value.length > 0) {
    selectedAliasFieldKey.value = fieldMappings.value[0].key
  }
}

const filteredCarrierOptions = (keyword) => {
  const text = (keyword || '').trim().toLowerCase()
  return carrierOptions.value.filter((item) => !text || item.toLowerCase().includes(text))
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
    express_no: row.express_no,
    address: row.address || '',
    created_time: row.created_time || '',
    weight: row.weight || 0,
    volume: row.volume || 0,
    freight: row.freight || 0,
    carrier: row.carrier || ''
  }
  dialogVisible.value = true
}

const saveBill = async () => {
  try {
    const payload = { ...form.value, carrier: form.value.carrier?.trim() || '' }
    if (editing.value) {
      await expressBillApi.updateBill(editingId.value, payload)
    } else {
      await expressBillApi.createBill(payload)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadBills()
    loadCarriers()
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
    loadCarriers()
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
    loadCarriers()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('批量删除失败')
    }
  }
}

const openImportDialog = () => {
  importForm.value = { carrier: '' }
  importFile.value = null
  importDialogVisible.value = true
}

const handleImportFileChange = (file) => {
  importFile.value = file.raw
}

const handleImportFileRemove = () => {
  importFile.value = null
}

const submitImport = async () => {
  if (!importForm.value.carrier.trim()) {
    ElMessage.error('请输入承运商名称')
    return
  }
  if (!importFile.value) {
    ElMessage.error('请选择要导入的文件')
    return
  }
  await executeImport()
}

const executeImport = async (fieldMapping = null) => {
  try {
    const res = await expressBillApi.importBills({
      carrier: importForm.value.carrier.trim(),
      file: importFile.value,
      fieldMapping
    })
    if (res.data.status === 'need_mapping') {
      importSourceColumns.value = res.data.source_columns || []
      mappingSystemFields.value = res.data.system_fields || []
      manualMapping.value = { ...(res.data.resolved_mapping || {}) }
      selectedSystemFieldKey.value = res.data.missing_fields?.[0] || mappingSystemFields.value[0]?.key || 'express_no'
      manualMappingDialogVisible.value = true
      return
    }
    ElMessage.success(`导入成功，共导入 ${res.data.count} 条`)
    importDialogVisible.value = false
    manualMappingDialogVisible.value = false
    await loadBills()
    await loadCarriers()
    await loadFieldMappings()
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '导入失败')
  }
}

const isColumnDisabled = (column) => {
  return Object.entries(manualMapping.value).some(([key, value]) => key !== selectedSystemFieldKey.value && value === column)
}

const confirmManualMapping = async () => {
  const missing = mappingSystemFields.value.filter((field) => !manualMapping.value[field.key])
  if (missing.length > 0) {
    ElMessage.error('请先完成所有系统字段的匹配')
    return
  }
  await executeImport(manualMapping.value)
}

const openFieldMappingDialog = async () => {
  await loadFieldMappings()
  selectedAliasFieldKey.value = fieldMappings.value[0]?.key || 'express_no'
  newAlias.value = ''
  fieldMappingDialogVisible.value = true
}

const addAlias = () => {
  const value = newAlias.value.trim()
  if (!value) {
    ElMessage.error('请输入字段名')
    return
  }
  const target = fieldMappings.value.find((item) => item.key === selectedAliasFieldKey.value)
  if (!target) {
    return
  }
  if (!target.aliases.includes(value)) {
    target.aliases.push(value)
  }
  newAlias.value = ''
}

const removeAlias = (alias) => {
  const target = fieldMappings.value.find((item) => item.key === selectedAliasFieldKey.value)
  if (!target) {
    return
  }
  target.aliases = target.aliases.filter((item) => item !== alias)
}

const saveFieldMappings = async () => {
  try {
    const mappings = {}
    fieldMappings.value.forEach((item) => {
      mappings[item.key] = item.aliases
    })
    await expressBillApi.updateFieldMappings(mappings)
    ElMessage.success('保存成功')
    fieldMappingDialogVisible.value = false
    await loadFieldMappings()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const handleSelectionChange = (selection) => {
  selectedBills.value = selection
}

const applyFilters = () => {
  pagination.value.page = 1
  loadBills()
}

const handlePageSizeChange = () => {
  pagination.value.page = 1
  loadBills()
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

onMounted(async () => {
  await loadBills()
  await loadCarriers()
  await loadFieldMappings()
})
</script>
