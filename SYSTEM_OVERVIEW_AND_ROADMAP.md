# RAG 系统总结与后续迭代计划

本文档用于快速理解当前 RAG 系统的端到端链路，并规划后续支持 TXT、PDF 文档和前端页面的迭代路线。

---

## 1. 当前系统定位

当前项目是一个轻量级企业知识库 RAG 后端 MVP，核心目标是：

1. 上传知识文档。
2. 抽取文档文本。
3. 将文本切分为语义片段。
4. 为片段生成向量。
5. 将向量写入 FAISS，将文档、片段、问答历史写入 SQLite。
6. 用户提问时检索相关片段。
7. 将片段与问题组装成 Prompt，调用 OpenAI-compatible LLM 生成回答。
8. 返回答案、上下文片段和来源信息。

当前优先级是先把后端 RAG 主链路跑通，再扩展更多文件类型与前端体验。

---

## 2. 当前能力总结

### 2.1 已支持能力

- FastAPI 后端服务。
- Markdown、TXT、文本型 PDF 文档上传。
- 通过统一 Loader Registry 读取文档文本（当前已注册 Markdown、TXT、PDF Loader）。
- 段落感知的文本切分。
- SQLite 存储：
  - documents：文档记录。
  - chunks：切分后的文本片段。
  - chat_history：问答历史。
- SentenceTransformer 文本向量化。
- FAISS 向量索引。
- vector_metadata.json 维护向量索引与 chunk/document 的映射关系。
- 基于向量检索的问答。
- 返回答案、召回上下文和来源元数据。
- 支持删除文档，并重建剩余 FAISS 索引。

### 2.2 当前接口

| 接口 | 方法 | 作用 |
| --- | --- | --- |
| `/health` | GET | 服务健康检查 |
| `/documents/upload` | POST | 上传 Markdown/TXT/文本型 PDF 文档并入库 |
| `/documents` | GET | 查看已上传文档列表 |
| `/documents/{document_id}` | DELETE | 删除文档、片段与对应向量 |
| `/ask` | POST | 基于知识库提问 |

---

## 3. 当前系统架构

```text
用户 / curl / Postman / Swagger / 未来前端
        ↓
FastAPI API 层
        ↓
Document Service 文档服务
        ↓
Loader 文档加载器（当前：Markdown/TXT/PDF）
        ↓
Chunking 文本切分
        ↓
Embedding Service 向量化
        ↓
FAISS Vector Store + vector_metadata.json
        ↓
RAGService 问答编排
        ↓
Prompt Builder
        ↓
OpenAI-compatible LLM
        ↓
答案 + 上下文 + 来源
```

---

## 4. 核心模块说明

| 模块 | 当前职责 |
| --- | --- |
| `api.py` | 定义 FastAPI 路由、请求响应模型和接口入口 |
| `document_service.py` | 文档保存、调用统一 Loader、切分、入库、向量化、删除编排 |
| `loaders/loader_registry.py` | 根据文件扩展名选择对应 Loader |
| `loaders/markdown_loader.py` | Markdown 文件类型判断和文本读取 |
| `loaders/text_loader.py` | TXT 文件类型判断和文本读取 |
| `loaders/pdf_loader.py` | 文本型 PDF 文件类型判断和文本抽取 |
| `chunking.py` | 将长文本切分成适合检索的 chunk |
| `embedding_service.py` | 加载 SentenceTransformer 并生成文本向量 |
| `vector_store.py` | 维护 FAISS 索引和向量元数据 |
| `database.py` | 初始化 SQLite 表结构和提供 CRUD 方法 |
| `rag_service.py` | 提问、检索、组装 Prompt、调用 LLM、记录历史 |
| `prompt_builder.py` | 构造限制模型基于知识回答的 Prompt |
| `llm.py` | OpenAI-compatible LLM 客户端封装 |
| `schemas.py` | RAG 响应数据结构 |

---

## 5. 当前端到端流程

### 5.1 文档上传入库流程

```text
POST /documents/upload
↓
校验文件名与文件类型
↓
保存原始上传文件到 storage/uploads/
↓
loader_registry 选择 Loader 并读取文本
↓
chunk_text 切分文本
↓
写入 documents 与 chunks 表
↓
embed_texts 批量生成 chunk 向量
↓
add_vectors 写入 FAISS 与 vector_metadata.json
↓
回写 chunks.embedding_ref
↓
更新文档状态为 completed
↓
返回 document_id、filename、file_type、chunk_count
```

