"""OpenAI嵌入API封装"""
import os
from openai import OpenAI

# 使用阿里云百炼 embedding
client = OpenAI(
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-v4')

def get_embedding(text: str) -> list[float]:
    """生成单个文本的嵌入向量"""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """批量生成嵌入向量"""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [d.embedding for d in response.data]
