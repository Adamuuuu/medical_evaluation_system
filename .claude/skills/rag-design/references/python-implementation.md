# Python RAG Implementation

## Quick Start

### 1. Setup Storage

```python
import sqlite3
import numpy as np
from typing import List, Dict

# Load sqlite-vec extension
conn = sqlite3.connect('memory.db')
conn.enable_load_extension(True)
conn.load_extension('vec0')  # or path to vec0.so

# Create tables
conn.executescript("""
    CREATE TABLE IF NOT EXISTS chunks (
        id TEXT PRIMARY KEY,
        path TEXT NOT NULL,
        start_line INTEGER,
        end_line INTEGER,
        content TEXT,
        source TEXT,
        created_at INTEGER
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
        embedding FLOAT[768]
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
        chunk_id UNINDEXED,
        content
    );

    CREATE TABLE IF NOT EXISTS embedding_cache (
        content_hash TEXT PRIMARY KEY,
        embedding BLOB,
        provider TEXT,
        model TEXT
    );
""")
conn.commit()
```

### 2. Initialize Embedding Provider

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def embed(text: str) -> List[float]:
    response = client.embeddings.create(
        model='text-embedding-3-small',
        input=text
    )
    return response.data[0].embedding

def embed_batch(texts: List[str]) -> List[List[float]]:
    response = client.embeddings.create(
        model='text-embedding-3-small',
        input=texts
    )
    return [d.embedding for d in response.data]
```

### 3. Index Documents

```python
import hashlib
import uuid
import time

def chunk_text(content: str, max_size: int = 500) -> List[Dict]:
    lines = content.split('\n')
    chunks = []
    current = {'text': '', 'start': 1, 'end': 1}

    for i, line in enumerate(lines, 1):
        current['text'] += line + '\n'
        current['end'] = i

        if len(current['text']) > max_size or i == len(lines):
            if current['text'].strip():
                chunks.append(current.copy())
            current = {'text': '', 'start': i + 1, 'end': i + 1}

    return chunks

def get_cached_embedding(content_hash: str) -> List[float] | None:
    cursor = conn.execute(
        "SELECT embedding FROM embedding_cache WHERE content_hash = ?",
        (content_hash,)
    )
    row = cursor.fetchone()
    if row:
        return np.frombuffer(row[0], dtype=np.float32).tolist()
    return None

def cache_embedding(content_hash: str, embedding: List[float], provider: str):
    blob = np.array(embedding, dtype=np.float32).tobytes()
    conn.execute(
        "INSERT OR REPLACE INTO embedding_cache VALUES (?, ?, ?, ?)",
        (content_hash, blob, provider, 'text-embedding-3-small')
    )
    conn.commit()

