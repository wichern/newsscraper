# newsscraper

`newsscraper` provides a simple framework for scraping web news with
[Selenium](https://www.seleniumhq.org/) and
[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/). `newsscraper`
will take care of remembering which news items where already read and creates
results in form of `json`, `csv`, or `html` files.

An minimal scraper for `newsscraper` that fetches the newest questions from
https://stackoverflow.com/questions could look like this:

```python
import newsscraper
import selenium.webdriver
import sys

with newsscraper.Scraper(sys.argv) as scraper:
    scraper.driver.get('https://stackoverflow.com/questions')

    for question in scraper.driver.find_elements_by_xpath('//a[@class="question-hyperlink"]'):
        url = question.get_attribute('href')
        if url in scraper: # Avoid adding an news item twice.
            continue
        scraper.add(url, question.text)
```

Additional configuration can be provided with arguments.
```sh
python3 stackoverflow.py --headless --out=$(date '+%Y-%m-%d %H:%M:%S').html
```

Run `python3 stackoverflow.py -h` for a list of all arguments.

## Features

* Remember already added items.
* Create reports in `json`, `csv`, `html`, or a custom format.
* Merge multiple `json` reports.
* Custom command-line arguments.

Read the [documentation](Documentation.md) for more details.

## Installation

```bash
pip3 install newsscraper
```

If you want to use the selenium drivers you have to download the corresponding
[third party drivers](https://www.seleniumhq.org/download/#thirdPartyDrivers)
in the `./assets/` subdirectory to your script. `pyscraper` will also
automatically load all add-ons you place in `./assets/`.

## Changes

* 0.0.1 initial version

## License

This project is licensed under the MIT License - see the LICENSE file for details.
