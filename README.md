# 医疗评价论坛 RAG 系统

基于 Python 的医疗评价检索增强生成系统，支持语义搜索、混合检索和智能问答。

## 功能特性

- 🔍 **混合检索**: 向量检索 + 关键词检索
- ⏰ **时间衰减**: 新评价权重更高
- 🎯 **MMR重排序**: 减少结果冗余
- 💬 **智能问答**: 基于检索内容的RAG问答

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key
```

### 3. 下载 sqlite-vec 扩展

从 [sqlite-vec releases](https://github.com/asg017/sqlite-vec/releases) 下载适合你系统的扩展文件：

- Windows: `vec0.dll`
- Linux: `vec0.so`
- macOS: `vec0.dylib`

将文件放在项目根目录。

### 4. 初始化数据库

```bash
python scripts/init_db.py
```

### 5. 索引示例数据

```bash
python scripts/index_data.py
```

### 6. 运行演示

```bash
python scripts/demo.py
```

## 项目结构

```
medical_evaluation_system/
├── src/              # 核心代码
├── data/             # 数据文件
├── scripts/          # 脚本工具
└── medical_reviews.db  # SQLite数据库
```

## 技术栈

- **向量数据库**: sqlite-vec
- **嵌入模型**: OpenAI text-embedding-3-small
- **语言模型**: OpenAI GPT-4
- **全文搜索**: SQLite FTS5

OPENAI_API_KEY=sk-9639b0c9cc5d4a918ef7bfefee20bfda
WQ_API_KEY=RYrw15X94NUgOVm9YUUnKjmBjYvnrjcjRIFaYTVKUo4
DASHSCOPE_API_KEY=sk-9639b0c9cc5d4a918ef7bfefee20bfda
OPENAI_API_BASE=https://wanqing.streamlakeapi.com/api/gateway/v1/endpoints
EMBEDDING_MODEL=text-embedding-v4
LLM_MODEL=kat-coder-pro-v1
DATABASE_PATH=./medical_reviews.db
