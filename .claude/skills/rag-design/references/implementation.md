# RAG Implementation Guide

## Quick Start

### 1. Setup Storage

```typescript
import Database from 'better-sqlite3';
import { loadVecExtension } from 'sqlite-vec';

const db = new Database('memory.db');
loadVecExtension(db);

// Create tables
db.exec(`
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
`);
```

### 2. Initialize Embedding Provider

```typescript
import OpenAI from 'openai';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function embed(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text,
  });
  return response.data[0].embedding;
}
```

### 3. Index Documents

```typescript
import crypto from 'crypto';

async function indexDocument(path: string, content: string) {
  const chunks = chunkText(content);

  for (const chunk of chunks) {
    const id = crypto.randomUUID();
    const hash = crypto.createHash('sha256').update(chunk.text).digest('hex');

    // Check cache
    let embedding = getCachedEmbedding(hash);
    if (!embedding) {
      embedding = await embed(chunk.text);
      cacheEmbedding(hash, embedding);
    }

    // Store chunk
    db.prepare(`
      INSERT INTO chunks (id, path, start_line, end_line, content, source, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(id, path, chunk.start, chunk.end, chunk.text, 'memory', Date.now());

    // Store vector
    db.prepare(`INSERT INTO chunks_vec (rowid, embedding) VALUES (?, ?)`).run(id, embedding);

    // Store FTS
    db.prepare(`INSERT INTO chunks_fts (chunk_id, content) VALUES (?, ?)`).run(id, chunk.text);
  }
}

function chunkText(content: string) {
  const lines = content.split('\n');
  const chunks = [];
  let current = { text: '', start: 1, end: 1 };

  for (let i = 0; i < lines.length; i++) {
    current.text += lines[i] + '\n';
    current.end = i + 1;

    if (current.text.length > 500 || i === lines.length - 1) {
      chunks.push({ ...current });
      current = { text: '', start: i + 2, end: i + 2 };
    }
  }

  return chunks.filter(c => c.text.trim());
}
```

### 4. Implement Search

```typescript
async function search(query: string, opts = { maxResults: 10 }) {
  const queryEmbedding = await embed(query);

  // Vector search
  const vectorResults = db.prepare(`
    SELECT c.*, vec_distance_L2(v.embedding, ?) as distance
    FROM chunks c
    JOIN chunks_vec v ON c.id = v.rowid
    ORDER BY distance
    LIMIT 50
  `).all(queryEmbedding);

  // Keyword search
  const ftsQuery = query.split(/\s+/).map(t => `"${t}"`).join(' AND ');
  const keywordResults = db.prepare(`
    SELECT c.*, f.rank
    FROM chunks c
    JOIN chunks_fts f ON c.id = f.chunk_id
    WHERE f.content MATCH ?
    ORDER BY f.rank
    LIMIT 50
  `).all(ftsQuery);

  // Merge
  const merged = mergeResults(vectorResults, keywordResults, {
    vectorWeight: 0.7,
    keywordWeight: 0.3
  });

  return merged.slice(0, opts.maxResults);
}

function mergeResults(vector, keyword, weights) {
  const byId = new Map();

  for (const v of vector) {
    byId.set(v.id, {
      ...v,
      score: weights.vectorWeight * (1 / (1 + v.distance))
    });
  }

  for (const k of keyword) {
    const existing = byId.get(k.id);
    const score = weights.keywordWeight * (1 / (1 + Math.abs(k.rank)));

    if (existing) {
      existing.score += score;
    } else {
      byId.set(k.id, { ...k, score });
    }
  }

  return Array.from(byId.values()).sort((a, b) => b.score - a.score);
}
```

## Advanced Features

### MMR Re-ranking

```typescript
function applyMMR(results: SearchResult[], lambda = 0.7, maxResults = 10) {
  const selected: SearchResult[] = [];
  const remaining = [...results];

  while (selected.length < maxResults && remaining.length > 0) {
    let bestIdx = 0;
    let bestScore = -Infinity;

    for (let i = 0; i < remaining.length; i++) {
      const relevance = remaining[i].score;
      const maxSim = selected.length === 0 ? 0 :
        Math.max(...selected.map(s => jaccardSimilarity(remaining[i].content, s.content)));

      const mmrScore = lambda * relevance - (1 - lambda) * maxSim;

      if (mmrScore > bestScore) {
        bestScore = mmrScore;
        bestIdx = i;
      }
    }

    selected.push(remaining[bestIdx]);
    remaining.splice(bestIdx, 1);
  }

  return selected;
}

function jaccardSimilarity(a: string, b: string): number {
  const tokensA = new Set(a.toLowerCase().match(/\w+/g) || []);
  const tokensB = new Set(b.toLowerCase().match(/\w+/g) || []);

  const intersection = new Set([...tokensA].filter(x => tokensB.has(x)));
  const union = new Set([...tokensA, ...tokensB]);

  return intersection.size / union.size;
}
```

### Temporal Decay

```typescript
function applyTemporalDecay(results: SearchResult[], halfLifeDays = 30) {
  const now = Date.now();
  const halfLifeMs = halfLifeDays * 24 * 60 * 60 * 1000;

  return results.map(r => ({
    ...r,
    score: r.score * Math.exp(-Math.log(2) * (now - r.created_at) / halfLifeMs)
  }));
}
```

### Batch Embedding

```typescript
async function batchEmbed(texts: string[], batchSize = 100) {
  const results: number[][] = [];

  for (let i = 0; i < texts.length; i += batchSize) {
    const batch = texts.slice(i, i + batchSize);
    const response = await openai.embeddings.create({
      model: 'text-embedding-3-small',
      input: batch,
    });

    results.push(...response.data.map(d => d.embedding));

    // Rate limiting
    if (i + batchSize < texts.length) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  return results;
}
```

### File Watching

```typescript
import chokidar from 'chokidar';

const watcher = chokidar.watch('memory/**/*.md', {
  ignoreInitial: true,
  awaitWriteFinish: { stabilityThreshold: 500 }
});

let updateTimer: NodeJS.Timeout | null = null;

watcher.on('change', (path) => {
  if (updateTimer) clearTimeout(updateTimer);

  updateTimer = setTimeout(async () => {
    const content = await fs.readFile(path, 'utf-8');
    await reindexDocument(path, content);
  }, 1000);
});
```

## Production Checklist

- [ ] Implement embedding cache with content hashing
- [ ] Add retry logic with exponential backoff
- [ ] Set up file watching for auto-reindexing
- [ ] Configure batch sizes for API limits
- [ ] Add progress callbacks for long operations
- [ ] Implement graceful degradation (keyword-only fallback)
- [ ] Set up monitoring for embedding costs
- [ ] Add database backup strategy
- [ ] Implement connection pooling for concurrent access
- [ ] Configure appropriate chunk sizes for your content
