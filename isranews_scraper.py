from concurrent.futures import ThreadPoolExecutor, as_completed
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import pandas as pd
import time, random, os, json, sys, re
from tqdm import tqdm
from datetime import datetime

base_url = "https://www.isranews.org"
category_map = {
    "ข่าว": "article/isranews-news.html",
    "ศูนย์ข่าวเพื่อชุมชน": "article/community/comm-news.html",
    "ศูนย์ข่าวภาคใต้": "article/south-news/other-news.html",
    "ศูนย์ข่าวนโยบายสาธารณะ": "article/thaireform/thaireform-news.html",
    "ศูนย์ข่าวสืบสวน": "article/investigative/investigate-news.html"
}
EXPORT_FORMATS = ['csv', 'excel', 'json', 'txt']
CHECKPOINT_FILE = "isranews_checkpoint.json"

def input_categories():
    print("เลือกหมวดข่าว (เลือกหลายหมวดด้วย comma หรือ all):")
    for i, (k, v) in enumerate(category_map.items(), 1):
        print(f"  {i}. {k} ({v})")
    print("  0. กำหนด URL เอง (comma คั่นได้)")
    sel = input("เลือกหมวด (เลข, all, หรือ path เอง): ").strip().lower()
    cats = []
    if sel == "all":
        cats = list(category_map.values())
    elif sel == "0":
        url = input("ใส่ path URL ต่อจาก https://www.isranews.org/ (คั่น , ได้): ").strip()
        cats = [s.strip() for s in url.split(",") if s.strip()]
    elif "," in sel:
        nums = [int(s) for s in sel.split(",") if s.isdigit() and 1 <= int(s) <= len(category_map)]
        cats = [list(category_map.values())[i-1] for i in nums]
    elif sel.isdigit() and 1 <= int(sel) <= len(category_map):
        cats = [list(category_map.values())[int(sel)-1]]
    elif sel in category_map:
        cats = [category_map[sel]]
    elif sel.startswith("article/"):
        cats = [sel]
    else:
        print("เลือกไม่ถูกต้อง ใช้ข่าว (article/isranews-news.html) ให้")
        cats = [list(category_map.values())[0]]
    return cats

def input_page_range():
    try:
        start = int(input("ต้องการดึงข่าวจากหน้าไหน? (เริ่มหน้า, default=1): ") or "1")
        end = input("ถึงหน้าไหน? (จบหน้า, 0=ดึงจนจบ, default=1): ") or "1"
        end = int(end)
        return start, end
    except Exception:
        print("ค่าไม่ถูกต้อง ใช้ default start=1, end=1")
        return 1, 1

def input_export_format():
    print("เลือกรูปแบบไฟล์ export:")
    for i, fmt in enumerate(EXPORT_FORMATS, 1):
        print(f"  {i}. {fmt}")
    sel = input("เลือกหมายเลข (1-4, default=1): ").strip()
    if sel.isdigit() and 1 <= int(sel) <= 4:
        return EXPORT_FORMATS[int(sel) - 1]
    return 'csv'

def input_filename():
    return input("ตั้งชื่อไฟล์ผลลัพธ์ (default: isranews): ").strip() or "isranews"

def input_filter_date():
    d = input("กรองเฉพาะข่าวที่ใหม่กว่า (YYYY-MM-DD, เว้นว่าง=ไม่กรอง): ").strip()
    try:
        if d:
            parts = d.split("-")
            if len(parts) == 3 and int(parts[0]) > 2400:
                print(f"คุณกรอกปี พ.ศ. ({parts[0]}) ระบบจะแปลงเป็น ค.ศ. ({int(parts[0])-543})")
                d = f"{int(parts[0])-543}-{parts[1]}-{parts[2]}"
            return datetime.strptime(d, "%Y-%m-%d")
        else:
            return None
    except Exception:
        print("วันที่ไม่ถูกต้อง ข้ามการกรอง")
        return None

def get_news_list_from_page(html):
    soup = BeautifulSoup(html, "html.parser")
    page_news = []
    for li in soup.select("li.fc_bloglist_item"):
        a = li.select_one("h3.contentheading a")
        title = a.text.strip() if a else ""
        news_url = a['href'] if a and a.has_attr('href') else ""
        if news_url and not news_url.startswith("http"):
            news_url = base_url + news_url
        date_tag = li.select_one("div.value.field_created")
        date = date_tag.text.strip() if date_tag else ""
        page_news.append({
            "หัวข้อ": title,
            "เนื้อหา": "",
            "วันที่_raw": date,
            "วันที่": "",
            "URL": news_url,
            "หมวดหมู่ข่าว": "",
            "Tags": "",
            "ยอดวิว": ""
        })
    return page_news

