"""混合检索器 - 核心检索逻辑"""
import numpy as np
import math
from datetime import datetime
from dataclasses import dataclass
from src.database import get_connection
from src.embeddings import get_embedding

@dataclass
class SearchResult:
    id: int
    doctor_name: str
    hospital: str
    department: str
    content: str
    rating: int
    created_at: str
    score: float
    embedding: list[float] = None

def vector_search(query_embedding: list[float], top_k: int = 50) -> list[SearchResult]:
    """向量相似度检索"""
    conn = get_connection()
    query_blob = np.array(query_embedding, dtype=np.float32).tobytes()

    results = conn.execute("""
        SELECT r.*, vec_distance_L2(v.embedding, ?) as distance, v.embedding
        FROM reviews r
        JOIN reviews_vec v ON r.id = v.rowid
        ORDER BY distance
        LIMIT ?
    """, (query_blob, top_k)).fetchall()

    conn.close()

    return [SearchResult(
        id=row[0], doctor_name=row[1], hospital=row[2], department=row[3],
        content=row[4], rating=row[5], created_at=row[6],
        score=1 / (1 + row[8]), embedding=np.frombuffer(row[9], dtype=np.float32).tolist()
    ) for row in results]

def fts_search(query: str, top_k: int = 50) -> list[SearchResult]:
    """FTS5关键词检索"""
    conn = get_connection()

    results = conn.execute("""
        SELECT r.*, f.rank
        FROM reviews r
        JOIN reviews_fts f ON r.id = f.rowid
        WHERE f.content MATCH ?
        ORDER BY f.rank
        LIMIT ?
    """, (query, top_k)).fetchall()

    conn.close()

    return [SearchResult(
        id=row[0], doctor_name=row[1], hospital=row[2], department=row[3],
        content=row[4], rating=row[5], created_at=row[6],
        score=1 / (1 + abs(row[8]))
    ) for row in results]

def rrf_fusion(vec_results: list[SearchResult], fts_results: list[SearchResult], k: int = 60) -> dict:
    """RRF融合算法"""
    scores = {}
    for rank, result in enumerate(vec_results, 1):
        scores[result.id] = scores.get(result.id, {'result': result, 'score': 0})
        scores[result.id]['score'] += 1 / (k + rank)
    for rank, result in enumerate(fts_results, 1):
        scores[result.id] = scores.get(result.id, {'result': result, 'score': 0})
        scores[result.id]['score'] += 1 / (k + rank)
    return scores

def apply_time_decay(results: list[SearchResult], decay_rate: float = 0.1) -> list[SearchResult]:
    """应用时间衰减"""
    from datetime import timezone
    now = datetime.now(timezone.utc)
    for result in results:
        try:
            created = datetime.fromisoformat(result.created_at.replace('Z', '+00:00'))
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            days_old = (now - created).days
            decay_factor = math.exp(-decay_rate * days_old / 365)
            result.score *= decay_factor
        except:
            pass  # 跳过无效时间
    return results

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """余弦相似度"""
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def mmr_rerank(results: list[SearchResult], lambda_param: float = 0.7, max_results: int = 10) -> list[SearchResult]:
    """MMR重排序"""
    selected, remaining = [], results.copy()
    while len(selected) < max_results and remaining:
        best_idx, best_score = 0, float('-inf')
        for i, result in enumerate(remaining):
            relevance = result.score
            max_sim = max(cosine_similarity(result.embedding, s.embedding) for s in selected if s.embedding) if selected and result.embedding else 0
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr_score > best_score:
                best_score, best_idx = mmr_score, i
        selected.append(remaining.pop(best_idx))
    return selected

def hybrid_search(query: str, top_k: int = 10) -> list[SearchResult]:
    """混合检索主函数"""
    query_embedding = get_embedding(query)
    vec_results = vector_search(query_embedding, top_k=50)
    try:
        fts_results = fts_search(query, top_k=50)
    except:
        fts_results = []
    scores = rrf_fusion(vec_results, fts_results)
    merged = [item['result'] for item in scores.values()]
    for result in merged:
        result.score = scores[result.id]['score']
    merged = apply_time_decay(merged, decay_rate=0.1)
    merged.sort(key=lambda x: x.score, reverse=True)
    if len(merged) > top_k and any(r.embedding for r in merged[:20]):
        merged = mmr_rerank(merged[:20], lambda_param=0.7, max_results=top_k)
    else:
        merged = merged[:top_k]
    return merged
