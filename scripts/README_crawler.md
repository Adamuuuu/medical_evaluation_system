# 小红书评论爬虫使用说明

## 快速开始

### 1. 安装依赖
```bash
cd MediaCrawler
pip install -r requirements.txt
cd ..
```

### 2. 获取小红书笔记URL
- 打开小红书网页版
- 找到医疗相关笔记
- 复制完整URL（必须包含 `xsec_token` 参数）

### 3. 运行爬虫
```bash
python scripts/crawl_xhs_comments.py "https://www.xiaohongshu.com/explore/xxx?xsec_token=xxx"
```

### 4. 测试问答
```bash
python scripts/test_qa.py
```

## 注意事项
- 首次运行需要手动登录小红书（15秒等待时间）
- 爬取速度：每条评论间隔1秒
- 默认最多爬取50条评论
- 评论会自动保存到 `medical_reviews.db`
