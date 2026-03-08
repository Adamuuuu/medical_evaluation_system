"""RAG问答系统"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from src.retriever import hybrid_search

load_dotenv()

client = OpenAI(
    api_key=os.getenv('WQ_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE')
)
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4')

def answer_question(question: str, top_k: int = 5) -> dict:
    """基于检索的问答"""
    relevant_reviews = hybrid_search(question, top_k=top_k)

    context = "\n\n".join([
        f"评价{i+1}：{r.content}\n医生：{r.doctor_name}\n医院：{r.hospital}\n科室：{r.department}\n评分：{r.rating}星\n时间：{r.created_at}"
        for i, r in enumerate(relevant_reviews)
    ])

    prompt = f"""基于以下医疗评价回答问题。注意：
- 仅基于提供的评价内容回答
- 如果评价中没有相关信息，明确说明
- 考虑评价的时效性和评分

问题：{question}

相关评价：
{context}

请提供专业、客观的回答："""

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "你是医疗评价分析助手，基于用户评价提供客观分析。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": relevant_reviews
    }
