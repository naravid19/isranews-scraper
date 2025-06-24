<!-- Improved compatibility of back to top link -->

<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Playwright-%5E1.0-green" />
  <img src="https://img.shields.io/badge/BeautifulSoup-OK-blueviolet" />
  <img src="https://img.shields.io/badge/Automation-Ready-brightgreen" />
</p>

<!-- PROJECT LOGO -->

<div align="center">
  <h1><b>isranews-scraper</b></h1>
  <p>
    <b>A robust and parallel web scraper for <a href="https://www.isranews.org" target="_blank">isranews.org</a><br>
    with multi-category support and data export</b>
  </p>
</div>

---

## 📰 About the Project

`isranews-scraper` คือ Web Scraper อัตโนมัติสำหรับเว็บไซต์ [isranews.org](https://www.isranews.org)
รองรับการดึงข่าวพร้อมกันหลายหมวดหมู่ หลายหน้า สามารถ export ข้อมูลข่าวเป็นไฟล์ `CSV`, `Excel`, `JSON`, หรือ `TXT`
ใช้เทคนิค scraping แบบขนาน (parallel) ทำให้เร็วมาก รองรับการใช้งานผ่าน CLI แบบมืออาชีพ

<details>
  <summary><b>Table of Contents</b></summary>
  <ol>
    <li><a href="#features">Features</a></li>
    <li><a href="#built-with">Built With</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

---

## ✨ Features

* ✅ เลือกหมวดข่าวเอง หรือ scrape ทั้งเว็บ (multi-category)
* ✅ ดึงหลายหน้า, หลายหมวด, หรือกำหนด URL ได้
* ✅ รองรับ export หลายฟอร์แมต (`csv`, `excel`, `json`, `txt`)
* ✅ Scrape ข้อมูลข่าวแบบ parallel ด้วย multi-thread (เร็วมาก)
* ✅ อัปเดต/ผสานข้อมูลเดิมโดยอัตโนมัติ
* ✅ กรองข่าวตามวันที่ (`YYYY-MM-DD` หรือ พ.ศ.)
* ✅ ใช้งานผ่าน CLI พร้อม `--help`
* ✅ เหมาะกับ automation, data analysis, data pipeline

---

## 🛠️ Built With

* [Python 3.8+](https://www.python.org/)
* [Playwright](https://playwright.dev/)
* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
* [pandas](https://pandas.pydata.org/)
* [tqdm](https://tqdm.github.io/)

---

## 🚀 Getting Started

### Prerequisites

* Python >= 3.8
* ติดตั้งแพ็กเกจด้านล่าง

### Installation

```bash
pip install playwright beautifulsoup4 pandas tqdm
python -m playwright install
```

---

## 💻 Usage

### Basic CLI Example

```bash
python isranews_scraper.py -c all -s 1 -e 3 -f excel -o ข่าวอิศรา
```

**ตัวเลือกหลัก:**

* `-c`, `--categories`    เลือกหมวดข่าว (`all`, ชื่อหมวด, หมายเลข, หรือ path)
* `-s`, `--start`         หน้าเริ่มต้น (default: 1)
* `-e`, `--end`           หน้าสุดท้าย (`0` = ดึงจนจบ, default: 1)
* `-f`, `--format`        รูปแบบไฟล์ export (`csv`, `excel`, `json`, `txt`)
* `-o`, `--output`        ชื่อไฟล์ผลลัพธ์ (ไม่ต้องใส่นามสกุล)
* `-d`, `--date`          กรองข่าวที่ใหม่กว่ากำหนด (`YYYY-MM-DD` หรือ พ.ศ.)
* `--max-threads`         จำนวน threads (default: 8)
* `-h`, `--help`          แสดงวิธีใช้งาน

### ตัวอย่างคำสั่ง

* ดึงข่าวทุกหมวด 3 หน้า เป็นไฟล์ Excel:

  ```bash
  python isranews_scraper.py -c all -s 1 -e 3 -f excel -o ข่าวอิศรา
  ```

* ดึงเฉพาะ "ศูนย์ข่าวสืบสวน" ทุกหน้า เป็น JSON:

  ```bash
  python isranews_scraper.py -c "ศูนย์ข่าวสืบสวน" -s 1 -e 0 -f json -o investigative-news
  ```

* ดึงข่าวหน้า 1-5, กรองวันที่หลัง 2024-01-01:

  ```bash
  python isranews_scraper.py -c 1 -s 1 -e 5 -f csv -o isranews-news -d 2024-01-01
  ```

---

## 🔖 Roadmap

* [x] Parallel scraping (multi-thread)
* [x] Export หลาย format
* [x] Merge ข่าวกับไฟล์เก่า
* [ ] เพิ่ม feature ดึงภาพ/เอกสารประกอบข่าว
* [ ] ตั้งเวลาทำงานอัตโนมัติ (cron, schedule)
* [ ] Web UI / API

---

## 📄 License

Distributed under the MIT License.
See `LICENSE` for more information.

---

## 🙏 Acknowledgments

* [isranews.org](https://www.isranews.org)
* [Playwright](https://playwright.dev/)
* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
* [shields.io](https://shields.io)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

**หมายเหตุ:**

* โค้ดและ README นี้เน้นเพื่อการศึกษา/รีเสิร์ช
* ข้อความและตัวอย่างหมวดหมู่ใน isranews อาจเปลี่ยนแปลงได้
