# 导师 RAG 优化建议落地计划

本文档将导师对当前 RAG 项目的优化建议整理成可执行的工程路线，目标是从“系统能跑通”升级到“系统效果可评估、过程可观测、架构可解释、参数可实验”。

---

## 1. 当前系统基线

当前项目已经具备 RAG MVP 的完整闭环：

```text
文档上传
→ Loader Registry 选择 Markdown / TXT / PDF Loader
→ 文本抽取
→ Chunking
→ Embedding
→ FAISS 向量写入
→ SQLite 记录文档 / Chunk / Chat History
→ 用户提问
→ 问题 Embedding
→ FAISS Top-K 检索
→ SQLite 回查 Chunk 文本与来源
→ Prompt 构建
→ LLM 生成回答
→ 前端展示 Answer / Sources / Contexts
```

当前系统的关键特点：

- 已支持 Markdown、TXT、文本型 PDF。
- 使用 SentenceTransformer 生成向量。
- 使用 FAISS 进行本地向量检索。
- 使用 SQLite 保存文档、Chunk、问答历史。
- 使用 React + Vite 前端完成上传、列表、删除和问答操作。

---

## 2. 优化方向总览

导师建议可以归纳为四个方向：

| 方向 | 目标 | 关键动作 |
| --- | --- | --- |
| 检索质量 | 让召回内容更准，减少无关上下文进入 Prompt | Rerank、跨文档测试集、Top-K 实验 |
| 数据管理 | 理解并增强向量存储能力 | 梳理 FAISS / SQLite 映射，调研 Qdrant、Milvus、pgvector |
| 工程能力 | 更容易定位问题和解释运行过程 | 日志、耗时统计、断点调试 |
| 系统灵活性 | 支持参数实验和前端交互配置 | 可配置 Top-K、Rerank 开关、阈值、Prompt、模型参数 |

推荐按照以下顺序推进：

```text
Step 1: 加日志与耗时统计
Step 2: 建立 10 条跨文档评测集
Step 3: 暴露 Top-K 等轻量参数
Step 4: 引入 Rerank 实验
Step 5: 深入向量存储并调研向量数据库
Step 6: 将实验参数接入前端
```

---

## 3. 方向一：引入 Rerank 模型

### 3.1 为什么需要 Rerank

当前 FAISS 检索主要依赖 query embedding 与 chunk embedding 的向量距离。它适合做第一阶段粗召回，但可能出现：

- 语义相近但实际不回答问题的 chunk 被召回。
- 多个相似文档中召回了错误版本。
- 用户问题需要精确匹配某个条件，但向量相似度不够细。
- Top-K 中混入无关 chunk，导致 Prompt 被噪声污染。

Rerank 的作用是在 FAISS 初筛之后，对“问题—候选 Chunk”做更精细的相关性打分。

### 3.2 推荐 Pipeline

```text
用户问题
→ embed_text(question)
→ FAISS 召回 Top-N，例如 10 条
→ Reranker 对 question + candidate_chunk 重新评分
→ 保留 Top-M，例如 3 条
→ build_prompt(contexts, question)
→ LLM 生成回答
```

### 3.3 建议的最小实现

为了不增加太多复杂性，可以先做一个可开关的 Rerank Service：

```text
rerank_service.py
├── rerank(question, candidates, top_n)
└── 返回按 rerank_score 排序后的 candidates
```

配置项建议：

```text
ENABLE_RERANK = False
RETRIEVAL_TOP_K = 10
RERANK_TOP_N = 3
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
```

### 3.4 验收标准

- 关闭 Rerank 时，系统行为与当前版本一致。
- 开启 Rerank 时，FAISS 先召回更多候选，再由 Rerank 选出最终上下文。
- `/ask` 返回 sources 时能看到原始 distance，后续可增加 rerank_score。
- 同一测试集下，开启 Rerank 后回答准确性或来源准确性有提升。

---

## 4. 方向二：建立跨文档问答测试集

### 4.1 测试集目标

目前系统已经“能跑”，但还需要证明“有效”。固定测试集可以帮助我们比较不同参数、不同 chunk 策略、是否开启 Rerank 对效果的影响。

### 4.2 建议测试集结构

建议新增：

```text
eval/
├── documents/
│   ├── alarm_manual.md
│   ├── device_notes.txt
│   └── troubleshooting_guide.pdf
└── rag_eval_questions.json
```

`rag_eval_questions.json` 示例：

