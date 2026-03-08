"""数据索引器"""
import json
import numpy as np
from src.database import get_connection
from src.embeddings import get_embedding

def index_review(review: dict):
    """索引单条评价"""
    conn = get_connection()

    # 1. 插入原始数据
    cursor = conn.execute("""
        INSERT INTO reviews (id, doctor_name, hospital, department, content, rating, created_at, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        review['id'],
        review['doctor_name'],
        review['hospital'],
        review.get('department', ''),
        review['content'],
        review['rating'],
        review['created_at'],
        json.dumps(review.get('tags', []))
    ))

    review_id = cursor.lastrowid

    # 2. 生成并存储向量
    embedding = get_embedding(review['content'])
    embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
    conn.execute("INSERT INTO reviews_vec (rowid, embedding) VALUES (?, ?)",
                 (review['id'], embedding_blob))

    # 3. 更新FTS5索引
    conn.execute("""
        INSERT INTO reviews_fts (rowid, content, doctor_name, hospital, department)
        VALUES (?, ?, ?, ?, ?)
    """, (review['id'], review['content'], review['doctor_name'],
          review['hospital'], review.get('department', '')))

    conn.commit()
    conn.close()

def index_reviews_batch(reviews: list[dict]):
    """批量索引评价"""
    for i, review in enumerate(reviews, 1):
        index_review(review)
        print(f"已索引: {i}/{len(reviews)} - {review['doctor_name']}")
