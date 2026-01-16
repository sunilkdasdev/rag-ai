# RAG Agent Implementation Guide

## Overview
This document outlines the step-by-step process of building a Retrieval-Augmented Generation (RAG) agent that converts documents into searchable vector embeddings and generates contextual responses.

## Implementation Steps

### Step 1: Document Conversion
**What:** Convert PDF documents to markdown format using Docling.
**Why:** Markdown provides a structured, readable format that preserves document hierarchy and content organization.
**Code:**
```python
converter = DocumentConverter()
doc = converter.convert(source).document
md = doc.export_to_markdown()
```

### Step 2: Document Chunking
**What:** Split the document into smaller, manageable chunks using HybridChunker.
**Why:** Large documents need to be broken into chunks to create meaningful embeddings and improve retrieval accuracy.
**Code:**
```python
chunker = HybridChunker()
chunk_iter = chunker.chunk(dl_doc=doc)
```

### Step 3: Vector Embeddings
**What:** Convert text chunks into dense vector representations using SentenceTransformer.
**Why:** Embeddings enable semantic similarity search, allowing the agent to find relevant content based on meaning rather than keyword matching.
**Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional vectors)

### Step 4: Database Storage
**What:** Store chunks and embeddings in PostgreSQL with pgvector extension.
**Why:** Persistent storage allows querying the same knowledge base multiple times without reprocessing.
**Table Structure:**
- `id`: Primary key
- `content`: Text chunk
- `embedding`: Vector(384) for similarity search

### Step 5: Vector Search
**What:** Implement semantic search using pgvector's distance operator (`<->`).
**Why:** Enables fast retrieval of the most relevant chunks for any user query.
**Key Fix:** Cast query embeddings to vector type using `%s::vector` syntax.

### Step 6: Response Generation
**What:** Add text generation to synthesize answers from retrieved content.
**Why:** Transforms the system from a retriever to a true generative agent that produces contextual responses.
**Model:** GPT-2 (can be upgraded to larger models for better quality)

### Step 7: Conversational Loop
**What:** Implement a persistent interactive session with exit functionality.
**Why:** Provides a user-friendly interface for multiple queries without restarting the agent.

## Architecture Flow
```
User Query
    ↓
Encode Query to Embedding
    ↓
Vector Search in PostgreSQL
    ↓
Retrieve Top 5 Relevant Chunks
    ↓
Generate Response using Retrieved Context
    ↓
Display Results to User
```

## Key Technologies
- **Document Processing:** Docling
- **Embeddings:** Sentence Transformers
- **Database:** PostgreSQL + pgvector
- **Text Generation:** Hugging Face Transformers
- **Connection:** psycopg2

## Future Enhancements
1. Upgrade text generation model (Mistral, Llama 2, etc.)
2. Add conversation history management
3. Implement reranking for better relevance
4. Add source attribution to generated responses
5. Support for multiple document sources
6. Fine-tuning embeddings on domain-specific data

## Commit Message
```
feat: Implement RAG agent with vector search and response generation

- Convert documents to markdown using Docling
- Chunk documents using HybridChunker
- Generate embeddings with SentenceTransformer
- Store chunks and embeddings in PostgreSQL with pgvector
- Implement semantic vector search with proper type casting
- Add text generation for contextual responses
- Create interactive conversational loop for user queries
- Include documentation for implementation steps
```
