# RAG System Architecture

## System Overview

```
User Query
    ↓
Query Expansion (keyword extraction)
    ↓
Parallel Execution
    ├─ Vector Search (semantic)
    └─ Keyword Search (FTS)
    ↓
Hybrid Merge (weighted combination)
    ↓
MMR Re-ranking (diversity)
    ↓
Temporal Decay (recency boost)
    ↓
Top-K Results
```

## Component Architecture

### 1. Storage Layer

**SQLite with Extensions**
- `sqlite-vec`: Vector similarity search
- `fts5`: Full-text search with BM25 ranking
- Native SQLite: Metadata and caching

**Schema Design**
```sql
-- Chunks table (source of truth)
CREATE TABLE chunks (
  id TEXT PRIMARY KEY,
  path TEXT NOT NULL,
  start_line INTEGER,
  end_line INTEGER,
  content TEXT,
  source TEXT,  -- 'memory' or 'sessions'
  created_at INTEGER
);

-- Vector index
CREATE VIRTUAL TABLE chunks_vec USING vec0(
  chunk_id TEXT PRIMARY KEY,
  embedding FLOAT[768]
);

-- Full-text index
CREATE VIRTUAL TABLE chunks_fts USING fts5(
  chunk_id UNINDEXED,
  content,
  tokenize='porter unicode61'
);

-- Embedding cache
CREATE TABLE embedding_cache (
  content_hash TEXT PRIMARY KEY,
  embedding BLOB,
  provider TEXT,
  model TEXT,
  created_at INTEGER
);
```

### 2. Embedding Layer

**Provider Interface**
```typescript
interface EmbeddingProvider {
  embed(text: string): Promise<number[]>;
  embedBatch(texts: string[]): Promise<number[][]>;
  dimensions: number;
  model: string;
}
```

**Multi-Provider Support**
- OpenAI: `text-embedding-3-small` (1536d), `text-embedding-3-large` (3072d)
- Gemini: `text-embedding-004` (768d)
- Voyage: `voyage-2` (1024d)
- Mistral: `mistral-embed` (1024d)
- Local: `node-llama-cpp` with GGUF models

**Fallback Chain**
```typescript
Primary Provider → Fallback Provider → Error
```

### 3. Search Layer

**Vector Search**
```typescript
async function vectorSearch(query: string, opts: SearchOpts) {
  const embedding = await provider.embed(query);

  return db.prepare(`
    SELECT chunk_id, distance
    FROM chunks_vec
    WHERE embedding MATCH ?
    ORDER BY distance
    LIMIT ?
  `).all(embedding, opts.limit);
}
```

**Keyword Search**
```typescript
async function keywordSearch(query: string, opts: SearchOpts) {
  const ftsQuery = buildFtsQuery(query);

  return db.prepare(`
    SELECT chunk_id, rank
    FROM chunks_fts
    WHERE chunks_fts MATCH ?
    ORDER BY rank
    LIMIT ?
  `).all(ftsQuery, opts.limit);
}
```

**Hybrid Merge**
```typescript
function mergeResults(vector, keyword, weights) {
  const byId = new Map();

  // Normalize and combine scores
  for (const v of vector) {
    byId.set(v.id, {
      ...v,
      score: weights.vector * normalize(v.distance)
    });
  }

  for (const k of keyword) {
    const existing = byId.get(k.id);
    const keywordScore = weights.keyword * bm25ToScore(k.rank);

    if (existing) {
      existing.score += keywordScore;
    } else {
      byId.set(k.id, { ...k, score: keywordScore });
    }
  }

  return Array.from(byId.values())
    .sort((a, b) => b.score - a.score);
}
```

### 4. Re-ranking Layer

**MMR Algorithm**
- Balances relevance vs diversity
- Prevents redundant results
- Configurable lambda parameter (0=diversity, 1=relevance)

**Temporal Decay**
- Exponential decay based on document age
- Configurable half-life period
- Boosts recent content

### 5. Index Management

**File Watcher**
```typescript
const watcher = chokidar.watch(paths, {
  ignoreInitial: true,
  awaitWriteFinish: { stabilityThreshold: 500 }
});

watcher.on('change', debounce(syncIndex, 1000));
```

**Incremental Updates**
- Track file modification times
- Only reindex changed files
- Atomic transactions for consistency

**Batch Processing**
- Group embeddings into batches
- Respect API rate limits
- Progress callbacks for long operations

## Data Flow

### Indexing Flow
```
File Change Event
    ↓
Debounce (1s)
    ↓
Read File Content
    ↓
Chunk Text (by paragraph/section)
    ↓
Check Cache (content hash)
    ↓
Batch Embed (if not cached)
    ↓
Store Vectors + FTS
    ↓
Update Metadata
```

### Search Flow
```
User Query
    ↓
Extract Keywords
    ↓
[Vector Search] + [Keyword Search]
    ↓
Merge Results (weighted)
    ↓
Apply MMR (diversity)
    ↓
Apply Temporal Decay
    ↓
Format Snippets
    ↓
Return Top-K
```

## Scalability Considerations

**Memory Management**
- Stream large files instead of loading entirely
- Limit embedding batch sizes
- Clear caches periodically

**Performance**
- Index on frequently queried fields
- Use prepared statements
- Parallel search execution
- Connection pooling for multi-tenant

**Reliability**
- Retry failed embeddings with exponential backoff
- Graceful degradation (keyword-only if vector fails)
- Read-only recovery for locked databases
- Transaction rollback on errors
