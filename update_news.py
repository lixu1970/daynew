import feedparser
import html
import re
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================
# 新闻源
# =========================

DOMESTIC_FEEDS = [
    ("中新网", "https://www.chinanews.com.cn/rss/china.xml"),
    ("中新网要闻", "https://www.chinanews.com.cn/rss/importnews.xml"),
    ("Google新闻", "https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"),
]

WORLD_FEEDS = [
    ("中新网国际", "https://www.chinanews.com.cn/rss/world.xml"),
    ("Google国际", "https://news.google.com/rss/headlines/section/topic/WORLD?hl=zh-CN&gl=CN&ceid=CN:zh-Hans"),
]

# =========================
# 文字处理
# =========================

def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def shorten(text, limit=180):
    text = clean_text(text)

    if len(text) > limit:
        return text[:limit].rstrip("，。；： ") + "……"

    return text


# =========================
# 获取新闻
# =========================

def get_news(feeds, count=10):

    results = []
    seen = set()

    for source_name, url in feeds:

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:

                title = clean_text(entry.get("title", ""))

                if not title:
                    continue

                # 简单去重
                key = re.sub(r"\W+", "", title)

                if key in seen:
                    continue

                seen.add(key)

                summary = entry.get("summary", "")
                summary = shorten(summary)

                if not summary:
                    summary = "点击标题查看这条新闻的详细报道。"

                link = entry.get("link", "#")

                results.append({
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "source": source_name
                })

                if len(results) >= count:
                    return results

        except Exception as e:
            print("新闻源读取失败：", source_name, e)

    return results


domestic = get_news(DOMESTIC_FEEDS, 10)
world = get_news(WORLD_FEEDS, 10)


# =========================
# 新闻卡片
# =========================

def make_cards(news_list):

    cards = ""

    for i, item in enumerate(news_list, 1):

        title = html.escape(item["title"])
        summary = html.escape(item["summary"])
        link = html.escape(item["link"], quote=True)
        source = html.escape(item["source"])

        cards += f"""
        <div class="news">
            <h2>
                <a href="{link}" target="_blank" rel="noopener">
                    {i}．{title}
                </a>
            </h2>

            <p>{summary}</p>

            <div class="source">
                来源：{source} · 点击标题查看原文
            </div>
        </div>
        """

    return cards


# =========================
# 北京时间
# =========================

now = datetime.now(ZoneInfo("Asia/Shanghai"))

date_text = (
    f"{now.year}年"
    f"{now.month}月"
    f"{now.day}日"
)

update_time = now.strftime("%H:%M")


# =========================
# 生成网页
# =========================

page = f"""<!DOCTYPE html>
<html lang="zh-CN">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>每日新闻</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: #f5f6f8;
    color: #222;

    font-family:
    -apple-system,
    BlinkMacSystemFont,
    "PingFang SC",
    "Microsoft YaHei",
    sans-serif;

    line-height: 1.75;
}}

.container {{
    max-width: 760px;
    margin: 0 auto;
    padding: 20px 16px 50px;
}}

.header {{
    text-align: center;
    padding: 22px 10px 18px;
}}

.header h1 {{
    margin: 0;
    font-size: 32px;
}}

.date {{
    margin-top: 8px;
    color: #666;
    font-size: 17px;
}}

.update {{
    margin-top: 3px;
    color: #999;
    font-size: 14px;
}}

.section-title {{
    margin: 22px 0 12px;
    padding-left: 10px;
    border-left: 5px solid #333;
    font-size: 25px;
    font-weight: bold;
}}

.news {{
    background: white;
    margin-bottom: 14px;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}

.news h2 {{
    margin: 0 0 8px;
    font-size: 21px;
    line-height: 1.45;
}}

.news h2 a {{
    color: #222;
    text-decoration: none;
}}

.news p {{
    margin: 0;
    font-size: 18px;
    line-height: 1.8;
}}

.source {{
    margin-top: 9px;
    color: #888;
    font-size: 14px;
}}

.footer {{
    text-align: center;
    color: #888;
    font-size: 14px;
    margin-top: 30px;
}}

</style>

</head>

<body>

<div class="container">

    <div class="header">

        <h1>每日新闻</h1>

        <div class="date">
            {date_text}
        </div>

        <div class="update">
            北京时间 {update_time} 更新
        </div>

    </div>


    <div class="section-title">
        国内新闻 · {len(domestic)}条
    </div>

    {make_cards(domestic)}


    <div class="section-title">
        国际新闻 · {len(world)}条
    </div>

    {make_cards(world)}


    <div class="footer">
        每日新闻 · daynew
        <br>
        每天北京时间06:00自动更新
    </div>

</div>

</body>
</html>
"""


# =========================
# 写入 index.html
# =========================

with open(
    "index.html",
    "w",
    encoding="utf-8"
) as f:

    f.write(page)


print(
    f"更新完成：国内 {len(domestic)} 条，"
    f"国际 {len(world)} 条"
)
