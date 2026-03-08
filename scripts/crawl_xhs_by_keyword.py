"""小红书关键词搜索爬虫"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "MediaCrawler"))

from playwright.async_api import async_playwright
from media_platform.xhs.client import XiaoHongShuClient
from media_platform.xhs.field import SearchSortType
import sqlite3
from datetime import datetime

class KeywordXHSCrawler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    async def search_and_crawl(self, keyword: str, max_notes: int = 10, comments_per_note: int = 10):
        """搜索关键词并爬取评论"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(user_agent=self.user_agent)
            await context.add_init_script(path=str(Path(__file__).parent.parent / "MediaCrawler/libs/stealth.min.js"))

            page = await context.new_page()
            await page.goto("https://www.xiaohongshu.com")

            print("请在浏览器中登录小红书，登录后按回车继续...")
            input()

            cookies = await context.cookies()
            cookie_dict = {c['name']: c['value'] for c in cookies}

            if 'a1' not in cookie_dict or not cookie_dict['a1']:
                print("错误：未检测到登录信息")
                await browser.close()
                return

            client = XiaoHongShuClient(
                timeout=60,
                headers={"User-Agent": self.user_agent},
                playwright_page=page,
                cookie_dict=cookie_dict
            )

            print(f"搜索关键词: {keyword}")
            search_result = await client.get_note_by_keyword(keyword, page_size=max_notes)

            notes = search_result.get('items', [])[:max_notes]
            print(f"找到 {len(notes)} 条笔记")

            total_comments = 0
            for i, note in enumerate(notes, 1):
                note_id = note.get('id') or note.get('note_id')
                xsec_token = note.get('xsec_token', '')
                title = note.get('title', '无标题')

                print(f"\n[{i}/{len(notes)}] 爬取: {title[:30]}")

                try:
                    comments = await client.get_note_all_comments(
                        note_id=note_id,
                        xsec_token=xsec_token,
                        max_count=comments_per_note,
                        crawl_interval=1.0
                    )
                    self._save_comments(comments, note_id, title)
                    total_comments += len(comments)
                    print(f"  获取 {len(comments)} 条评论")
                except Exception as e:
                    print(f"  失败: {e}")

                await asyncio.sleep(2)

            await browser.close()
            print(f"\n完成！共保存 {total_comments} 条评论")

    def _save_comments(self, comments: list, note_id: str, note_title: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for comment in comments:
            content = comment.get('content', '')
            user_info = comment.get('user_info', {})

            cursor.execute("""
                INSERT INTO reviews
                (content, doctor_name, hospital, department, rating, created_at, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                content,
                user_info.get('nickname', '匿名'),
                note_title[:50],
                '小红书',
                5,
                datetime.now().isoformat(),
                f"xhs://{note_id}"
            ))

        conn.commit()
        conn.close()

async def main():
    if len(sys.argv) < 2:
        print("用法: python crawl_xhs_by_keyword.py <关键词> [笔记数量] [每篇评论数]")
        print("示例: python crawl_xhs_by_keyword.py 北京协和医院 10 10")
        return

    keyword = sys.argv[1]
    max_notes = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    comments_per_note = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    db_path = Path(__file__).parent.parent / "medical_reviews.db"
    crawler = KeywordXHSCrawler(str(db_path))
    await crawler.search_and_crawl(keyword, max_notes, comments_per_note)

if __name__ == "__main__":
    asyncio.run(main())
