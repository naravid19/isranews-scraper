แน่นอนครับ! นี่คือไฟล์ **README.md** สำหรับโปรเจกต์ `isranews-scraper` ที่จัดรูปแบบและตกแต่งอย่างสวยงาม พร้อมอธิบายวิธีการใช้งาน และอ้างอิง tag/ฟีเจอร์ตามภาพหน้าหลัก GitHub ที่คุณแนบมา

---

````markdown
# isranews-scraper

> **A robust and parallel web scraper for [isranews.org](https://www.isranews.org) with multi-category support and data export**

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-%5E1.0-green)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-OK-blueviolet)
![Automation](https://img.shields.io/badge/Automation-Ready-brightgreen)

---

## 📰 Overview

`isranews-scraper` เป็น **Web Scraper สำหรับเว็บไซต์ isranews.org** ที่ออกแบบมาเพื่อดึงข่าวแบบอัตโนมัติ รองรับการเลือกหมวดหมู่ หลายหน้า หลายหมวด หรือทั้งเว็บไซต์ สามารถ export ข้อมูลเป็นไฟล์ `CSV`, `Excel`, `JSON`, หรือ `TXT` และรองรับการ scrape ข้อมูลแบบขนาน (parallel) เพื่อความรวดเร็วสูงสุด

**Features:**
- เลือกหมวดข่าวเองหรือ scrape ทั้งเว็บ (multi-category)
- กำหนดช่วงหน้า (start-end) และวันที่
- Export ข้อมูลเป็น csv, xlsx, json, txt
- รองรับ CLI เต็มรูปแบบ พร้อม `--help`
- อัปเดตข่าว/ผสานกับไฟล์เดิมอัตโนมัติ
- รองรับ automation และใช้งานร่วมกับ workflow อื่นได้
- ใช้ `Playwright` และ `BeautifulSoup` ทำให้ scrape ข้อมูลได้แม้เว็บเปลี่ยนแปลง
- Threaded scraping เร็วสุดๆ (ตั้งค่า `--max-threads` ได้)

---

## 🚀 Quick Start

### **ติดตั้ง dependency**

```bash
pip install playwright beautifulsoup4 pandas tqdm
python -m playwright install
````

### **ใช้งานผ่าน CLI**

ตัวอย่างคำสั่งง่ายๆ:

```bash
python isranews_scraper.py -c all -s 1 -e 3 -f excel -o ข่าวอิศรา
```

หรือ

```bash
python isranews_scraper.py -c 2 -s 1 -e 0 -f csv -o isranews-community
```

**หมายเหตุ:**

* ถ้าไม่ใส่ parameter จะเข้าสู่ interactive mode (ถามผ่าน command line)
* `-c` หมวดหมู่ (`all`, เลข, ชื่อ, หรือ path)
* `-s` หน้าเริ่มต้น
* `-e` หน้าสุดท้าย (`0` = scrape จนหมด)
* `-f` รูปแบบ export (`csv`, `excel`, `json`, `txt`)
* `-o` ชื่อไฟล์ผลลัพธ์ (ไม่ต้องใส่นามสกุล)
* `-d` วันที่กรอง (`YYYY-MM-DD` หรือ พ.ศ.)
* `--max-threads` จำนวน thread (default=8)

ดูรายละเอียดเพิ่มเติมด้วย `-h` หรือ `--help`

```bash
python isranews_scraper.py -h
```

---

## 🔖 ตัวอย่างคำสั่ง

* ดึงทุกหมวดทุกหน้าเป็น Excel:

  ```bash
  python isranews_scraper.py -c all -s 1 -e 0 -f excel -o all-news
  ```
* ดึงเฉพาะหมวด "ศูนย์ข่าวสืบสวน" 20 หน้า แปลงเป็น CSV:

  ```bash
  python isranews_scraper.py -c "ศูนย์ข่าวสืบสวน" -s 1 -e 20 -f csv -o investigative-news
  ```
* กรองข่าวหลังวันที่ 2024-01-01:

  ```bash
  python isranews_scraper.py -c 1 -s 1 -e 0 -d 2024-01-01 -o new-news
  ```

---

## 🏷️ Supported Categories

| เลข | ชื่อหมวด               | Path                                        |
| --- | ---------------------- | ------------------------------------------- |
| 1   | ข่าว                   | article/isranews-news.html                  |
| 2   | ศูนย์ข่าวเพื่อชุมชน    | article/community/comm-news.html            |
| 3   | ศูนย์ข่าวภาคใต้        | article/south-news/other-news.html          |
| 4   | ศูนย์ข่าวนโยบายสาธารณะ | article/thaireform/thaireform-news.html     |
| 5   | ศูนย์ข่าวสืบสวน        | article/investigative/investigate-news.html |

---

## ⚡ Features

* **python** • **automation** • **news-scraper**
* **scraping** • **web-scraper** • **beautifulsoup**
* **data-collection** • **playwright** • **thai-news** • **isranews**
* Multi-threaded, resilient, easy to extend

---

## 📂 Output

Output ตัวอย่าง (CSV/Excel/JSON/TXT):

| หัวข้อ | เนื้อหา | วันที่ | URL | หมวดหมู่ข่าว | Tags | ยอดวิว |
| ------ | ------- | ------ | --- | ------------ | ---- | ------ |

> ในไฟล์ TXT จะ export ในรูปแบบอ่านง่าย พร้อมแยกข่าวแต่ละชิ้นด้วย `=`

---

## 🧑‍💻 Developer Notes

* สามารถพัฒนาเพิ่มเติม เช่น

  * Scrape รูปภาพ หรือ multimedia
  * Export รูปแบบอื่น, Push ข้อมูลไป DB, Google Sheets
  * ตัดคำ/วิเคราะห์ NLP ต่อยอดข่าว
  * ทำ Dashboard Visualize หรือเชื่อม API

---

## 🛠️ Credits

* [Playwright](https://playwright.dev/)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [pandas](https://pandas.pydata.org/)
* [tqdm](https://tqdm.github.io/)

---

## License

[MIT](./LICENSE)
