from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer
from docling.chunking import HybridChunker
from sentence_transformers import SentenceTransformer
from transformers import pipeline  # Import the pipeline for text generation
import os
import psycopg2
from pgvector.psycopg2 import register_vector

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MAX_TOKENS = 64  # set to a small number for illustrative purposes

# Convert document
source = "2600_Digital_Edition-42-4.pdf"
converter = DocumentConverter()
doc = converter.convert(source).document
md = (doc.export_to_markdown())
put_paath = "output/output_simple.md"
with open(put_paath, 'w', encoding='utf-8') as f:
    f.write(md)

# Chunk document
chunker = HybridChunker()
chunk_iter = chunker.chunk(dl_doc=doc)

# Print chunks for inspection
for i, chunk in enumerate(chunk_iter):
    print(f"=== {i} ===")
    print(f"chunk.text:\n{f'{chunk.text[:300]}…'!r}")
    enriched_text = chunker.contextualize(chunk=chunk)
    print(f"chunker.contextualize(chunk):\n{f'{enriched_text[:300]}…'!r}")
    print()

# Setup PostgreSQL connection
DBUSER = "postgres"
DBPASS = "postgres"
DBHOST = "localhost"
DBNAME = "docdb"
DBSSL = "disable" if DBHOST == "localhost" else "require"

conn = psycopg2.connect(database=DBNAME, user=DBUSER, password=DBPASS, host=DBHOST, sslmode=DBSSL)
conn.autocommit = True
cur = conn.cursor()
cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)

# Create table for storing chunks and embeddings
cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        content TEXT,
        embedding vector(384)
    )
""")
conn.commit()

# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer(EMBED_MODEL_ID)
# Load the text generation model
generator = pipeline('text-generation', model='gpt2')  # You can choose a different model if needed

# Re-chunk and generate embeddings
chunk_iter = chunker.chunk(dl_doc=doc)
print("Storing chunks with embeddings...")
for i, chunk in enumerate(chunk_iter):
    embedding = model.encode(chunk.text)
    cur.execute(
        "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
        (chunk.text, embedding.tolist())
    )
    print(f"Stored chunk {i}")

conn.commit()
print("All chunks stored successfully!")

def main():
    while True:
        # Get user input for query
        query = input("Enter your search query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        
        query_embedding = model.encode(query)

        cur.execute(""" 
            SELECT id, content, embedding <-> %s::vector as distance 
            FROM documents 
            ORDER BY embedding <-> %s::vector 
            LIMIT 5 
        """, (query_embedding.tolist(), query_embedding.tolist()))

        results = cur.fetchall()
        print(f"\nSearch results for '{query}':")
        for result in results:
            print(f"ID: {result[0]}, Distance: {result[2]:.4f}")
            print(f"Content: {result[1][:200]}...\n")

        # Generate a response based on the retrieved content
        response_input = "Based on the following information, provide a summary: " + " ".join([result[1] for result in results])
        response = generator(response_input, max_length=150, num_return_sequences=1)
        print(f"AI Response: {response[0]['generated_text']}")

# Call the main function
if __name__ == "__main__":
    main()

cur.close()
conn.close()