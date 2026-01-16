#!/bin/bash

# Initialize git repository
git init

# Configure git user (update with your details)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Add all files to staging area
git add .

# Create initial commit with descriptive message
git commit -m "feat: Implement RAG agent with vector search and response generation

- Convert documents to markdown using Docling
- Chunk documents using HybridChunker
- Generate embeddings with SentenceTransformer
- Store chunks and embeddings in PostgreSQL with pgvector
- Implement semantic vector search with proper type casting
- Add text generation for contextual responses
- Create interactive conversational loop for user queries
- Include comprehensive implementation documentation"

# Display git status
git status

# Display commit log
git log --oneline
