"""测试问答系统"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.qa import answer_question

def main():
    questions = [
        "推荐哪些医院",
        # "患者对医院的服务满意吗？",
        # "有没有关于治疗效果的评价？"
    ]

    for q in questions:
        print(f"\n问题: {q}")
        print("-" * 50)
        result = answer_question(q, top_k=3)
        print(result['answer'])
        print()

if __name__ == "__main__":
    main()
