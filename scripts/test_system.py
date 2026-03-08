"""系统测试脚本 - 验证依赖、模型和功能"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def test_dependencies():
    """测试依赖安装"""
    print("=== 测试依赖安装 ===")
    try:
        import openai
        print("✓ openai")
        import numpy
        print("✓ numpy")
        from dotenv import load_dotenv
        print("✓ python-dotenv")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        return False

def test_env_config():
    """测试环境变量配置"""
    print("\n=== 测试环境变量 ===")
    api_key = os.getenv('WQ_API_KEY')
    base_url = os.getenv('OPENAI_API_BASE')

    if not api_key:
        print("✗ WQ_API_KEY 未配置")
        return False
    print(f"✓ WQ_API_KEY: {api_key[:10]}...")

    if not base_url:
        print("✗ OPENAI_API_BASE 未配置")
        return False
    print(f"✓ OPENAI_API_BASE: {base_url}")

    return True

def test_sqlite_vec():
    """测试sqlite-vec扩展"""
    print("\n=== 测试sqlite-vec扩展 ===")
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')
        conn.enable_load_extension(True)

        for ext in ['vec0', './vec0', './vec0.dll', './vec0.so', './vec0.dylib']:
            try:
                conn.load_extension(ext)
                print(f"✓ sqlite-vec 加载成功: {ext}")
                conn.close()
                return True
            except:
                continue

        print("✗ sqlite-vec 扩展未找到")
        print("  请从 https://github.com/asg017/sqlite-vec/releases 下载")
        conn.close()
        return False
    except Exception as e:
        print(f"✗ sqlite-vec 测试失败: {e}")
        return False

def test_embedding_api():
    """测试嵌入API"""
    print("\n=== 测试嵌入API ===")
    try:
        from src.embeddings import get_embedding
        embedding = get_embedding("测试文本")
        print(f"✓ 嵌入API调用成功，维度: {len(embedding)}")
        return True
    except Exception as e:
        print(f"✗ 嵌入API调用失败: {e}")
        return False

def test_llm_api():
    """测试LLM API"""
    print("\n=== 测试LLM API ===")
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.getenv('WQ_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE')
        )
        response = client.chat.completions.create(
            model=os.getenv('LLM_MODEL', 'gpt-4'),
            messages=[{"role": "user", "content": "你好"}],
            max_tokens=10
        )
        print(f"✓ LLM API调用成功: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"✗ LLM API调用失败: {e}")
        return False

def test_database():
    """测试数据库功能"""
    print("\n=== 测试数据库功能 ===")
    try:
        from src.database import init_database
        init_database()
        print("✓ 数据库初始化成功")
        return True
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False

if __name__ == '__main__':
    results = []
    results.append(("依赖安装", test_dependencies()))
    results.append(("环境变量", test_env_config()))
    results.append(("sqlite-vec", test_sqlite_vec()))
    results.append(("嵌入API", test_embedding_api()))
    results.append(("LLM API", test_llm_api()))
    results.append(("数据库", test_database()))

    print("\n" + "="*50)
    print("测试结果汇总:")
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n总体状态:", "✓ 所有测试通过" if all_passed else "✗ 部分测试失败")
    sys.exit(0 if all_passed else 1)

