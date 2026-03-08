"""初始化数据库"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.database import init_database

if __name__ == '__main__':
    init_database()
