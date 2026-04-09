from playwright.sync_api import sync_playwright
import time
import json
import random
from datetime import datetime

#search posts by keywords
KEYWORDS = ["ai", "IT", "dior"]
TOP_POSTS = 0  #Parse the top posts: enter the number of posts required, recommended: 30–50 posts per keyword
NEW_POSTS = 0  #if not required, leave as 0

#A feature is to collect posts from specific accounts
ACCOUNTS = [" "] #If you don't need acc - leave empty [ ]
ACC_POSTS = 3 #how many posts to scrape

#access to your Treads account
USERNAME = "hello.world"
PASSWORD = "qwerty"

def login(page):
    print("🔐 Logging in...")

    page.goto("https://www.threads.net/login")
    time.sleep(2)

    page.fill('input[autocomplete="username"]', USERNAME)
    time.sleep(1)

    page.fill('input[type="password"]', PASSWORD)
    time.sleep(1)

    page.keyboard.press("Enter")

    time.sleep(8)

    print("✅ Logged in")

def normalize_likes(raw):
    if not raw:
        return 0

    raw = raw.lower().replace(" ", "").replace("\xa0", "").replace(",", "")

    try:
        if "тис" in raw:
            return int(float(raw.replace("тис.", "").replace("тис", "")) * 1000)

        if "k" in raw:
            return int(float(raw.replace("k", "")) * 1000)

        if raw.isdigit():
            return int(raw)

    except:
        pass

    return 0
def parse_feed(page, keyword, mode="top", limit=10):

    if mode == "top":
        url = f"https://www.threads.net/search?q={keyword}"
    elif mode == "new":
        url = f"https://www.threads.net/search?q={keyword}&filter=recent"

    print(f"\n🔎 Searching ({mode.upper()}): {keyword}")
    page.goto(url)
    time.sleep(4)

    collected = []
    seen_texts = set()

    while len(collected) < limit:
        posts = page.locator('div[data-pressable-container="true"]').all()
        for post in posts:
            try:
                text_spans = post.locator('div.x1a6qonq span[dir="auto"] > span').all()
                text = "\n".join([t.inner_text() for t in text_spans if t.inner_text().strip() != ""])
                if not text or text in seen_texts:
                    continue
                seen_texts.add(text)

                date_str = "unknown"
                timestamp = ""
                try:
                    datetime_raw = post.locator("time").first.get_attribute("datetime")
                    timestamp = datetime_raw
                    dt = datetime.fromisoformat(datetime_raw.replace("Z", "+00:00"))
                    date_str = dt.strftime("%m/%d/%y")
                except:
                    pass

                raw_likes = ""
                likes = 0
                try:
                    like_span = (
                        post
                        .locator('svg[aria-label="Подобається"]')
                        .locator('..')
                        .locator('..')
                        .locator('span.x1o0tod')
                    )
                    raw_likes = like_span.first.inner_text().strip()
                    likes = normalize_likes(raw_likes)
                except:
                    raw_likes = "0"
                    likes = 0

                collected.append({
                    "date": date_str,
                    "timestamp": timestamp,
                    "text": text.strip(),
                    "likes": likes,
                    "likes_raw": raw_likes,
                    "keyword": keyword,
                    "mode": mode
                })

                if len(collected) >= limit:
                    break

            except:
                continue

        page.mouse.wheel(0, 4000)
        time.sleep(random.uniform(1.5, 2.5))

    return collected
def parse_account_posts(page, account, limit=10):

    url = f"https://www.threads.net/@{account}"
    print(f"\n🔎 Searching posts from account: {account}")
    page.goto(url)
    time.sleep(4)

    collected = []
    seen_texts = set()

    while len(collected) < limit:
        posts = page.locator('div[data-pressable-container="true"]').all()
        for post in posts:
            try:
                text_spans = post.locator('div.x1a6qonq span[dir="auto"] > span').all()
                text = "\n".join([t.inner_text() for t in text_spans if t.inner_text().strip() != ""])
                if not text or text in seen_texts:
                    continue
                seen_texts.add(text)

                date_str = "unknown"
                timestamp = ""
                try:
                    datetime_raw = post.locator("time").first.get_attribute("datetime")
                    timestamp = datetime_raw
                    dt = datetime.fromisoformat(datetime_raw.replace("Z", "+00:00"))
                    date_str = dt.strftime("%m/%d/%y")
                except:
                    pass

                raw_likes = ""
                likes = 0
                try:
                    like_span = (
                        post
                        .locator('svg[aria-label="Подобається"]')
                        .locator('..')
                        .locator('..')
                        .locator('span.x1o0tod')
                    )
                    raw_likes = like_span.first.inner_text().strip()
                    likes = normalize_likes(raw_likes)
                except:
                    raw_likes = "0"
                    likes = 0

                collected.append({
                    "account": account,
                    "date": date_str,
                    "timestamp": timestamp,
                    "text": text.strip(),
                    "likes": likes,
                    "likes_raw": raw_likes

                })

                if len(collected) >= limit:
                    break

            except:
                continue

        page.mouse.wheel(0, 4000)
        time.sleep(random.uniform(1.5, 2.5))

    return collected
def save_to_json(posts, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(posts)} posts to {filename}")

def run():
    top_posts_all = []
    new_posts_all = []
    acc_posts_all = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page)

        for keyword in KEYWORDS:
            if TOP_POSTS > 0:
                top_posts = parse_feed(page, keyword, mode="top", limit=TOP_POSTS)
                top_posts_all.extend(top_posts)
            if NEW_POSTS > 0:
                new_posts = parse_feed(page, keyword, mode="new", limit=NEW_POSTS)
                new_posts_all.extend(new_posts)


        if ACC_POSTS > 0:
            for account in ACCOUNTS:
                posts = parse_account_posts(page, account, limit=ACC_POSTS)
                acc_posts_all.extend(posts)

        browser.close()


    if top_posts_all:
        save_to_json(top_posts_all, "top_posts.json")
    if new_posts_all:
        save_to_json(new_posts_all, "new_posts.json")
    if acc_posts_all:
        save_to_json(acc_posts_all, "account_posts.json")


if __name__ == "__main__":
    run()