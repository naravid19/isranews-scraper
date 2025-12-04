<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Isranews Scraper</h3>

  <p align="center">
    A robust, asynchronous web scraper for Isranews.org with a modern GUI and CLI support.
    <br />
    <a href="https://github.com/your_username/repo_name"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/your_username/repo_name">View Demo</a>
    &middot;
    <a href="https://github.com/your_username/repo_name/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/your_username/repo_name/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

`isranews-scraper` is a high-performance web scraping tool designed specifically for [isranews.org](https://www.isranews.org). It allows users to extract news articles from various categories efficiently using asynchronous operations.

Key features include:

- **Asynchronous Scraping**: Built with `asyncio` and `playwright` for maximum speed and concurrency.
- **Dual Interface**: Offers both a Command Line Interface (CLI) for automation and a Graphical User Interface (GUI) for ease of use.
- **Multi-Format Export**: Save data in CSV, Excel, JSON, or TXT formats.
- **Smart Filtering**: Filter news by date and automatically merge new data with existing files.
- **Robust Error Handling**: Handles network issues and encoding errors gracefully.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

This project is built using robust Python libraries to ensure reliability and performance.

- [![Python][Python.org]][Python-url]
- [![Playwright][Playwright.dev]][Playwright-url]
- [![Pandas][Pandas.pydata.org]][Pandas-url]
- [![BeautifulSoup][BeautifulSoup.com]][BeautifulSoup-url]
- [![PyQt6][PyQt6.org]][PyQt6-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1.  Clone the repo
    ```sh
    git clone https://github.com/your_username/isranews-scraper.git
    ```
2.  Install Python packages
    ```sh
    pip install -r requirements.txt
    ```
3.  Install Playwright browsers
    ```sh
    python -m playwright install
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

### Graphical User Interface (GUI)

For a user-friendly experience, run the GUI application:

```bash
python isranews_scraper_gui.py
```

1.  **Select Categories**: Choose one or more news categories from the list.
2.  **Set Range**: Define the start and end pages to scrape.
3.  **Filter**: Optionally set a date to filter news items.
4.  **Export**: Choose your desired output format and filename.
5.  **Start**: Click the "Start Scraping" button.

### Command Line Interface (CLI)

For automation or server environments, use the CLI:

```bash
python isranews_scraper.py -c "ศูนย์ข่าวสืบสวน" -s 1 -e 5 -o investigative_news
```

**Arguments:**

- `-c`, `--categories`: Category name or index (comma-separated). Use "all" for everything.
- `-s`, `--start`: Start page number (default: 1).
- `-e`, `--end`: End page number (0 for all).
- `-o`, `--output`: Output filename (without extension).
- `-f`, `--format`: Output format (`csv`, `excel`, `json`, `txt`).
- `-d`, `--date`: Filter date (`YYYY-MM-DD`).
- `--max-threads`: Maximum concurrent pages (default: 5).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [x] Migrated to Asynchronous Architecture (`asyncio` + `playwright`)
- [x] Modern Dark-Themed GUI (`PyQt6`)
- [x] Multi-format Export Support
- [x] Automatic Data Merging
- [ ] Add support for downloading article images/attachments
- [ ] Implement scheduled scraping (Cron/Task Scheduler integration)
- [ ] REST API for remote triggering

See the [open issues](https://github.com/your_username/repo_name/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

- [Isranews.org](https://www.isranews.org)
- [Playwright](https://playwright.dev/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Pandas](https://pandas.pydata.org/)
- [PyQt6](https://pypi.org/project/PyQt6/)
- [Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Python.org]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Playwright.dev]: https://img.shields.io/badge/Playwright-45ba4b?style=for-the-badge&logo=Playwright&logoColor=white
[Playwright-url]: https://playwright.dev/
[Pandas.pydata.org]: https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white
[Pandas-url]: https://pandas.pydata.org/
[BeautifulSoup.com]: https://img.shields.io/badge/BeautifulSoup-OK-blueviolet?style=for-the-badge
[BeautifulSoup-url]: https://www.crummy.com/software/BeautifulSoup/
[PyQt6.org]: https://img.shields.io/badge/PyQt6-41CD52?style=for-the-badge&logo=Qt&logoColor=white
[PyQt6-url]: https://pypi.org/project/PyQt6/