### 5.2 用户提问流程

```text
POST /ask
↓
embed_text 将问题向量化
↓
vector_store.search 在 FAISS 中检索 Top-K chunk
↓
通过 chunk_id 查询 SQLite 中的 chunk 文本与文档信息
↓
build_prompt 将上下文和问题组装成 Prompt
↓
generate_answer 调用 LLM
↓
写入 chat_history
↓
返回 answer、contexts、sources
```

---

## 6. 当前系统边界与风险

1. **文件格式仍需继续扩展**：目前已支持 Markdown、TXT、文本型 PDF；还不支持扫描版 PDF OCR、DOCX、HTML 等知识文档。
2. **配置安全性不足**：API Key 仍在 `config.py` 中，应迁移到环境变量或 `.env`。
3. **缺少自动化测试**：上传、切分、向量写入、检索、删除等主流程需要测试覆盖。
4. **检索策略较基础**：当前使用 FAISS L2 Top-K 检索，还没有相似度阈值、重排序、混合检索或多路召回。
5. **Chunk 策略较简单**：按段落和长度切分，后续可针对通信手册、告警 SOP、表格内容做结构化切分。
6. **前端尚未实现**：目前主要依赖 curl、Postman 或 Swagger UI 测试。
7. **运行时存储为本地文件**：适合 MVP，不适合多人协作和生产级高并发。

---

## 7. 后续迭代路线

建议按“先文档类型、再质量评估、再前端体验、最后生产化”的顺序推进。

### 7.1 迭代一：统一文档 Loader 架构

状态：已完成基础版。当前已有 `loaders/loader_registry.py`，文档服务已通过统一入口选择 Loader，Markdown Loader 已适配 `supports` / `load_text` 接口。

目标：为 TXT、PDF、DOCX 等扩展做准备，避免每增加一种文件类型都修改大量业务逻辑。

建议改造：

1. 已新增统一 Loader 接口，例如：

```python
def supports(filename: str) -> bool:
    ...


def load_text(file_path: str) -> str:
    ...
```

2. 已新增 `loaders/loader_registry.py`：
   - 根据文件扩展名选择对应 loader。
   - 文档服务只调用统一的 `load_document_text(file_path)`。

3. 已将文档服务主流程升级为更通用的：
   - `ingest_document_file`
   - `ingest_document_upload`

原有 `ingest_markdown_file` / `ingest_markdown_upload` 已保留为兼容入口。

验收标准：

- Markdown 原有上传流程不受影响。
- 新增格式只需要新增 loader 并注册。
- API 层不需要为每种文件类型新增单独上传接口。

### 7.2 迭代二：增加 TXT 文档支持

状态：已完成基础版。当前已新增 `loaders/text_loader.py`，支持 `.txt` UTF-8 文本读取。

目标：快速支持最简单的纯文本知识库导入。

建议实现：

1. 已新增 `loaders/text_loader.py`。
2. 已支持扩展名：`.txt`。
3. 当前优先使用 UTF-8 读取。
4. 如果后续有中文 Windows 文档，可再增加编码检测，例如 `charset-normalizer`。
5. 上传响应的 `file_type` 返回 `text`。

验收标准：

- 上传 `.txt` 文件成功。
- documents 表中 file_type 为 `text`。
- chunks 表中能看到切分后的文本。
- `/ask` 可以从 TXT 内容中召回答案。
- 删除 TXT 文档后，对应向量也被移除。

### 7.3 迭代三：增加 PDF 文档支持

状态：已完成基础版。当前已新增 `loaders/pdf_loader.py`，支持通过 `pypdf` 抽取文本型 PDF，并对扫描版 PDF 返回明确错误。

目标：支持企业手册、设备说明书、告警处理手册等常见 PDF 知识文档。

建议实现：

1. 已新增轻量 PDF 解析依赖 `pypdf`，适合普通文本型 PDF。
2. 已新增 `loaders/pdf_loader.py`。
3. 已支持扩展名：`.pdf`。
4. 当前在抽取文本中保留 `[Page N]` 标记；后续如需更强来源定位，再扩展 chunk metadata。
5. 对扫描版 PDF，暂不强行支持 OCR，后续单独做 OCR 迭代。

建议的 PDF metadata：

```json
{
  "document_id": "...",
  "chunk_id": "...",
  "filename": "manual.pdf",
  "page_start": 3,
  "page_end": 4
}
```

验收标准：

