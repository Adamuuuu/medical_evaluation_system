"""索引示例数据"""
import json
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.indexer import index_reviews_batch

if __name__ == '__main__':
    with open('data/sample_reviews.json', 'r', encoding='utf-8') as f:
        reviews = json.load(f)

    print(f"开始索引 {len(reviews)} 条评价...")
    index_reviews_batch(reviews)
    print("✓ 索引完成")
