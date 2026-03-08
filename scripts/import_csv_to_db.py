"""导入CSV评论到数据库"""
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

csv_file = Path(__file__).parent.parent / "MediaCrawler/data/xhs/csv/search_comments_2026-03-08.csv"
db_file = Path(__file__).parent.parent / "medical_reviews.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        cursor.execute("""
            INSERT INTO reviews (content, doctor_name, hospital, department, rating, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row['content'],
            row['nickname'],
            '小红书',
            '待分类',
            5,
            datetime.now().isoformat()
        ))
        count += 1

conn.commit()
conn.close()
print(f"导入完成，共 {count} 条评论")
