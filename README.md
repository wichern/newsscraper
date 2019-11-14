# pyscraper

`pyscraper` aims to provide a simple library for scraping the web and providing
the scraped items in a simple HTML5 report. It is build with `python3` and `Selenium`.

## Installation

```bash
pip3 install selenium pyscraper
```

Install a third-party webdriver from https://www.seleniumhq.org/download/#thirdPartyDrivers into your assets directory (default: `./assets/`).

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
```

Get matching chromedriver from https://sites.google.com/a/chromium.org/chromedriver/downloads and put it in `./assets/chromedriver` subdirectory.

```
mkdir assets
cd assets
wget https://chromedriver.storage.googleapis.com/78.0.3904.70/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
rm chromedriver_linux64.zip
```

## Usage

This sample script will parse the head page of stackoverflow.com for questions.
It will save all results as `report.json`.

```python3
#!/usr/bin/env python3

import pyscraper
import selenium.webdriver
import sys

with pyscraper.PyScraper(sys.argv) as scraper:
    scraper.driver.get('https://stackoverflow.com/questions')

    for question in scraper.driver.find_elements_by_xpath('//a[@class="question-hyperlink"]'):
        url = question.get_attribute('href')
        title = question.text

        # Avoid adding an url twice.
        if url in scraper:
            continue

        scraper.add(url, title)
```

Use `create_html_report.py` for creating the HTML5 report.
```bash
./create_html_report.py report.json report.html
```

## Changes

* 0.0.1 initial version

## Resources

* https://selenium-python.readthedocs.io/
* https://www.w3schools.com/xml/xpath_intro.asp
