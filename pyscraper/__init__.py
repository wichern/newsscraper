#!/usr/bin/env python3

import pickle
import json
import os
import urllib.request
import datetime
import selenium
import ntpath
import uuid

class PyScraper(object):
    def __init__(self, argv):
        self.script = ntpath.basename(argv[0])
        if self.script.endswith('.py'):
            self.script = self.script[:-3]
        self.pickle_dir = './.pickle/'
        self.pickle_path = self.pickle_dir + self.script + '.pickle'
        self.download_dir = './downloads/' + self.script
        self.report_file = 'report.json'
        self.driver = None
        self.headless = 'headless' in argv
        self.loglevel = 3 if 'verbose' in argv else 2
        self.dryrun = 'dry' in argv

        self.known_urls = set()
        if os.path.exists(self.pickle_path):
            with open(self.pickle_path, 'rb') as infile:
                data = pickle.load(infile)
                self.known_urls = data['urls']
                print('Openend {:s} from {:s}'.format(self.pickle_path, data['last_date']))

        self.items = dict()
        if os.path.exists(self.report_file) and os.stat(self.report_file).st_size > 0:
            with open(self.report_file, 'r') as infile:
                self.items = json.load(infile)
        self.item_count = len(self.items)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.close()
        if self.dryrun:
            return
        with open(self.report_file, 'w') as outfile:
            json.dump(self.items, outfile, indent=4)
            new_item_count = len(self.items) - self.item_count
            self.logI('Write {:d} new items to {:s}'.format(new_item_count, self.report_file))
        if not os.path.exists(self.pickle_dir):
            os.makedirs(self.pickle_dir)
        with open(self.pickle_path, 'wb') as outfile:
            pickle.dump({ 'urls': self.known_urls, 'last_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") }, outfile)

    def get_webdriver(self, size=[1024,768]):
        if self.driver:
            return self.driver
        options = selenium.webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('headless')
        options.add_argument('window-size={:d},{:d}'.format(size[0], size[1]))
        self.driver = selenium.webdriver.Chrome('./assets/chromedriver', chrome_options=options)
        return self.driver

    def download(self, url, dest=None, overwrite=False):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        if not dest:
            dest = url[url.rfind("/")+1:]
        dest_path = self.download_dir + '/' + dest
        if overwrite == False and os.path.exists(dest_path):
            return False
        urllib.request.urlretrieve(url, dest_path)
        return True

    def has_url(self, url):
        return url in self.known_urls

    def add_item(self, url, title='', img='', date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), hot=False):
        if title:
            self.logI('New item: {:s}'.format(title))
        else:
            self.logI('New item: {:s}'.format(url))

        self.known_urls.add(url)

        key = str(uuid.uuid4());
        self.items[key] = {
            'url': url,
            'img': img,
            'title': title,
            'date': date,
            'script': self.script
        }

        if hot:
            self.items[key]['hot'] = True

    def logI(self, msg):
        if self.loglevel >= 3:
            print(msg)

    def logW(self, msg):
        if self.loglevel >= 2:
            print(msg)

    def logE(self, msg):
        if self.loglevel >= 1:
            print(msg)

# ------------------------------------------------------------------------------

def html_report(report_path, out_path):
    if not os.path.exists(report_path):
        print('{:s} not found!'.format(report_path))
        return

    template_path = os.path.dirname(os.path.realpath(__file__)) + '/report.html'
    if not os.path.exists(template_path):
        print('Template {:s} not found!'.format(template_path))
        return

    with open(report_path, 'r') as infile:
        items = json.load(infile)

        if len(items) == 0:
            print('No items in {:s}.'.format(report_path))
            return

        with open(template_path, 'r') as template:
            with open(out_path, 'w') as outfile:
                outfile.write(template.read().replace('__ITEMS__', json.dumps(items)))
