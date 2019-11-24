============
newsscraper
============

``newsscraper`` provides a framework for scraping web news with
`Selenium <https://www.seleniumhq.org/>`_ and `Beautiful Soup <https://www.crummy.com/software/BeautifulSoup/>`_. ``newsscraper`` will take care of remembering which news items where already read and creates
results in form of ``json``, ``csv``, or ``html`` files.

A minimal scraper for `newsscraper` that fetches the newest questions from
https://stackoverflow.com/questions can look like this:

.. code-block:: python3

 # content of stackoverflow.py
 import newsscraper
 import sys

 with newsscraper.Scraper(sys.argv) as scraper:
    driver = scraper.get_chrome()
    driver.get('https://stackoverflow.com/questions')
    for question in driver.find_elements_by_xpath('//a[@class="question-hyperlink"]'):
        scraper.add(question.get_attribute('href'), question.text)

Additional configuration can be provided with arguments:

.. code-block:: sh

 python3 stackoverflow.py --headless --verbose report=html --out=$(date '+%Y-%m-%d %H:%M:%S').html

Run ``python3 stackoverflow.py -h`` for a list of all arguments.

********
Features
********

- Remember already added news items
- Create reports in `json`, `csv`, `html`, or a custom format
- Merge multiple `json` reports
- Custom command-line arguments

*******
Roadmap
*******

- Proxy support
- Sort items by date in HTML5 report
- Tags in HTML5 report
- Custom report templates
- RSS reports
- python2 support

************
Installation
************

.. code-block:: sh

 pip3 install newsscraper

If you want to use the selenium drivers you have to download the corresponding `third party drivers <https://www.seleniumhq.org/download/#thirdPartyDrivers>`_
in the ``./assets/`` subdirectory to your script. ``newsscraper`` will also
automatically load all add-ons you place in ``./assets/``.

*******
Changes
*******

- 0.1.0 initial version

*******
License
*******

This project is licensed under the MIT License - see the `LICENSE <https://github.com/wichern/newsscraper/blob/master/LICENSE>`_ for details.
