# ModularRAG

> A modular, benchmarkable RAG engine for building and evaluating retrieval-augmented generation systems.

**ModularRAG** is an open-source RAG framework designed around one idea:

**Every part of your RAG pipeline should be replaceable, observable, and measurable.**

Swap chunking strategies, embedding models, retrievers, rerankers, and LLMs without rebuilding your entire application.

---

## Why ModularRAG?

Most RAG applications quickly become tightly coupled:

```text
PDF
 ↓
Chunking
 ↓
Embedding
 ↓
Vector DB
 ↓
LLM
```

Changing one component often means changing several others.

ModularRAG separates the pipeline into independent components:

```text
                 ┌──────────────────┐
                 │    Documents     │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │    Ingestion     │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │     Chunking     │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │    Embeddings    │
                 └────────┬─────────┘
                          ↓
              ┌─────────────────────────┐
              │       Retrieval         │
              │                         │
              │ Vector │ BM25 │ Hybrid │
              └────────────┬────────────┘
                           ↓
                 ┌──────────────────┐
                 │    Reranking     │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │    Generation    │
                 └────────┬─────────┘
                          ↓
                 ┌──────────────────┐
                 │ Answer + Sources │
                 └──────────────────┘
```

---

## Features

* 📄 PDF/document ingestion
* ✂️ Pluggable chunking strategies
* 🧠 Configurable embedding models
* 🔎 Vector similarity search
* 🔀 Hybrid retrieval
* 🎯 Optional reranking
* 🤖 OpenAI-compatible generation
* 📚 Source-aware answers
* 📊 Retrieval evaluation
* ⚡ FastAPI backend
* 🐘 PostgreSQL + pgvector
* 🐳 Docker-based infrastructure
* 🧩 Modular architecture

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/modularrag.git
cd modularrag
```

### 2. Start PostgreSQL + pgvector

```bash
docker compose up -d
```

### 3. Create the Python environment

```bash
cd backend

python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create:

```text
backend/.env
```

Example:

```env
DATABASE_URL=postgresql+psycopg://raguser:ragpassword@localhost:5432/ragdb

OPENAI_API_KEY=your_key_here

EMBEDDING_MODEL=text-embedding-3-small
```

### 6. Start the API

```bash
python -m uvicorn app.main:app --port 8001
```

API:

```text
http://127.0.0.1:8001
```

Interactive API documentation:

```text
http://127.0.0.1:8001/docs
```

---

# Architecture

```text
modularrag/
│
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       │
│       ├── db/
│       │   └── database.py
│       │
│       ├── ingestion/
│       │   └── pdf.py
│       │
│       ├── rag/
│       │   ├── chunker.py
│       │   ├── embedder.py
│       │   ├── retriever.py
│       │   ├── reranker.py
│       │   └── generator.py
│       │
│       └── main.py
│
├── frontend/
│
├── schema.sql
├── docker-compose.yml
└── README.md
```

The goal is to keep each stage independently replaceable.

---

# RAG Pipeline

## 1. Ingestion

Documents are parsed into text while preserving useful metadata such as:

```json
{
  "filename": "resume.pdf",
  "page_start": 1,
  "page_end": 1,
  "text": "..."
}
```

---

## 2. Chunking

Documents are divided into smaller pieces before embedding.

ModularRAG is designed to support multiple chunking strategies:

```text
Recursive Chunking
Semantic Chunking
Markdown/Structure-aware Chunking
```

A future configuration might look like:

```python
rag = RAG(
    chunker="semantic"
)
```

---

## 3. Embeddings

Each chunk is converted into a vector representation.

For example:

```text
"Convex Twin is a deterministic replay platform..."
                         ↓
              [0.012, -0.231, 0.884, ...]
```

These vectors are stored in PostgreSQL using `pgvector`.

---

## 4. Retrieval

A user's question is embedded and compared against stored chunks.

Example:

```text
Query:
"What projects has Rewant built?"

             ↓

      Vector Retrieval

             ↓

1. Convex Twin
2. Anchor
3. Delta Mandate
4. Agent Failure Simulator
```

