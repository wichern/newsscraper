#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import pickle
from selenium import webdriver
import urllib.request
import uuid

class PyScraper(object):
    def __init__(self, argv, parser=argparse.ArgumentParser(prog='pyscraper')):
        parser.add_argument('--out', type=str, default='report.json', help='Output file')
        parser.add_argument('--browser', type=str, default='firefox', help='Selenium Webdriver (default=firefox)')
        parser.add_argument('--headless', action='store_true')
        parser.add_argument('--dry', action='store_true', help='Do not actually download or store results.')
        parser.add_argument('--quiet', '-q', action='store_true')
        parser.add_argument('--pickle', type=str, default='./.pickle/__script__.pickle', help='Pickle file containing all known urls.')
        parser.add_argument('--download_dir', type=str, default='./downloads/__script__/')
        parser.add_argument('--screensize', type=str, default='1024,768', help='Browser screen size')
        parser.add_argument('--asset_dir', type=str, default='./assets/')

        self.args = parser.parse_args(argv[1:])
        self.script = os.path.splitext(os.path.basename(argv[0]))[0]
        self.pickle = self.args.pickle.replace('__script__', self.script)
        self.download_dir = self.args.download_dir.replace('__script__', self.script)

        if self.args.browser == 'firefox':
            options = webdriver.FirefoxOptions()
            options.headless = self.args.headless
            options.add_argument('--width={:s}'.format(self.args.screensize.split(',')[0]))
            options.add_argument('--height={:s}'.format(self.args.screensize.split(',')[1]))
            profile = webdriver.FirefoxProfile()
            for extension in os.listdir(self.args.asset_dir):
                if extension.endswith('.xpi'):
                    self.say('Add firefox extension: {:s}'.format(extension))
                    profile.add_extension(self.args.asset_dir + extension)
            self.driver = webdriver.Firefox(executable_path=self.args.asset_dir + 'geckodriver', options=options, firefox_profile=profile)
        elif self.args.browser == 'chrome':
            options = webdriver.ChromeOptions()
            if self.args.headless:
                options.add_argument('headless')
            for extension in os.listdir(self.args.asset_dir):
                if extension.endswith('.crx'):
                    self.say('Add chrome extension: {:s}'.format(extension))
                    options.add_extension(self.args.asset_dir + extension)
            options.add_argument('window-size={:s}'.format(self.args.screensize))
            self.driver = webdriver.Chrome(self.args.asset_dir + 'chromedriver', chrome_options=options)
        else:
            raise ValueError('Driver "{:s}" not found!'.format(self.args.driver))

        self.known_urls = set()
        if os.path.exists(self.pickle):
            with open(self.pickle, 'rb') as infile:
                data = pickle.load(infile)
                self.known_urls = data['urls']
                self.say('Openend {:s} from {:s}'.format(self.pickle, data['last_date']))

        self.items = dict()
        if os.path.exists(self.args.out) and os.stat(self.args.out).st_size > 0:
            with open(self.args.out, 'r') as infile:
                self.items = json.load(infile)
        self.item_count = len(self.items)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.close()
        if self.args.dry:
            return
        if exc_type:
            return
        with open(self.args.out, 'w') as outfile:
            json.dump(self.items, outfile, indent=4)
            new_item_count = len(self.items) - self.item_count
            self.say('Write {:d} new items to {:s}'.format(new_item_count, self.args.out))
        pickle_path = os.path.dirname(os.path.abspath(self.pickle))
        if not os.path.exists(pickle_path):
            os.makedirs(pickle_path)
        with open(self.pickle, 'wb') as outfile:
            pickle.dump({ 'urls': self.known_urls, 'last_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") }, outfile)

    def __contains__(self, url):
        return url in self.known_urls

    def download(self, url, dest=None, overwrite=False):
        if self.args.dry:
            return
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        if not dest:
            dest = url[url.rfind("/")+1:]
        dest_path = self.download_dir + dest
        if overwrite == False and os.path.exists(dest_path):
            return False
        urllib.request.urlretrieve(url, dest_path)
        return True

    def add(self, url, title='', img='', date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        self.say('+ {:s}'.format(title if title else url))

        self.known_urls.add(url)
        key = str(uuid.uuid4());
        self.items[key] = {
            'url': url,
            'img': img,
            'title': title,
            'date': date,
            'script': self.script
        }

        return self.items[key]

    def say(self, msg):
        if not self.args.quiet:
            print(msg)

# ------------------------------------------------------------------------------

def merge_results(inputs, output):
    items = dict()

    for file in inputs:
        with open(file, 'r', encoding='utf-8') as infile:
            items.update(json.load(infile))

    with open(output, 'w') as out:
        json.dump(items, out, indent=4)
