---
name: interpretation-engine
description: Core interpretation patterns for Cortexa Phase 1. Use when working on document RAG or input interpreter features.
---

# Interpretation Engine - Phase 1

## Features

### 1. Document RAG
Upload txt/pdf/md → chunk → embed → store → query → answer

See [document-rag skill](../document-rag/SKILL.md) for implementation details.

### 2. Input Interpreter  
User text → prompt template (tone/style) → AI → interpretation

See [input-interpreter skill](../input-interpreter/SKILL.md) for implementation details.

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/upload` | POST | Upload document (txt, pdf, md) |
| `/ask` | POST | Query document with question |
| `/interpret` | POST | Interpret user input with tone/style |
| `/health` | GET | Health check |

## Config Settings

```python
# config.py
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 100
EMBEDDING_MODEL: str = "text-embedding-3-large"
CHAT_MODEL: str = "gpt-4o-mini"
```

## Service Dependencies

```
main.py
├── document_service (upload, extract, chunk)
├── embedding_service (generate embeddings)
├── vector_store_service (store, query ChromaDB)
├── rag_service (answer questions)
└── interpreter_service (interpret user input)
```