def index_document(path: str, content: str):
    chunks = chunk_text(content)

    for chunk in chunks:
        chunk_id = str(uuid.uuid4())
        content_hash = hashlib.sha256(chunk['text'].encode()).hexdigest()

        # Check cache
        embedding = get_cached_embedding(content_hash)
        if not embedding:
            embedding = embed(chunk['text'])
            cache_embedding(content_hash, embedding, 'openai')

        # Store chunk
        conn.execute("""
            INSERT INTO chunks (id, path, start_line, end_line, content, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (chunk_id, path, chunk['start'], chunk['end'],
              chunk['text'], 'memory', int(time.time() * 1000)))

        # Store vector
        embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
        conn.execute(
            "INSERT INTO chunks_vec (rowid, embedding) VALUES (?, ?)",
            (chunk_id, embedding_blob)
        )

        # Store FTS
        conn.execute(
            "INSERT INTO chunks_fts (chunk_id, content) VALUES (?, ?)",
            (chunk_id, chunk['text'])
        )

    conn.commit()
```

### 4. Implement Search

```python
from dataclasses import dataclass

@dataclass
class SearchResult:
    id: str
    path: str
    start_line: int
    end_line: int
    content: str
    score: float
    source: str

def search(query: str, max_results: int = 10) -> List[SearchResult]:
    # Get query embedding
    query_embedding = embed(query)
    query_blob = np.array(query_embedding, dtype=np.float32).tobytes()

    # Vector search
    vector_results = conn.execute("""
        SELECT c.*, vec_distance_L2(v.embedding, ?) as distance
        FROM chunks c
        JOIN chunks_vec v ON c.id = v.rowid
        ORDER BY distance
        LIMIT 50
    """, (query_blob,)).fetchall()

    # Keyword search
    fts_query = ' AND '.join(f'"{word}"' for word in query.split())
    keyword_results = conn.execute("""
        SELECT c.*, f.rank
        FROM chunks c
        JOIN chunks_fts f ON c.id = f.chunk_id
        WHERE f.content MATCH ?
        ORDER BY f.rank
        LIMIT 50
    """, (fts_query,)).fetchall()

    # Merge results
    merged = merge_results(vector_results, keyword_results)

    return merged[:max_results]

def merge_results(vector_results, keyword_results,
                 vector_weight=0.7, keyword_weight=0.3):
    by_id = {}

    # Process vector results
    for row in vector_results:
        chunk_id = row[0]
        by_id[chunk_id] = {
            'id': row[0],
            'path': row[1],
            'start_line': row[2],
            'end_line': row[3],
            'content': row[4],
            'source': row[5],
            'score': vector_weight * (1 / (1 + row[7]))  # distance
        }

    # Process keyword results
    for row in keyword_results:
        chunk_id = row[0]
        keyword_score = keyword_weight * (1 / (1 + abs(row[7])))  # rank

        if chunk_id in by_id:
            by_id[chunk_id]['score'] += keyword_score
        else:
            by_id[chunk_id] = {
                'id': row[0],
                'path': row[1],
                'start_line': row[2],
                'end_line': row[3],
                'content': row[4],
                'source': row[5],
                'score': keyword_score
            }

    # Sort by score
    results = sorted(by_id.values(), key=lambda x: x['score'], reverse=True)
    return [SearchResult(**r) for r in results]
```

## Advanced Features

### MMR Re-ranking

```python
def jaccard_similarity(text_a: str, text_b: str) -> float:
    tokens_a = set(text_a.lower().split())
    tokens_b = set(text_b.lower().split())

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b

    return len(intersection) / len(union)

def apply_mmr(results: List[SearchResult],
              lambda_param: float = 0.7,
              max_results: int = 10) -> List[SearchResult]:
    selected = []
    remaining = results.copy()

    while len(selected) < max_results and remaining:
        best_idx = 0
        best_score = float('-inf')

        for i, result in enumerate(remaining):
            relevance = result.score

            if selected:
                max_sim = max(
                    jaccard_similarity(result.content, s.content)
                    for s in selected
                )
            else:
                max_sim = 0

            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = i

        selected.append(remaining.pop(best_idx))

    return selected
```

### Temporal Decay

```python
import math

def apply_temporal_decay(results: List[SearchResult],
                        half_life_days: int = 30) -> List[SearchResult]:
    now_ms = int(time.time() * 1000)
    half_life_ms = half_life_days * 24 * 60 * 60 * 1000

    for result in results:
        # Assuming created_at is stored in the result
        age_ms = now_ms - result.created_at
        decay_factor = math.exp(-math.log(2) * age_ms / half_life_ms)
        result.score *= decay_factor

    return sorted(results, key=lambda x: x.score, reverse=True)
```

### Batch Embedding

```python
import asyncio
from typing import List

async def batch_embed_async(texts: List[str],
                           batch_size: int = 100,
                           delay_ms: int = 100) -> List[List[float]]:
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = embed_batch(batch)
        results.extend(embeddings)

        # Rate limiting
        if i + batch_size < len(texts):
            await asyncio.sleep(delay_ms / 1000)

    return results

# Synchronous version
def batch_embed_sync(texts: List[str],
                    batch_size: int = 100,
                    delay_ms: int = 100) -> List[List[float]]:
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = embed_batch(batch)
        results.extend(embeddings)

        if i + batch_size < len(texts):
            time.sleep(delay_ms / 1000)

    return results
```

### File Watching

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

class MemoryFileHandler(FileSystemEventHandler):
    def __init__(self, debounce_seconds: float = 1.0):
        self.debounce_seconds = debounce_seconds
        self.timers = {}

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return

        # Cancel existing timer
        if event.src_path in self.timers:
            self.timers[event.src_path].cancel()

        # Set new timer
        timer = threading.Timer(
            self.debounce_seconds,
            self.reindex_file,
            args=[event.src_path]
        )
        self.timers[event.src_path] = timer
        timer.start()

    def reindex_file(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        index_document(path, content)
        print(f"Reindexed: {path}")

# Start watching
observer = Observer()
handler = MemoryFileHandler(debounce_seconds=1.0)
observer.schedule(handler, path='./memory', recursive=True)
observer.start()
```

## Alternative: Using LangChain

```python
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize
embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# Create vector store
vectorstore = Chroma(
    embedding_function=embeddings,
    persist_directory='./chroma_db'
)

# Index documents
def index_with_langchain(path: str, content: str):
    chunks = text_splitter.create_documents(
        texts=[content],
        metadatas=[{'path': path}]
    )
    vectorstore.add_documents(chunks)

# Search
def search_with_langchain(query: str, k: int = 10):
    return vectorstore.similarity_search_with_score(query, k=k)
```

## Alternative: Using LlamaIndex

```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.embeddings import OpenAIEmbedding

# Initialize
embed_model = OpenAIEmbedding(model='text-embedding-3-small')
service_context = ServiceContext.from_defaults(embed_model=embed_model)

# Load and index
documents = SimpleDirectoryReader('./memory').load_data()
index = VectorStoreIndex.from_documents(
    documents,
    service_context=service_context
)

# Search
query_engine = index.as_query_engine(similarity_top_k=10)
response = query_engine.query("your query here")
```

## Dependencies

```bash
pip install openai numpy watchdog

# For LangChain
pip install langchain chromadb

# For LlamaIndex
pip install llama-index

# For sqlite-vec
# Download from: https://github.com/asg017/sqlite-vec
```
