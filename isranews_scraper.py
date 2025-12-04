#!/usr/bin/env python3
import argparse
import asyncio
import logging
import os
import json
import re
import random
from datetime import datetime
from typing import List, Dict, Optional, Set, Any



import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout, Browser, Page

# --- Configuration & Constants ---
BASE_URL = "https://www.isranews.org"
CATEGORY_MAP = {
    "ศูนย์ข่าวเพื่อชุมชน": "article/community/comm-news.html",
    "ศูนย์ข่าวภาคใต้": "article/south-news/other-news.html",
    "ศูนย์ข่าวนโยบายสาธารณะ": "article/thaireform/thaireform-news.html",
    "ศูนย์ข่าวสืบสวน": "article/investigative/investigate-news.html"
}
EXPORT_FORMATS = ['csv', 'excel', 'json', 'txt']

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("IsranewsScraper")

class IsranewsScraper:
    def __init__(self, max_concurrency: int = 5, headless: bool = True):
        self.max_concurrency = max_concurrency
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def start_browser(self):
        """Initialize Playwright and Browser."""
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logger.info("Browser started.")


    async def stop_browser(self):
        """Close Browser and Playwright."""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        logger.info("Browser stopped.")

    async def _get_page_content(self, url: str, wait_min: int = 1000, wait_max: int = 2000, timeout: int = 30000) -> Optional[str]:
        """Helper to get page content using a new page in the existing browser."""
        if not self.browser:
            await self.start_browser()
        
        async with self.semaphore:
            page = None
            context = None
            try:
                context = await self.browser.new_context()
                page = await context.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
                # Random sleep to mimic human behavior
                await asyncio.sleep(random.randint(wait_min, wait_max) / 1000.0)
                content = await page.content()
                return content
            except Exception as e:
                logger.error(f"Failed to load {url}: {e}")
                return None
            finally:
                if page:
                    await page.close()
                if context:
                    await context.close()

    def parse_datetime_thai(self, text: str) -> Optional[datetime]:
        """Parse Thai datetime string to datetime object."""
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

    def parse_date(self, d: str) -> Optional[datetime]:
        """Wrapper to parse date string."""
        d = d.strip()
        dt = self.parse_datetime_thai(d)
        if dt:
            return dt
        try:
            return datetime.strptime(d, "%Y-%m-%d")
        except Exception:
            return None

    def get_news_list_from_html(self, html: str) -> List[Dict[str, Any]]:
        """Extract news items from a category page HTML."""
        soup = BeautifulSoup(html, "html.parser")
        page_news = []
        items = soup.select("li.fc_bloglist_item")
        logger.info(f"Found {len(items)} items in HTML")
        
        for li in items:
            a = li.select_one("h3.contentheading a")
            title = a.text.strip() if a else ""
            news_url = a['href'] if a and a.has_attr('href') else ""
            if news_url and not news_url.startswith("http"):
                news_url = BASE_URL + news_url
            
            date_tag = li.select_one("div.value.field_created")
            date_raw = date_tag.text.strip() if date_tag else ""
            
            page_news.append({
                "หัวข้อ": title,
                "เนื้อหา": "",
                "วันที่_raw": date_raw,
                "วันที่": "",
                "URL": news_url,
                "หมวดหมู่ข่าว": "",
                "Tags": "",
                "ยอดวิว": ""
            })
        return page_news

    async def scrape_category_pages(self, cat_path: str, start_page: int, end_page: int, filter_date: Optional[datetime], scraped_urls: Set[str]) -> List[Dict[str, Any]]:
        """Scrape news list from category pages."""
        results = []
        page_num = start_page
        
        while True:
            page_start = (page_num - 1) * 10 if page_num > 1 else 0
            url = f"{BASE_URL}/{cat_path}" if page_num == 1 else f"{BASE_URL}/{cat_path}?start={page_start}"
            logger.info(f"Scraping List: Page {page_num} - {url}")
            
            html = await self._get_page_content(url)
            if not html:
                break
                
            page_news = self.get_news_list_from_html(html)
            if not page_news:
                logger.info(f"No news found on page {page_num}. Stopping.")
                break

            valid_news_count = 0
            for n in page_news:
                dt = self.parse_date(n["วันที่_raw"])
                n["วันที่"] = dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""
                
                # Filter by URL (already scraped)
                if n["URL"] in scraped_urls:
                    continue
                
                # Filter by Date
                if filter_date is not None and (dt is None or dt < filter_date):
                    continue
                
                results.append(n)
                scraped_urls.add(n["URL"])
                valid_news_count += 1
            
            if valid_news_count == 0 and filter_date and page_news:
                 last_dt = self.parse_date(page_news[-1]["วันที่_raw"])
                 if last_dt and last_dt < filter_date:
                     logger.info("Reached news older than filter date. Stopping.")
                     break

            if end_page != 0 and page_num >= end_page:
                break
            
            page_num += 1
            
        return results

    async def extract_content(self, url: str, max_retry: int = 2) -> tuple:
        """Extract full content and metadata from a news article URL."""
        for _ in range(max_retry):
            html = await self._get_page_content(url, wait_min=1500, wait_max=2300)
            if not html:
                continue
            
            try:
                soup = BeautifulSoup(html, "html.parser")
                
                # Content
                content_div = soup.find("div", class_="desc-content field_text")
                texts = []
                if content_div:
                    paragraphs = content_div.find_all(['p', 'blockquote'])
                    for tag in paragraphs:
                        # Remove images inside text
                        for img in tag.find_all('img'):
                            img.decompose()
                        txt = tag.get_text(separator=" ", strip=True)
                        # Filter "อ่านประกอบ"
                        if txt.strip().startswith("อ่านประกอบ") or ("อ่านประกอบ" in txt and not txt.replace("อ่านประกอบ", "").strip()):
                            continue
                        if txt:
                            texts.append(txt)
                content_text = "\n\n".join(texts)
                
                # Categories
                categories_div = soup.find("div", class_="flexi value field_categories")
                categories = []
                if categories_div:
                    links = categories_div.find_all("a")[1:] 
                    categories = [a.get_text(strip=True) for a in links]
                categories_text = ",".join(categories)
                
                # Tags
                tags_div = soup.find("div", class_="flexi value field_tags")
                tags = []
                if tags_div:
                    tags = [a.get_text(strip=True) for a in tags_div.find_all("a")]
                tags_text = ",".join(tags)
                
                # Views
                hits_div = soup.find("div", class_="flexi value field_hits")
                views = ""
                if hits_div:
                    views_raw = hits_div.get_text(strip=True)
                    m = re.search(r"\d+", views_raw.replace(",", ""))
                    if m:
                        views = m.group()
                        
                return content_text, categories_text, tags_text, views
            except Exception as e:
                logger.error(f"Error parsing {url}: {e}")
                
        return '[ERROR]', '', '', ''

    async def run(self, cat_paths: List[str], start: int, end: int, filter_date: Optional[datetime], 
            filename: str, fmt: str, progress_callback=None):
        """Main execution method."""
        
        await self.start_browser()
        try:
            filename_with_ext = f"{filename}.{('xlsx' if fmt=='excel' else fmt)}"
            old_news = self.load_old_news(filename_with_ext, fmt)
            scraped_urls = {news["URL"] for news in old_news}
            
            new_news_results = []
            
            # 1. Scrape Lists
            logger.info("Starting to scrape category lists...")
            tasks = [
                self.scrape_category_pages(cat, start, end, filter_date, scraped_urls)
                for cat in cat_paths
            ]
            results = await asyncio.gather(*tasks)
            for res in results:
                new_news_results.extend(res)
                    
            news_list = self.merge_news(old_news, new_news_results)
            total_items = len(news_list)
            
            # 2. Scrape Content
            logger.info(f"Starting to scrape content for {total_items} items...")
            
            items_to_scrape = [
                (i, news) for i, news in enumerate(news_list) 
                if not news.get("เนื้อหา") or news.get("เนื้อหา") == "[ERROR]"
            ]
            
            total_to_scrape = len(items_to_scrape)
            completed_count = 0
            
            if total_to_scrape > 0:
                # Process in chunks or just create tasks (semaphore handles concurrency)
                tasks = []
                for i, news in items_to_scrape:
                    tasks.append(self.process_item_content(i, news))
                
                # Use as_completed to update progress
                for future in asyncio.as_completed(tasks):
                    i, content, categories, tags, views = await future
                    news_list[i]['เนื้อหา'] = content
                    news_list[i]['หมวดหมู่ข่าว'] = categories
                    news_list[i]['Tags'] = tags
                    news_list[i]['ยอดวิว'] = views
                    
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total_to_scrape, news_list[i]['หัวข้อ'])
                    else:
                        logger.info(f"[{completed_count}/{total_to_scrape}] Scraped: {news_list[i]['หัวข้อ']}")

            self.export_news(news_list, filename, fmt)
            logger.info(f"Done. Saved to {filename}.{fmt}")
        finally:
            await self.stop_browser()

    async def process_item_content(self, i, news):
        content, categories, tags, views = await self.extract_content(news['URL'])
        return i, content, categories, tags, views

    @staticmethod
    def load_old_news(filename: str, fmt: str) -> List[Dict]:
        if not os.path.exists(filename):
            return []
        try:
            if fmt == 'csv':
                return pd.read_csv(filename, dtype=str).fillna("").to_dict('records')
            elif fmt == 'excel':
                return pd.read_excel(filename, dtype=str).fillna("").to_dict('records')
            elif fmt == 'json':
                with open(filename, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load old file {filename}: {e}")
        return []

    @staticmethod
    def merge_news(old_news: List[Dict], new_news: List[Dict]) -> List[Dict]:
        url_to_old = {n["URL"]: n for n in old_news if "URL" in n}
        out = []
        for n in new_news:
            if n["URL"] in url_to_old:
                old_n = url_to_old[n["URL"]]
                if not old_n.get("เนื้อหา") or old_n.get("เนื้อหา") == "[ERROR]":
                     out.append(n)
                else:
                    out.append(old_n)
                del url_to_old[n["URL"]]
            else:
                out.append(n)
        for old_n in url_to_old.values():
            out.append(old_n)
        return out

    @staticmethod
    def export_news(news_list: List[Dict], filename: str, fmt: str):
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

# --- CLI Helper Functions ---
def parse_args():
    parser = argparse.ArgumentParser(description="Isranews Scraper CLI (Async)")
    parser.add_argument('-c', '--categories', type=str, help='Categories (comma separated or "all")')
    parser.add_argument('-s', '--start', type=int, default=1, help='Start page')
    parser.add_argument('-e', '--end', type=int, default=1, help='End page (0 for all)')
    parser.add_argument('-d', '--date', type=str, help='Filter date (YYYY-MM-DD)')
    parser.add_argument('-f', '--format', type=str, choices=EXPORT_FORMATS, default='csv', help='Output format')
    parser.add_argument('-o', '--output', type=str, default='isranews', help='Output filename')
    parser.add_argument('--max-threads', type=int, default=5, help='Max concurrency (default=5)')
    return parser.parse_args()

def resolve_categories(sel: Optional[str]) -> List[str]:
    if not sel:
        return list(CATEGORY_MAP.values())
    
    sel = sel.strip().lower()
    if sel == "all":
        return list(CATEGORY_MAP.values())
    
    cats = []
    items = [s.strip() for s in sel.split(",") if s.strip()]
    for x in items:
        if x in CATEGORY_MAP:
            cats.append(CATEGORY_MAP[x])
        elif x.isdigit() and 1 <= int(x) <= len(CATEGORY_MAP):
            cats.append(list(CATEGORY_MAP.values())[int(x)-1])
        else:
            cats.append(x)
    return cats

async def async_main():
    try:
        args = parse_args()
        cat_paths = resolve_categories(args.categories)
        
        filter_date = None
        if args.date:
            try:
                filter_date = datetime.strptime(args.date, "%Y-%m-%d")
            except ValueError:
                logger.error("Invalid date format. Use YYYY-MM-DD.")
                return

        scraper = IsranewsScraper(max_concurrency=args.max_threads)
        await scraper.run(
            cat_paths=cat_paths,
            start=args.start,
            end=args.end,
            filter_date=filter_date,
            filename=args.output,
            fmt=args.format
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR: {e}")

def main():
    # Force UTF-8 for stdout/stderr to handle Thai characters
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
