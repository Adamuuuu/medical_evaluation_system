# RAG Configuration Guide

## Embedding Providers

### OpenAI

```typescript
{
  provider: 'openai',
  model: 'text-embedding-3-small',  // 1536 dims, $0.02/1M tokens
  // model: 'text-embedding-3-large',  // 3072 dims, $0.13/1M tokens
  apiKey: process.env.OPENAI_API_KEY,
  batchSize: 100,
  maxRetries: 3
}
```

### Google Gemini

```typescript
{
  provider: 'gemini',
  model: 'text-embedding-004',  // 768 dims, free tier available
  apiKey: process.env.GEMINI_API_KEY,
  batchSize: 100
}
```

### Voyage AI

```typescript
{
  provider: 'voyage',
  model: 'voyage-2',  // 1024 dims, optimized for retrieval
  apiKey: process.env.VOYAGE_API_KEY,
  batchSize: 128
}
```

### Local (node-llama-cpp)

```typescript
{
  provider: 'local',
  modelPath: './models/nomic-embed-text-v1.5.Q8_0.gguf',
  dimensions: 768,
  contextSize: 2048
}
```

## Search Parameters

### Hybrid Search Weights

```typescript
{
  vectorWeight: 0.7,    // Semantic similarity (0-1)
  keywordWeight: 0.3,   // Keyword matching (0-1)
  // Sum should equal 1.0
}
```

**Tuning Guide:**
- High vector weight (0.8+): Prioritize semantic meaning
- Balanced (0.5-0.7): General purpose
- High keyword weight (0.8+): Exact term matching

### MMR Configuration

```typescript
{
  enabled: true,
  lambda: 0.7,  // 0=max diversity, 1=max relevance
  maxResults: 10
}
```

**Lambda tuning:**
- 0.9-1.0: Prioritize relevance (may have duplicates)
- 0.6-0.8: Balanced
- 0.3-0.5: Prioritize diversity (may sacrifice relevance)

### Temporal Decay

```typescript
{
  enabled: true,
  halfLifeDays: 30,  // Time for score to decay by 50%
  minScore: 0.1      // Floor to prevent zero scores
}
```

**Half-life tuning:**
- 7 days: Strong recency bias (news, updates)
- 30 days: Moderate recency (general knowledge)
- 90+ days: Weak recency (stable documentation)

## Chunking Strategy

### By Paragraph

```typescript
{
  strategy: 'paragraph',
  maxChunkSize: 500,     // characters
  overlap: 50,           // character overlap between chunks
  minChunkSize: 100      // skip very small chunks
}
```

### By Section

```typescript
{
  strategy: 'section',
  delimiter: /^#{1,3}\s/m,  // Markdown headers
  maxChunkSize: 1000,
  preserveHeaders: true
}
```

### Fixed Size

```typescript
{
  strategy: 'fixed',
  chunkSize: 512,    // tokens or characters
  overlap: 128
}
```

## Caching

### Embedding Cache

```typescript
{
  enabled: true,
  maxEntries: 10000,     // LRU eviction
  ttl: 30 * 24 * 60 * 60 * 1000,  // 30 days
  hashAlgorithm: 'sha256'
}
```

### Query Cache

```typescript
{
  enabled: true,
  maxEntries: 1000,
  ttl: 5 * 60 * 1000,  // 5 minutes
  keyFields: ['query', 'maxResults', 'minScore']
}
```

## Performance Tuning

### Batch Processing

```typescript
{
  batchSize: 100,           // embeddings per batch
  concurrency: 3,           // parallel batches
  delayMs: 100,             // delay between batches
  maxRetries: 3,
  retryDelayMs: 1000
}
```

### Database

```typescript
{
  walMode: true,            // Write-Ahead Logging
  cacheSize: 10000,         // pages
  mmapSize: 30000000000,    // 30GB
  busyTimeout: 5000         // ms
}
```

### File Watching

```typescript
{
  enabled: true,
  debounceMs: 1000,         // wait before reindexing
  ignorePatterns: [
    '**/node_modules/**',
    '**/.git/**',
    '**/dist/**'
  ]
}
```

## Recommended Configurations

### Small Dataset (<1000 docs)

```typescript
{
  provider: 'openai',
  model: 'text-embedding-3-small',
  vectorWeight: 0.7,
  mmr: { enabled: true, lambda: 0.7 },
  temporalDecay: { enabled: false },
  chunkSize: 500,
  batchSize: 100
}
```

### Medium Dataset (1K-10K docs)

```typescript
{
  provider: 'gemini',
  model: 'text-embedding-004',
  vectorWeight: 0.6,
  mmr: { enabled: true, lambda: 0.6 },
  temporalDecay: { enabled: true, halfLifeDays: 30 },
  chunkSize: 512,
  batchSize: 100,
  cache: { enabled: true, maxEntries: 5000 }
}
```

### Large Dataset (10K+ docs)

```typescript
{
  provider: 'local',
  modelPath: './models/nomic-embed.gguf',
  vectorWeight: 0.5,
  mmr: { enabled: true, lambda: 0.5 },
  temporalDecay: { enabled: true, halfLifeDays: 60 },
  chunkSize: 256,
  batchSize: 200,
  concurrency: 5,
  cache: { enabled: true, maxEntries: 10000 }
}
```

## Cost Optimization

### Reduce Embedding Costs

1. **Use smaller models**: `text-embedding-3-small` vs `large`
2. **Enable caching**: Avoid re-embedding unchanged content
3. **Batch requests**: Reduce API overhead
4. **Chunk efficiently**: Balance granularity vs volume
5. **Use local models**: Zero API costs for high volume

### Reduce Latency

1. **Parallel search**: Run vector + keyword concurrently
2. **Connection pooling**: Reuse database connections
3. **Prepared statements**: Pre-compile SQL queries
4. **Index optimization**: Add indexes on frequently queried fields
5. **Limit results**: Fetch only what's needed
