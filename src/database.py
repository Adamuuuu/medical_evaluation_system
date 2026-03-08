"""数据库连接和schema管理"""
import sqlite3
import os
from pathlib import Path

DB_PATH = os.getenv('DATABASE_PATH', './medical_reviews.db')

def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.enable_load_extension(True)

    # 尝试加载sqlite-vec扩展
    for ext in ['vec0', './vec0', './vec0.dll', './vec0.so', './vec0.dylib']:
        try:
            conn.load_extension(ext)
            break
        except:
            continue

    return conn

def init_database():
    """初始化数据库schema"""
    conn = get_connection()

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            doctor_name TEXT NOT NULL,
            hospital TEXT NOT NULL,
            department TEXT,
            content TEXT NOT NULL,
            rating INTEGER,
            created_at TEXT,
            tags TEXT
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS reviews_vec USING vec0(
            embedding FLOAT[1024]
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS reviews_fts USING fts5(
            content, doctor_name, hospital, department
        );
    """)

    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")