The system returns the most relevant context for generation.

---

## 5. Generation

Retrieved context is passed to the language model:

```text
Question
   +
Retrieved Context
   ↓
LLM
   ↓
Grounded Answer
   +
Sources
```

The generator is instructed to answer using the retrieved evidence rather than inventing information.

---

# Example

Upload a resume:

```text
POST /documents/upload
```

Then ask:

```json
{
  "question": "What projects has Rewant built?"
}
```

Response:

```json
{
  "answer": "Rewant's projects include Convex Twin, Anchor, Delta Mandate, and Agent Failure Simulator.",
  "sources": [
    {
      "filename": "RewantResume.pdf",
      "page_start": 1,
      "page_end": 1
    }
  ]
}
```

---

# The Interesting Part: Evaluation

A RAG system can produce an answer that *sounds* correct while retrieving the wrong context.

ModularRAG aims to make those failures measurable.

Instead of only asking:

> "Does the answer look good?"

evaluate the pipeline itself:

```text
                 RAG Evaluation

Retrieval Recall@K
        ↓
Context Precision
        ↓
Context Recall
        ↓
Answer Relevance
        ↓
Faithfulness
        ↓
Latency
```

This allows different configurations to be compared.

Example:

```text
                    Recall@5    Latency

Recursive + Vector     87%       320ms
Semantic + Vector      91%       410ms
Semantic + Hybrid      95%       530ms
```

The goal is to make RAG architecture **experimentable rather than opinion-based**.

---

# Roadmap

### In Progress

* [x] PDF ingestion
* [x] PostgreSQL + pgvector
* [x] Document/chunk storage
* [x] Embedding pipeline
* [x] Vector retrieval
* [x] LLM generation
* [x] Source citations
* [x] FastAPI API

### Next

* [ ] Pluggable chunkers
* [ ] Hybrid BM25 + vector retrieval
* [ ] Reranking
* [ ] Retrieval evaluation
* [ ] Dataset-based benchmarks
* [ ] Streaming responses
* [ ] Query rewriting
* [ ] Parent-document retrieval
* [ ] Metadata filtering
* [ ] Observability
* [ ] Local embedding models
* [ ] Ollama support

### Long Term

* [ ] RAG evaluation dashboard
* [ ] Retrieval playground
* [ ] Configuration-based pipelines
* [ ] Multiple vector database adapters
* [ ] TypeScript SDK
* [ ] CLI
* [ ] Plugin system
* [ ] Community-contributed components

---

# Design Principles

### 1. Components over monoliths

Every major RAG operation should be independently replaceable.

### 2. Retrieval is a first-class system

Good generation cannot compensate for consistently bad retrieval.

### 3. Measure before optimizing

Changes to chunking, embeddings, retrieval, and reranking should be evaluated rather than guessed.

### 4. Bring your own model

The framework should not force users into a single model provider.

### 5. Local-first where possible

The long-term goal is to make it possible to run the complete pipeline locally.

---

# Tech Stack

| Layer          | Technology         |
| -------------- | ------------------ |
| API            | FastAPI            |
| Language       | Python             |
| Database       | PostgreSQL         |
| Vector Search  | pgvector           |
| ORM            | SQLAlchemy         |
| Embeddings     | Configurable       |
| LLM            | OpenAI-compatible  |
| Infrastructure | Docker             |
| Frontend       | React / TypeScript |

---

# Contributing

Contributions are welcome.

Areas where contributions are particularly useful:

* New chunking strategies
* Embedding providers
* Retrieval algorithms
* Rerankers
* Evaluation metrics
* Vector database adapters
* Local model integrations
* Documentation
* Benchmarks

Before opening a PR, please open an issue describing the proposed change.

---

# License

MIT

---

## Status

🚧 **Early development**

ModularRAG is currently evolving from a working RAG application into a general-purpose modular RAG experimentation framework.

If you're interested in retrieval systems, LLM infrastructure, or evaluation, contributions and feedback are welcome.
