"""演示脚本"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.retriever import hybrid_search
from src.qa import answer_question

def demo_search():
    print("\n=== 混合检索演示 ===")
    query = "心脏病治疗"
    results = hybrid_search(query, top_k=3)
    print(f"\n查询: {query}")
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r.doctor_name} - {r.hospital} ({r.department})")
        print(f"   评分: {r.rating}星 | 相似度: {r.score:.3f}")
        print(f"   内容: {r.content[:50]}...")

def demo_qa():
    print("\n\n=== 问答演示 ===")
    questions = [
        "张医生的患者评价怎么样？",
        "哪家医院的骨科比较好？"
    ]

    for q in questions:
        print(f"\n问题: {q}")
        result = answer_question(q, top_k=3)
        print(f"回答: {result['answer']}")
        print(f"来源: {len(result['sources'])} 条评价")

if __name__ == '__main__':
    demo_search()
    demo_qa()