def parse_datetime_thai(text: str) -> datetime | None:
    m = re.search(r"(\d{1,2})\s+([ก-๙\.]+)\s+(\d{4})(?:\s*เวลา\s*(\d{1,2}):(\d{2}))?", text)
    if not m:
        return None
    day, month_th, year_th = int(m.group(1)), m.group(2), int(m.group(3))
    hour, minute = 0, 0
    if m.group(4) and m.group(5):
        hour, minute = int(m.group(4)), int(m.group(5))
    month_map = {
        "มกราคม":1, "กุมภาพันธ์":2, "มีนาคม":3, "เมษายน":4,
        "พฤษภาคม":5, "มิถุนายน":6, "กรกฎาคม":7, "สิงหาคม":8,
        "กันยายน":9, "ตุลาคม":10, "พฤศจิกายน":11, "ธันวาคม":12,
        "ม.ค.":1, "ก.พ.":2, "มี.ค.":3, "เม.ย.":4,
        "พ.ค.":5, "มิ.ย.":6, "ก.ค.":7, "ส.ค.":8,
        "ก.ย.":9, "ต.ค.":10, "พ.ย.":11, "ธ.ค.":12
    }
    month = month_map.get(month_th)
    if not month:
        return None
    if year_th > 2400:
        year_th -= 543
    return datetime(year_th, month, day, hour, minute)

def parse_date(d: str) -> datetime | None:
    d = d.strip()
    dt = parse_datetime_thai(d)
    if dt:
        return dt
    try:
        return datetime.strptime(d, "%Y-%m-%d")
    except Exception:
        return None

def extract_full_content_and_meta(url, max_retry=2):
    for _ in range(max_retry):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(random.randint(1500, 2300))
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                content_div = soup.find("div", class_="desc-content field_text")
                texts = []
                if content_div:
                    paragraphs = content_div.find_all(['p', 'blockquote'])
                    for tag in paragraphs:
                        for img in tag.find_all('img'):
                            img.decompose()
                        txt = tag.get_text(separator=" ", strip=True)
                        if txt.strip().startswith("อ่านประกอบ"):
                            continue
                        if "อ่านประกอบ" in txt and not txt.replace("อ่านประกอบ", "").strip():
                            continue
                        if txt:
                            texts.append(txt)
                content_text = "\n\n".join(texts)
                content_text = "\n".join([
                    line for line in content_text.splitlines()
                    if not line.strip().startswith("อ่านประกอบ")
                ])
                categories_div = soup.find("div", class_="flexi value field_categories")
                categories = []
                if categories_div:
                    links = categories_div.find_all("a")[1:]
                    categories = [a.get_text(strip=True) for a in links]
                categories_text = ",".join(categories)
                tags_div = soup.find("div", class_="flexi value field_tags")
                tags = []
                if tags_div:
                    tags = [a.get_text(strip=True) for a in tags_div.find_all("a")]
                tags_text = ",".join(tags)
                hits_div = soup.find("div", class_="flexi value field_hits")
                views = ""
                if hits_div:
                    views_raw = hits_div.get_text(strip=True)
                    m = re.search(r"\d+", views_raw.replace(",", ""))
                    if m:
                        views = m.group()
                browser.close()
                return content_text, categories_text, tags_text, views
        except PlaywrightTimeout:
            time.sleep(2 + random.random())
            continue
        except Exception as e:
            print(f"ERROR at {url}: {e}")
            time.sleep(2 + random.random())
            continue
    return '[ERROR]', '', '', ''

def export_news(news_list, filename, fmt):
    for news in news_list:
        dt = parse_date(news.get("วันที่_raw", ""))
        news["วันที่"] = dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""
    df = pd.DataFrame(news_list)
    if fmt == 'csv':
        df.to_csv(filename + ".csv", index=False, encoding='utf-8-sig')
    elif fmt == 'excel':
        df.to_excel(filename + ".xlsx", index=False)
    elif fmt == 'json':
        df.to_json(filename + ".json", orient='records', force_ascii=False, indent=2)
    elif fmt == 'txt':
        with open(filename + ".txt", "w", encoding='utf-8') as f:
            for i, news in enumerate(news_list, 1):
                f.write(f"[{i}] {news['หัวข้อ']}\nวันที่: {news['วันที่']}\nหมวด: {news['หมวดหมู่ข่าว']}\nTags: {news['Tags']}\nยอดวิว: {news['ยอดวิว']}\nURL: {news['URL']}\n\n{news['เนื้อหา']}\n\n{'='*60}\n\n")
    else:
        print("ไม่รองรับ format นี้")

