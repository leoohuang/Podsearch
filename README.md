# PodSearch

一个播客语义搜索系统。输入一句话，从播客音频中找到最相关的片段。

比如搜索"AI时代的焦虑"，系统会从所有播客中找到讨论这个话题的具体时间段和内容。

## 它是怎么工作的

整个系统分为两大部分：**数据处理流水线** 和 **搜索引擎**。

### 数据处理流水线

```
播客音频 → 语音转文字 → 文本切片 → 生成向量 → 存入向量数据库
```

1. **下载播客音频**（`download_all.py`）：根据 `podcasts.yaml` 配置，下载指定播客的音频文件
2. **语音转文字**（`transcribe_all.py`）：用 Faster-Whisper 把音频转成带时间戳的文字
3. **文本切片**（`src/chunking.py`）：把长文本按语义切成 30~60 秒的小段，段与段之间重叠 5 秒防止语义断裂
4. **生成向量并入库**（`build_vector.py`）：用 BGE-M3 模型把每段文本转成 1024 维向量，存入 ChromaDB

### 搜索引擎（两阶段架构）

```
用户输入 → 向量召回 Top-30 → Cross-Encoder 精排 → 返回 Top-10
```

**第一阶段 — 向量召回**：把搜索词转成向量，在数据库中找到最相似的 30 条候选结果。速度快，但精度有限。

**第二阶段 — Cross-Encoder 精排**：用 BGE-Reranker 把搜索词和每条候选文本拼在一起，逐一精算相关度，重新排序后取前 10 条。精度高，但速度慢，所以只对第一阶段筛出的 30 条做精排。

## 评估结果

在 20 个中英文测试 query 上进行了人工标注评估：

| 指标 | 分数 | 含义 |
|------|------|------|
| MRR | 0.825 | 第一个相关结果平均排在第 1~2 名 |
| Precision@10 | 0.630 | 返回的 10 条结果中平均 6.3 条是相关的 |

部分 query 的表现：

| Query | MRR | Precision@10 |
|-------|-----|-------------|
| ADHD | 1.000 | 1.000 |
| 巴菲特 | 1.000 | 1.000 |
| 健康习惯 | 1.000 | 1.000 |
| 人工智能未来 | 1.000 | 0.900 |
| ai焦虑 | 1.000 | 0.700 |
| cryptocurrency | 0.500 | 0.100 |
| consciousness | 0.500 | 0.100 |

系统在播客库覆盖的话题上表现很好（MRR=1.0），在库中内容较少的话题上表现较差（如 cryptocurrency），这符合预期。

## 项目结构

```
podsearch/
├── src/
│   ├── config.py        # 所有配置（路径、模型、参数）
│   ├── transcribe.py    # 语音转文字
│   ├── chunking.py      # 文本切片
│   ├── embedding.py     # 文本向量化（BGE-M3）
│   ├── indexing.py      # ChromaDB 向量数据库连接
│   ├── search.py        # 搜索 + 精排逻辑
│   ├── ingest.py        # 数据导入
│   └── pipeline.py      # 完整流水线
├── data/
│   ├── raw_audio/       # 下载的播客音频
│   ├── transcripts/     # 语音转文字结果（JSON）
│   └── chroma_db/       # 向量数据库
├── podcasts.yaml        # 播客源配置
├── download_all.py      # 批量下载播客
├── transcribe_all.py    # 批量语音转文字
├── build_vector.py      # 构建向量数据库
├── retrieve.py          # 命令行搜索入口
└── requirements.txt     # Python 依赖
```

## 快速开始

### 1. 安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 处理数据

```bash
# 下载播客音频
python download_all.py

# 语音转文字
python transcribe_all.py

# 构建向量数据库
python build_vector.py
```

### 3. 搜索

```bash
python retrieve.py
```

输入搜索内容，系统会返回最相关的播客片段，包含精排分数、时间戳和播客名称。

## 技术栈

| 组件 | 技术 |
|------|------|
| 语音转文字 | Faster-Whisper (tiny) |
| 文本向量化 | BGE-M3 (1024维) |
| 向量数据库 | ChromaDB |
| 精排模型 | BGE-Reranker-v2-M3 |
| 前端（开发中） | Streamlit |

## 支持的播客

支持所有能够获取 RSS 的播客，例如：

- Apple Podcast
- 小宇宙、Spotify（这俩作者目前没有自己试过）