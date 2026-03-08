"""检查数据库内容"""
import sqlite3

conn = sqlite3.connect('medical_reviews.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM medical_reviews")
total = cursor.fetchone()[0]
print(f"总评论数: {total}")

cursor.execute("SELECT hospital, COUNT(*) FROM medical_reviews GROUP BY hospital")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}条")

conn.close()
