# 京东账单核对系统 - 设计文档

## 一、技术选型

### 前端技术栈
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios

### 后端技术栈
- **Web 框架**: FastAPI + Uvicorn
- **ORM**: SQLAlchemy 2.0
- **数据库**: SQLite
- **数据处理**: Pandas
- **数据验证**: Pydantic

---

## 二、项目目录结构

```
jd-bill-check-sys/
├── backend/                    # 后端目录
│   ├── app/
│   │   ├── api/                # 路由层
│   │   │   ├── __init__.py
│   │   │   ├── jd_bill.py      # 京东账单接口
│   │   │   ├── erp_order.py    # ERP订单接口
│   │   │   ├── express_bill.py # 快递账单接口
│   │   │   ├── cost.py         # 成本管理接口
│   │   │   └── dashboard.py    # 主页数据接口
│   │   ├── core/               # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py       # 配置管理
│   │   │   └── database.py     # 数据库连接
│   │   ├── models/             # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── jd_bill.py
│   │   │   ├── erp_order.py
│   │   │   ├── express_bill.py
│   │   │   └── cost.py
│   │   ├── schemas/            # Pydantic验证模型
│   │   │   ├── __init__.py
│   │   │   ├── jd_bill.py
│   │   │   ├── erp_order.py
│   │   │   ├── express_bill.py
│   │   │   └── cost.py
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── jd_bill_service.py
│   │   │   ├── erp_order_service.py
│   │   │   ├── express_bill_service.py
│   │   │   ├── cost_service.py
│   │   │   └── calculation_service.py  # 利润计算核心逻辑
│   │   └── utils/              # 工具类
│   │       ├── __init__.py
│   │       ├── csv_parser.py   # CSV解析器
│   │       └── exporter.py     # 数据导出工具
│   ├── main.py                 # 启动文件
│   └── requirements.txt
├── frontend/                   # 前端目录
│   ├── src/
│   │   ├── api/                # API调用
│   │   ├── components/         # 公共组件
│   │   ├── views/              # 页面视图
│   │   ├── stores/             # Pinia状态管理
│   │   ├── router/             # 路由
│   │   └── utils/              # 工具函数
│   └── package.json
└── data/                       # 数据存储
    └── db.sqlite
```

---

## 三、数据库设计

### 1. jd_bills（京东账单主表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| date_range | String | 账单日期区间 |
| shop_name | String | 店铺名称 |
| created_at | DateTime | 创建时间 |

### 2. jd_bill_items（京东账单明细表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| jd_bill_id | Integer | 外键关联jd_bills |
| order_no | String | 订单编号 |
| order_status | String | 订单状态 |
| order_time | DateTime | 订单下单时间 |
| product_no | String | 商品编号 |
| product_name | String | 商品名称 |
| quantity | Integer | 商品数量 |
| commission_type | String | 扣点类型 |
| commission_rate | Float | 佣金比例 |
| fee_name | String | 费用名称 |
| settlement_amount | Float | 应结金额 |
| currency | String | 币种 |
| direction | String | 收支方向 |
| settlement_status | String | 结算状态 |
| fee_meaning | String | 费用项含义 |
| fee_description | String | 费用说明 |

### 3. erp_orders（ERP订单表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| jd_order_no | String | 京东系统订单号 |
| shop_name | String | 店铺名称 |
| express_no | String | 快递单号 |
| created_at | DateTime | 创建时间 |

### 4. express_bills（快递账单表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| express_no | String | 快递单号 |
| address | String | 收货地址 |
| weight | Float | 重量 |
| freight | Float | 运费 |
| carrier | String | 承运商 |
| created_at | DateTime | 创建时间 |

### 5. costs（成本管理表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| shop_name | String | 店铺名称 |
| sku | String | 商品SKU |
| product_name | String | 商品名称 |
| cost | Float | 成本 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

---

## 四、模块功能设计

### 1. 京东账单模块
- 账单列表：创建、编辑、删除账单（选择日期区间、店铺名称）
- 账单明细：点击账单进入明细页面
- CSV导入：上传京东导出的CSV，自动解析指定字段
- 手动操作：支持手动添加、修改、删除明细数据

### 2. ERP订单模块
- 订单列表：展示所有ERP订单
- 数据导入：导入ERP系统导出的表格
- 手动操作：支持手动添加、修改、删除订单数据

### 3. 快递账单模块
- 账单列表：展示所有快递账单
- 数据导入：导入承运商对账表
- 手动操作：支持手动添加、修改、删除账单数据

### 4. 成本管理模块
- 自动同步：从京东账单提取SKU去重添加
- 成本编辑：手动编辑商品成本
- 批量导入：支持批量导入成本数据

### 5. 主页/仪表盘
- 筛选条件：店铺、日期区间
- 核心指标：利润、总收入、总支出、单量
- 收支明细：按金额从大到小排列，显示百分比
- 导出功能：导出包含订单号、快递单号、重量和各收支项目的明细表格

---

## 五、核心计算逻辑

### 利润计算流程
1. 数据关联：按订单号关联三表（京东账单 ↔ ERP订单 ↔ 快递账单）
2. 收入计算：京东账单应结金额
3. 支出计算：快递运费 + 商品成本
4. 利润计算：利润 = 收入 - 支出
5. 分类统计：按收支项目分类汇总

---

## 六、关键技术点

1. **CSV解析**: 使用Pandas读取，灵活处理不同格式
2. **数据关联**: 用Pandas的merge操作替代SQL join，更灵活
3. **异步处理**: FastAPI异步处理大文件上传
4. **数据导出**: 用openpyxl或xlsxwriter生成Excel
