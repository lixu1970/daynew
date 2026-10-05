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


def make_comment(title, summary):
    """点评取新闻正文/摘要中最后两个以句号结束的完整句子。"""
    text = clean_text(summary) or clean_text(title)
    sentences = re.findall(r"[^。]+。", text)
    if len(sentences) >= 2:
        return "".join(sentences[-2:]).strip()
    if len(sentences) == 1:
        return sentences[-1].strip()
    return text.strip()


# =========================
# 获取新闻
# =========================

def get_news(feeds, count=30):
    results = []
    seen = set()

    for source_name, url in feeds:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:
                title = clean_text(entry.get("title", ""))
                if not title:
                    continue

                # 标题归一化去重
                key = re.sub(r"\W+", "", title).lower()
                if key in seen:
                    continue
                seen.add(key)

                summary = shorten(entry.get("summary", ""))
                if not summary:
                    summary = "点击标题查看这条新闻的详细报道。"

                link = entry.get("link", "#")

                results.append({
                    "title": title,
                    "summary": summary,
                    "comment": make_comment(title, summary),
                    "link": link,
                    "source": source_name
                })

                if len(results) >= count:
                    return results

        except Exception as e:
            print("新闻源读取失败：", source_name, e)

    return results


domestic = get_news(DOMESTIC_FEEDS, 30)
world = get_news(WORLD_FEEDS, 30)


# =========================
# 新闻卡片 / 分页
# =========================

def make_cards(news_list, section):
    cards = ""

    for i, item in enumerate(news_list, 1):
        page_no = (i - 1) // 10 + 1

        title = html.escape(item["title"])
        summary = html.escape(item["summary"])
        comment = html.escape(item["comment"])
        link = html.escape(item["link"], quote=True)
        source = html.escape(item["source"])

        cards += f"""
        <div class="news news-page {section}-page-{page_no}" data-page="{page_no}">
            <h2>
                <a href="{link}" target="_blank" rel="noopener">
                    {i}．{title}
                </a>
            </h2>

            <p>{summary}</p>

            <div class="comment-box">
                <strong>点评：</strong>{comment}
            </div>

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
header_time = f"北京时间{now.strftime('%y')}年{now.month}月{now.day}日{now.strftime('%H:%M')}更新"


# =========================
# 生成网页
# =========================

page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日新闻</title>

<style>
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: #f5f6f8;
    color: #222;
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
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

.update-line {{
    margin-top: 8px;
    color: #666;
    font-size: 16px;
    white-space: nowrap;
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

.comment-box {{
    margin-top: 12px;
    padding: 11px 12px;
    background: #f1f6ff;
    border: 1px solid #d8e7ff;
    border-radius: 9px;
    font-size: 16px;
    line-height: 1.7;
    color: #333;
}}

.source {{
    margin-top: 9px;
    color: #888;
    font-size: 14px;
}}

.pagination {{
    display: flex;
    gap: 8px;
    margin: 8px 0 28px;
}}

.pagination button {{
    flex: 1;
    min-height: 44px;
    border: 1px solid #cfd4dc;
    border-radius: 9px;
    background: #1677ff;
    color: #fff;
    border-color: #1677ff;
    font-size: 16px;
    font-weight: 600;
}}

.pagination button.active {{
    background: #0958d9;
    color: #fff;
    border-color: #0958d9;
}}

.footer {{
    text-align: center;
    color: #888;
    font-size: 14px;
    margin-top: 30px;
}}

@media (max-width: 420px) {{
    .container {{
        padding-left: 12px;
        padding-right: 12px;
    }}
    .header h1 {{
        font-size: 29px;
    }}
    .update-line {{
        font-size: 15px;
    }}
    .news {{
        padding: 16px;
    }}
    .news h2 {{
        font-size: 20px;
    }}
    .news p {{
        font-size: 17px;
    }}
    .comment-box {{
        font-size: 15px;
    }}
}}
</style>
</head>

<body>
<div class="container">

    <div class="header">
        <h1>每日新闻</h1>
        <div class="update-line">{header_time}</div>
    </div>

    <div class="section-title">
        国内新闻 · 每页10条
    </div>

    <div id="domestic-news">
        {make_cards(domestic, "domestic")}
    </div>

    <div class="pagination" id="domestic-pagination">
        <button type="button" class="active" onclick="showPage('domestic', 1, this)">第一页</button>
        <button type="button" onclick="showPage('domestic', 2, this)">第二页</button>
        <button type="button" onclick="showPage('domestic', 3, this)">第三页</button>
    </div>

    <div class="section-title">
        国际新闻 · 每页10条
    </div>

    <div id="world-news">
        {make_cards(world, "world")}
    </div>

    <div class="pagination" id="world-pagination">
        <button type="button" class="active" onclick="showPage('world', 1, this)">第一页</button>
        <button type="button" onclick="showPage('world', 2, this)">第二页</button>
        <button type="button" onclick="showPage('world', 3, this)">第三页</button>
    </div>

    <div class="footer">
        每日新闻 · daynew
        <br>
        每天北京时间06:00自动更新
        <br>
        版本号：261005-2
    </div>

</div>

<script>
function showPage(section, page, clickedButton) {{
    const cards = document.querySelectorAll('.' + section + '-page-1, .' + section + '-page-2, .' + section + '-page-3');

    cards.forEach(function(card) {{
        card.style.display = (Number(card.dataset.page) === page) ? 'block' : 'none';
    }});

    const buttons = document.querySelectorAll('#' + section + '-pagination button');
    buttons.forEach(function(button) {{
        button.classList.remove('active');
    }});
    clickedButton.classList.add('active');

    const title = document.getElementById(section + '-news').previousElementSibling;
    if (title) {{
        title.scrollIntoView({{behavior: 'smooth', block: 'start'}});
    }}
}}

document.addEventListener('DOMContentLoaded', function() {{
    ['domestic', 'world'].forEach(function(section) {{
        document.querySelectorAll('.' + section + '-page-2, .' + section + '-page-3').forEach(function(card) {{
            card.style.display = 'none';
        }});
    }});
}});
</script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(page)

print(
    f"更新完成：国内 {len(domestic)} 条，"
    f"国际 {len(world)} 条；每类最多30条，三页显示"
)