def save_checkpoint(filename, news_list):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

def load_checkpoint(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def scrape_category(cat_path, start, end, filter_date, scraped_urls):
    """Scrape หมวดเดียว จบใน thread"""
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page_num = start
        while True:
            page_start = (page_num - 1) * 10 if page_num > 1 else 0
            url = f"{base_url}/{cat_path}" if page_num == 1 else f"{base_url}/{cat_path}?start={page_start}"
            print(f"\n[PAGE {page_num}] {url}")
            try:
                page.goto(url, timeout=10000)
                page.wait_for_timeout(random.randint(1000, 1800))
                html = page.content()
            except Exception as e:
                print(f"ไม่สามารถโหลดหน้านี้ได้: {url} : {e}")
                break
            page_news = get_news_list_from_page(html)
            for n in page_news:
                dt = parse_date(n["วันที่_raw"])
                n["วันที่"] = dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""
                if n["URL"] in scraped_urls:
                    continue
                if filter_date is not None and (dt is None or dt < filter_date):
                    continue
                results.append(n)
                scraped_urls.add(n["URL"])
            if not page_news or (end != 0 and page_num >= end):
                break
            page_num += 1
            time.sleep(random.uniform(1.5, 3.0))
        browser.close()
    return results

if __name__ == "__main__":
    news_list = []
    if os.path.exists(CHECKPOINT_FILE):
        resume = input("พบ checkpoint เดิม ต้องการ resume? (y/n): ").strip().lower()
        if resume == "y":
            news_list = load_checkpoint(CHECKPOINT_FILE)
            print(f"อ่าน checkpoint สำเร็จ ({len(news_list)} ข่าว)")
    cat_paths = input_categories()
    start, end = input_page_range()
    filter_date = input_filter_date()
    fmt = input_export_format()
    filename = input_filename()

    # --- SCRAPING LOOP (MULTI CATEGORY, PARALLEL) ---
    scraped_urls = {news["URL"] for news in news_list}
    news_results = []
    max_workers = min(8, len(cat_paths))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future2cat = {
            executor.submit(scrape_category, cat_path, start, end, filter_date, scraped_urls): cat_path
            for cat_path in cat_paths
        }
        for future in tqdm(as_completed(future2cat), total=len(future2cat), desc="Scraping Categories"):
            news_results.extend(future.result())
    news_list.extend(news_results)
    save_checkpoint(CHECKPOINT_FILE, news_list)

    print(f"\nรวมข่าวทั้งหมด {len(news_list)} ข่าว, กำลังดึงเนื้อหาข่าวแต่ละข่าว...\n")

    # --- SCRAPE CONTENTS (Parallel URLs) ---
    max_threads = 8
    total = len(news_list)
    idx_to_page = {}
    per_page = 10
    for i, news in enumerate(news_list):
        idx_to_page[i] = (i // per_page) + start

    last_page = None
    with ThreadPoolExecutor(max_workers=max_threads) as executor, tqdm(total=total, ncols=80) as pbar:
        future_to_idx = {
            executor.submit(extract_full_content_and_meta, news['URL']): i
            for i, news in enumerate(news_list)
            if not news.get("เนื้อหา") or news.get("เนื้อหา") == "[ERROR]"
        }
        done_idx = {i for i, news in enumerate(news_list) if news.get("เนื้อหา") and news.get("เนื้อหา") != "[ERROR]"}
        for idx, future in enumerate(as_completed(future_to_idx), 1):
            i = future_to_idx[future]
            this_page = idx_to_page[i]
            if this_page != last_page:
                tqdm.write(f"\n[PAGE {this_page}]")
                last_page = this_page
            tqdm.write(f"[{i+1}/{total}] {news_list[i]['หัวข้อ']}")
            content, categories, tags, views = future.result()
            news_list[i]['เนื้อหา'] = content
            news_list[i]['หมวดหมู่ข่าว'] = categories
            news_list[i]['Tags'] = tags
            news_list[i]['ยอดวิว'] = views
            save_checkpoint(CHECKPOINT_FILE, news_list)
            pbar.update(1)
        pbar.update(len(done_idx))

    export_news(news_list, filename, fmt)
    print("\n" + "="*60)
    print(f"บันทึกข่าวทั้งหมดลงไฟล์ {filename}.{fmt} แล้ว")
    print("="*60)
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)
