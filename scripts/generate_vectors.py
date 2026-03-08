"""为数据库中的评论生成向量索引"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.database import get_connection
from src.embeddings import get_embedding
import numpy as np

conn = get_connection()
cursor = conn.cursor()

# 获取所有评论
cursor.execute("SELECT id, content, doctor_name, hospital, department FROM reviews")
reviews = cursor.fetchall()

print(f"开始为 {len(reviews)} 条评论生成向量...")

# 清空旧向量
cursor.execute("DELETE FROM reviews_vec")
cursor.execute("DELETE FROM reviews_fts")

# 生成向量和全文索引
for i, (review_id, content, doctor, hospital, dept) in enumerate(reviews, 1):
    embedding = get_embedding(content)
    embedding_blob = np.array(embedding, dtype=np.float32).tobytes()
    cursor.execute("INSERT INTO reviews_vec(rowid, embedding) VALUES (?, ?)", (review_id, embedding_blob))
    cursor.execute("INSERT INTO reviews_fts(rowid, content, doctor_name, hospital, department) VALUES (?, ?, ?, ?, ?)",
                   (review_id, content, doctor, hospital, dept or ''))

    if i % 10 == 0:
        print(f"已处理 {i}/{len(reviews)}")

conn.commit()
conn.close()
print("向量索引生成完成！")