```json
[
  {
    "id": "q001",
    "question": "OTN LOS 告警常见原因有哪些？",
    "expected_answer_keywords": ["fiber disconnected", "optical module", "low optical power"],
    "expected_sources": ["alarm_manual.md"],
    "type": "single_document"
  }
]
```

### 4.3 推荐覆盖类型

至少准备 10 条问题：

| 类型 | 数量 | 目的 |
| --- | --- | --- |
| 单文档直接问答 | 2 | 验证基础召回和回答 |
| 多文档知识检索 | 2 | 验证跨文档召回 |
| 多文档综合 | 2 | 验证综合上下文能力 |
| 相似内容区分 | 2 | 验证检索精度 |
| 知识库不存在答案 | 1 | 验证拒答能力 |
| 来源正确性 | 1 | 验证 source metadata |

### 4.4 评估指标

建议记录：

- 检索是否命中正确文档。
- Top-K 中正确 chunk 的排名。
- 回答是否包含 expected keywords。
- sources 是否正确。
- 总耗时。
- 检索耗时。
- LLM 调用耗时。

---

## 5. 方向三：理解向量存储与向量数据库

### 5.1 当前向量存储机制

当前系统采用 “FAISS + SQLite + JSON Metadata” 的组合：

```text
SQLite documents 表
  保存 document_id / filename / file_type / status

SQLite chunks 表
  保存 chunk_id / document_id / chunk_text / embedding_ref

FAISS index
  保存 chunk embedding 向量

vector_metadata.json
  保存 vector_index → chunk_id / document_id 映射
```

这种架构清晰、轻量，适合 MVP 和学习 RAG 原理。

### 5.2 需要重点理解的问题

1. 文本如何通过 SentenceTransformer 转换成 384 维向量。
2. FAISS 中的第 N 个向量如何通过 metadata 找回 chunk_id。
3. 为什么 chunk 文本不直接存 FAISS，而是存 SQLite。
4. 删除文档时为什么需要重建 FAISS index。
5. 当 vector_metadata.json 丢失或损坏时，FAISS 和 SQLite 会出现什么不一致。

### 5.3 向量数据库调研方向

后续可以调研：

| 方案 | 适合场景 |
| --- | --- |
| Qdrant | 本地和服务化部署都比较友好，metadata filter 能力好 |
| Milvus | 大规模向量检索，偏生产集群 |
| pgvector | 如果系统已经使用 PostgreSQL，数据和向量可放在同一个数据库 |
| FAISS | 本地轻量、学习和原型验证方便 |

### 5.4 建议先做的实验

不建议马上替换 FAISS。可以先写一个对比文档：

```text
VECTOR_STORE_NOTES.md
├── 当前 FAISS 如何保存/加载
├── vector_metadata.json 如何映射 chunk
├── 删除文档时如何重建 index
├── Qdrant / Milvus / pgvector 对比
└── 后续迁移条件
```

---

## 6. 方向四：增加日志记录

### 6.1 为什么日志优先级很高

当前前端遇到 “Failed to fetch”、上传失败、检索为空、LLM 报错时，如果没有日志，很难判断问题发生在：

- 前端请求阶段。
- FastAPI 接口层。
- 文件保存阶段。
- 文本解析阶段。
- Chunking 阶段。
- Embedding 阶段。
- FAISS 写入阶段。
- LLM 调用阶段。

日志能让系统从黑盒变成可观察的流水线。

### 6.2 建议记录的关键节点

文档入库：

```text
upload_start
file_saved
text_loaded
chunks_created
embeddings_created
vectors_added
document_completed
document_failed
```

问答流程：

```text
ask_start
question_embedded
vector_search_completed
chunks_loaded
prompt_built
llm_completed
ask_completed
ask_failed
```

### 6.3 每条日志建议包含

- stage：当前阶段。
- document_id。
- filename。
- file_type。
- chunk_count。
- chunk_ids。
- top_k。
- distances。
- elapsed_ms。
- error_message。

### 6.4 最小实现建议

先不要引入复杂日志平台，只用 Python 标准库：

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

然后逐步把 `print()` 替换成：

```python
logger.info("Document loaded", extra={"document_id": document_id})
logger.exception("Document ingestion failed")
```

---

## 7. 方向五：学习断点调试

### 7.1 推荐断点位置

建议在这些函数设置断点：