- 上传文本型 PDF 成功。
- 能检索 PDF 内容。
- sources 中最好能展示文件名和页码。
- 对无法抽取文字的扫描 PDF，返回清晰错误提示：需要 OCR 或该 PDF 暂不支持。

### 7.4 迭代四：增强数据库与元数据模型

目标：支撑多格式文件、页码、标题、来源定位、前端展示。

建议扩展 chunks 表字段：

- `source_type`：markdown/text/pdf/docx。
- `page_start` / `page_end`：PDF 页码。
- `section_title`：章节标题。
- `token_count`：chunk token 数。
- `metadata_json`：保留格式特有元数据。

建议扩展 documents 表字段：

- `stored_path`：上传后文件路径。
- `file_size`：文件大小。
- `content_hash`：用于去重。
- `error_message`：失败原因。

### 7.5 迭代五：检索与回答质量优化

目标：减少答非所问，提高来源可信度。

可选优化：

1. 增加相似度阈值，距离过远时返回“知识库未找到”。
2. 将 `TOP_K` 改为接口参数或配置项。
3. 增加 reranker 对 Top-K 结果重排序。
4. 增加关键词检索，与向量检索做混合召回。
5. Prompt 中要求模型引用来源编号。
6. 前端展示“答案依据来自哪些文件/页码/片段”。

### 7.6 迭代六：增加前端

目标：让普通用户可以通过浏览器管理知识库并进行问答。

建议先做两个页面：

#### 知识库管理页

核心功能：

- 上传文档（Markdown/TXT/PDF）。
- 查看文档列表。
- 展示文档状态：processing/completed/failed。
- 展示 chunk 数量、上传时间、文件类型。
- 删除文档。
- 失败时展示错误原因。

#### Chat 问答页

核心功能：

- 输入问题。
- 展示模型回答。
- 展示引用来源：文件名、chunk、页码或章节。
- 展开查看召回上下文。
- 显示加载状态和错误状态。

建议技术栈：

- React + Vite。
- TypeScript。
- Tailwind CSS 或普通 CSS Modules。
- fetch/axios 调用 FastAPI。

前端目录建议：

```text
frontend/
├── src/
│   ├── api/
│   │   └── client.ts
│   ├── components/
│   │   ├── DocumentUploader.tsx
│   │   ├── DocumentList.tsx
│   │   ├── ChatBox.tsx
│   │   └── SourceList.tsx
│   ├── pages/
│   │   ├── KnowledgePage.tsx
│   │   └── ChatPage.tsx
│   └── App.tsx
└── package.json
```

### 7.7 迭代七：生产化与部署

目标：让系统从本地 MVP 走向稳定可部署版本。

建议事项：

1. 将 API Key、Base URL、模型名迁移到环境变量。
2. 增加 `.env.example`。
3. 增加 Dockerfile 与 docker-compose。
4. 增加日志系统，替换直接 `print`。
5. 增加上传文件大小限制。
6. 增加文档去重。
7. 增加用户认证。
8. 支持异步入库任务，避免大 PDF 上传时阻塞请求。
9. 为 SQLite/FAISS 抽象存储接口，后续可迁移 PostgreSQL、Milvus、Qdrant 或 pgvector。

---

## 8. 推荐近期开发顺序

如果只规划接下来 3 个小版本，建议如下：

### v0.2：多格式文档基础

- 抽象 Loader Registry。
- 保持 Markdown 可用。
- 新增 TXT Loader。
- 新增基础测试。

### v0.3：PDF 知识库

- 新增 PDF Loader。
- 增加页码 metadata。
- 优化 chunks/sources 返回结构。
- 增加 PDF 上传与检索测试。

### v0.4：前端 MVP

- React + Vite 初始化。
- 知识库管理页。
- Chat 问答页。
- 来源展示与上下文展开。

---

## 9. 建议优先完成的任务清单

1. 迁移密钥配置到环境变量。
2. 增加 pytest 测试覆盖上传、删除和问答基础流程。
3. 增加前端知识库管理页。
4. 增加前端 Chat 页。
5. 优化 Prompt 和来源展示。
6. 增加日志、错误信息和运行文档。

---

## 10. 一句话总结

当前系统已经具备 RAG MVP 的完整后端闭环：上传 Markdown/TXT/文本型 PDF、切分、向量化、入库、检索、调用 LLM 回答；下一阶段应在不增加过多复杂性的前提下，优先补少量测试，然后实现前端知识库管理和 Chat 问答页面。
