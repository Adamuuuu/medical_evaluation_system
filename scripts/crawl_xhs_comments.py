"""小红书医疗评论爬虫 - 精简版"""
import asyncio
import sys
import os
from pathlib import Path

# 添加MediaCrawler到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "MediaCrawler"))

from playwright.async_api import async_playwright
from media_platform.xhs.client import XiaoHongShuClient
from media_platform.xhs.help import parse_note_info_from_note_url
import sqlite3
from datetime import datetime

class SimpleXHSCrawler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    async def crawl_note_comments(self, note_url: str, max_comments: int = 50):
        """爬取指定笔记的评论"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(user_agent=self.user_agent)
            await context.add_init_script(path=str(Path(__file__).parent.parent / "MediaCrawler/libs/stealth.min.js"))

            page = await context.new_page()
            await page.goto("https://www.xiaohongshu.com")

            # 等待登录
            print("请在浏览器中登录小红书，登录后按回车继续...")
            input()

            cookies = await context.cookies()
            cookie_dict = {c['name']: c['value'] for c in cookies}

            # 验证登录
            if 'a1' not in cookie_dict or not cookie_dict['a1']:
                print("错误：未检测到登录信息，请确保已登录")
                await browser.close()
                return []

            # 创建客户端
            client = XiaoHongShuClient(
                timeout=60,
                headers={"User-Agent": self.user_agent},
                playwright_page=page,
                cookie_dict=cookie_dict
            )

            # 解析笔记信息
            note_info = parse_note_info_from_note_url(note_url)
            note_id = note_info.note_id
            xsec_token = note_info.xsec_token

            print(f"开始爬取笔记 {note_id} 的评论...")

            # 获取评论
            comments = await client.get_note_all_comments(
                note_id=note_id,
                xsec_token=xsec_token,
                max_count=max_comments,
                crawl_interval=1.0
            )

            # 保存到数据库
            self._save_comments(comments, note_url)

            await browser.close()
            return comments

    def _save_comments(self, comments: list, source_url: str):
        """保存评论到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        saved = 0
        for comment in comments:
            content = comment.get('content', '')
            user_info = comment.get('user_info', {})

            cursor.execute("""
                INSERT INTO reviews
                (content, doctor_name, hospital, department, rating, created_at, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                content,
                user_info.get('nickname', '匿名用户'),
                '小红书来源',
                '待分类',
                5,  # 默认评分
                datetime.now().isoformat(),
                source_url
            ))
            saved += 1

        conn.commit()
        conn.close()
        print(f"已保存 {saved} 条评论到数据库")

async def main():
    if len(sys.argv) < 2:
        print("用法: python crawl_xhs_comments.py <小红书笔记URL>")
        print("示例: python crawl_xhs_comments.py 'https://www.xiaohongshu.com/explore/xxx?xsec_token=xxx'")
        return

    note_url = sys.argv[1]
    db_path = Path(__file__).parent.parent / "medical_reviews.db"

    crawler = SimpleXHSCrawler(str(db_path))
    comments = await crawler.crawl_note_comments(note_url, max_comments=50)
    print(f"爬取完成，共获取 {len(comments)} 条评论")

if __name__ == "__main__":
    asyncio.run(main())
