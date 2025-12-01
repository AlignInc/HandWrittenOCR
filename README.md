# HandWritten OCR Web Application

一個全功能的手寫表格 OCR 識別系統，支持中文手寫申請表的自動識別、結構化數據提取和導出。

## ✨ 功能特性

- 📤 **多圖片上傳**：支持拖拽、相機拍照，可批量上傳
- 🤖 **智能識別**：PaddleOCR + 可選 GPT-4 Vision 雙引擎
- 📝 **在線編輯**：可編輯的字段表格，實時預覽
- 📊 **多格式導出**：CSV / Markdown 格式，自動保存到服務器
- 📱 **響應式設計**：完美支持手機和電腦端
- 🎨 **現代化 UI**：TailwindCSS + Glassmorphism + 流暢動畫

## 🏗️ 技術棧

### 後端

- **FastAPI** - 現代化 Python web 框架
- **PaddleOCR** - 中文 OCR 識別引擎
- **OpenAI GPT-4 Vision** - 可選的智能字段提取
- **Redis + RQ** - 異步任務隊列
- **SQLAlchemy + SQLite** - 數據庫 ORM

### 前端

- **React 18** - UI 框架
- **Vite** - 快速開發構建工具
- **TailwindCSS** - 原子化 CSS
- **React Router** - 路由管理
- **Axios** - HTTP 客戶端

## 📋 環境要求

- Python 3.9+
- Node.js 20.9+
- Redis (可選，用於異步處理)

## 🚀 快速開始

### 1. 克隆項目

```bash
cd /Users/aaron/Downloads/HandWrittenOCR
```

### 2. 後端設置

```bash
cd backend

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 配置環境變量
cp .env.example .env
# 編輯 .env 文件，填入 OpenAI API Key（可選）

# 初始化數據庫
python -c "from database import init_db; init_db()"
```

### 3. 前端設置

```bash
cd frontend

# 安裝依賴
npm install

# 或使用 pnpm/yarn
# pnpm install
# yarn install
```

### 4. 啟動服務

**終端 1 - 後端 API 服務器：**

```bash
cd backend
source venv/bin/activate
python main.py
```

訪問: <http://localhost:8000>
API 文檔: <http://localhost:8000/docs>

**終端 2 - RQ Worker（處理 OCR 任務）：**

```bash
# 確保 Redis 運行中
redis-server

# 啟動 worker
cd backend
source venv/bin/activate
python worker.py
```

**終端 3 - 前端開發服務器：**

```bash
cd frontend
npm run dev
```

訪問: <http://localhost:5173>

## 📁 項目結構

```
HandWrittenOCR/
├── backend/
│   ├── api/                 # API 路由
│   │   └── batches.py      # 批次處理端點
│   ├── ocr/                # OCR 處理
│   │   ├── processor.py    # OCR 引擎
│   │   └── templates.py    # 表格模板
│   ├── exporters/          # 導出功能
│   │   ├── csv_exporter.py
│   │   └── markdown_exporter.py
│   ├── workers/            # 異步任務
│   │   └── batch_processor.py
│   ├── main.py             # FastAPI 應用
│   ├── models.py           # 數據庫模型
│   ├── schemas.py          # Pydantic 模式
│   ├── database.py         # 數據庫配置
│   ├── config.py           # 配置管理
│   └── worker.py           # RQ Worker 腳本
├── frontend/
│   ├── src/
│   │   ├── components/     # React 組件
│   │   │   ├── UploadZone.jsx
│   │   │   ├── ResultsView.jsx
│   │   │   ├── FieldEditor.jsx
│   │   │   └── MarkdownPreview.jsx
│   │   ├── App.jsx         # 主應用
│   │   ├── main.jsx        # 入口文件
│   │   ├── api.js          # API 客戶端
│   │   └── index.css       # 全局樣式
│   └── package.json
└── Sample/                 # 示例表格
    ├── 10K Form/
    └── Mgt Book/
```

## 🔧 配置說明

### 後端環境變量 (.env)

```env
# 數據庫
DATABASE_URL=sqlite:///./ocr_app.db

# Redis
REDIS_URL=redis://localhost:6379/0

# 文件存儲
UPLOAD_DIR=./uploads
EXPORT_DIR=./data/exports

# OpenAI（可選 - 用於 GPT-4 Vision 增強識別）
OPENAI_API_KEY=your_api_key_here
USE_GPT_VISION=true

# OCR 設置
OCR_LANGUAGE=ch
```

### 表格類型

目前支持的表格模板：

- **GCCF_10K** - GCCF 10K 申請表
- **MGT_BOOK** - 管理記錄簿

可在 `backend/ocr/templates.py` 中添加新模板。

## 📖 API 文檔

### 上傳批次

```http
POST /api/batches?form_type=GCCF_10K
Content-Type: multipart/form-data

images: File[]
```

### 獲取批次狀態

```http
GET /api/batches/{batch_id}
```

### 更新批次數據

```http
PUT /api/batches/{batch_id}
Content-Type: application/json

{
  "data": {
    "applicant_name_en": "CHAN XX",
    ...
  }
}
```

### 導出批次

```http
GET /api/batches/{batch_id}/export?format=csv
GET /api/batches/{batch_id}/export?format=md
```

## 🎯 使用流程

1. **上傳表格**：在首頁選擇表格類型，上傳圖片（支持拖拽）
2. **等待處理**：系統自動進行 OCR 識別（實時狀態更新）
3. **查看結果**：查看識別的字段和置信度
4. **編輯修改**：在線編輯識別錯誤的字段
5. **導出數據**：導出為 CSV 或 Markdown 格式

## 🔍 OCR 處理流程

1. **圖片預處理**：去噪、增強對比度、二值化
2. **文本識別**：PaddleOCR 提取文本
3. **結構化提取**：
   - 優先級 1：GPT-4 Vision 智能識別（如啟用）
   - 優先級 2：模板規則匹配
4. **置信度計算**：每個字段附帶識別置信度
5. **保存結果**：存入數據庫，準備導出

## 🐛 常見問題

### PaddleOCR 安裝失敗

```bash
# macOS M1/M2 芯片可能需要
pip install paddlepaddle --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Redis 連接失敗

```bash
# 啟動 Redis
brew services start redis  # macOS
# 或
redis-server
```

### 前端代理錯誤

檢查 `vite.config.js` 中的代理配置是否指向正確的後端地址。

## 📝 開發提示

- 修改表格模板：編輯 `backend/ocr/templates.py`
- 調整 OCR 參數：編輯 `backend/ocr/processor.py`
- 自定義樣式：編輯 `frontend/src/index.css` 和 `tailwind.config.js`
- 添加新路由：編輯 `frontend/src/App.jsx`

## 🚢 生產部署

1. **後端**：

```bash
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **前端**：

```bash
cd frontend
npm run build
# 部署 dist/ 目錄到靜態服務器
```

3. **數據庫**：遷移到 PostgreSQL 以獲得更好性能

## 📄 許可證

MIT License

## 👥 貢獻

歡迎提交 Issue 和 Pull Request！
