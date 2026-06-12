# 京东账单核对系统

一个用于核对京东POP商家账单的全栈应用。

## 技术栈

### 后端
- FastAPI - Web框架
- SQLAlchemy - ORM
- SQLite - 数据库
- Pandas - 数据处理

### 前端
- Vue 3 - 前端框架
- Vite - 构建工具
- Element Plus - UI组件库
- Vue Router - 路由
- Axios - HTTP客户端

## 项目结构

```
jd-bill-check-sys/
├── backend/           # 后端代码
│   ├── app/
│   │   ├── api/      # API路由
│   │   ├── core/     # 核心配置
│   │   ├── models/   # 数据模型
│   │   ├── schemas/  # Pydantic模型
│   │   ├── services/ # 业务逻辑
│   │   └── utils/    # 工具类
│   └── main.py
├── frontend/         # 前端代码
│   └── src/
│       ├── api/      # API调用
│       ├── views/    # 页面组件
│       └── router/   # 路由
└── data/             # 数据存储
```

## 功能模块

1. **仪表盘** - 利润统计、收入支出明细、导出明细
2. **京东账单** - 创建账单、上传CSV、管理明细
3. **ERP订单** - 导入ERP订单、手动管理
4. **快递账单** - 导入快递对账表、管理运费
5. **成本管理** - 从京东账单同步SKU、设置商品成本

## 启动方式

### 1. 安装后端依赖

```bash
# 进入后端目录
cd backend

# 激活虚拟环境
..\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
# 在backend目录下
python main.py
```

后端服务将在 http://localhost:8000 启动

### 3. 安装前端依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 4. 启动前端服务

```bash
# 在frontend目录下
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 使用说明

### 京东账单CSV格式

上传的CSV文件应包含以下字段（列名需匹配）：
- 订单编号
- 订单状态
- 订单下单时间
- 商品编号
- 商品名称
- 商品数量
- 扣点类型
- 佣金比例
- 费用名称
- 应结金额
- 币种
- 收支方向
- 结算状态
- 费用项含义
- 费用说明

### ERP订单CSV格式

- 京东系统订单号 / jd_order_no / order_no
- 店铺名称 / shop_name
- 快递单号 / express_no

### 快递账单CSV格式

- 快递单号 / express_no
- 收货地址 / address
- 重量 / weight
- 运费 / freight
- 承运商 / carrier

### 成本CSV格式

- 店铺名称 / shop_name
- sku / SKU / 商品编号
- 商品名称 / product_name
- 成本 / cost