| 文件 | 函数 | 观察内容 |
| --- | --- | --- |
| `api.py` | `upload_document` | 上传文件名、content bytes |
| `document_service.py` | `ingest_document_file` | filename、file_type、text、chunks |
| `chunking.py` | `chunk_text` | paragraphs、current_chunk、chunks |
| `embedding_service.py` | `embed_texts` | embedding shape |
| `vector_store.py` | `add_vectors` | vector_index、metadata |
| `vector_store.py` | `search` | distances、indices、metadata mapping |
| `rag_service.py` | `ask` | search_results、contexts、sources、prompt |
| `llm.py` | `generate_answer` | prompt、LLM response |

### 7.2 推荐观察变量

- 文档读取后的 `text`。
- `chunks` 数量和每个 chunk 内容。
- embedding 维度是否为 384。
- FAISS 返回的 `indices` 和 `distances`。
- `vector_metadata.json` 中的 vector_index 是否和 FAISS 对齐。
- `contexts` 是否真的与问题相关。
- 最终 prompt 是否包含正确上下文。

---

## 8. 方向六：增强系统理解

需要能够清楚解释以下问题：

### 8.1 为什么文档需要切块

因为 LLM Prompt 长度有限，且向量检索需要以较小语义单元为对象。如果直接把整篇 PDF 或整份手册作为一个向量，检索粒度太粗，也容易把无关内容带入 Prompt。

### 8.2 Embedding 和 FAISS 分别负责什么

- Embedding：把文本变成向量。
- FAISS：在向量空间里快速找到与用户问题最相似的文本块。

### 8.3 为什么同时使用 FAISS 和 SQLite

- FAISS 擅长向量检索，但不适合保存完整业务数据。
- SQLite 擅长保存文档、chunk、文件名、状态、问答历史等结构化信息。
- `vector_metadata.json` 负责把 FAISS 的 vector_index 映射回 SQLite 的 chunk_id。

### 8.4 Loader Registry 为什么便于扩展

因为上传流程只依赖统一接口：

```text
supports(filename)
load_text(file_path)
FILE_TYPE
SUPPORTED_EXTENSIONS
```

新增 DOCX 或 HTML 时，只需要增加 loader 并注册，不需要重写上传、chunk、embedding、vector store 逻辑。

---

## 9. 方向七：增加用户可配置输入

### 9.1 为什么需要可配置

RAG 效果高度依赖参数。例如：

- Top-K 太小：可能召回不到正确上下文。
- Top-K 太大：Prompt 噪声变多。
- Rerank 开启：准确性可能提升，但耗时增加。
- 相似度阈值太严格：可能误判“知识库没有答案”。
- Prompt 不同：回答风格和引用方式会变化。

### 9.2 建议分阶段加入

第一阶段只加轻量参数：

```text
retrieval_top_k
```

第二阶段加入：

```text
enable_rerank
rerank_top_n
similarity_threshold
```

第三阶段加入：

```text
system_prompt
temperature
retrieval_mode
```

### 9.3 前端交互建议

在 Chat 页面右侧或下方增加一个 “Experiment Settings” 小面板：

```text
[ ] Enable rerank
Top-K: 2 / 5 / 10
Rerank keep: 2 / 3 / 5
Similarity threshold: slider
Temperature: slider
```

这样前端会从简单演示页，逐步变成 RAG 实验平台。

---

## 10. 推荐短期任务拆分

### v0.5：可观测性和测试集

- 增加 logging 基础配置。
- 替换关键 `print()`。
- 增加耗时统计。
- 新增 `eval/rag_eval_questions.json`。
- 写一个简单 `eval_runner.py`，记录 retrieval hit 和 answer keyword match。

### v0.6：检索参数可配置

- `/ask` request 增加 `top_k`。
- `vector_store.search()` 支持传入 top_k。
- 前端 Chat 页增加 Top-K 设置。
- 记录不同 Top-K 下的结果。

### v0.7：Rerank 实验

- 新增 `rerank_service.py`。
- 新增 `ENABLE_RERANK` 配置。
- FAISS 先召回 Top-10。
- Rerank 保留 Top-3。
- 测试集对比 rerank 前后来源命中率。

### v0.8：向量数据库调研或 PoC

- 写 Qdrant / pgvector 对比文档。
- 做一个单独分支 PoC。
- 不急着替换当前 FAISS 主流程。

---

## 11. 最推荐现在立刻做的下一步

如果只选一个最值得马上做的任务，我建议：

```text
先加日志 + 建立 10 条跨文档测试集
```

原因：

1. 不会大幅增加系统复杂性。
2. 能让你清楚解释整个 RAG Pipeline。
3. 后续做 Rerank、Top-K、Prompt 优化时有固定评估基准。
4. 出错时能快速定位是上传、解析、向量、检索还是 LLM 的问题。

