#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup
import csv
import datetime
import json
import os
import pickle
from selenium import webdriver
import sys
import urllib.request
import uuid

def default_report(items, out, type):
    if type == 'json':
        json.dump(items, out, indent=4)
    elif type == 'csv':
        writer = csv.DictWriter(out, items.keys())
        writer.writeheader()
        writer.writerow(items)
    elif type == 'html':
        template_path = os.path.dirname(os.path.abspath(__file__)) + '/report.html'
        with open(template_path, 'r') as infile:
            template = infile.read()
            out.write(template.replace('__ITEMS__', json.dumps(items)))

class Scraper(object):
    def __init__(self, argv, parser=argparse.ArgumentParser(prog='pyscraper'), report=default_report):
        parser.add_argument('--out', type=argparse.FileType('w'), default=sys.stdout, help='Report output')
        parser.add_argument('--report', type=str, default='json', help='Report type (json|csv|html). Default: json')
        parser.add_argument('--headless', action='store_true')
        parser.add_argument('--verbose', action='store_true', help='Print some logs')
        parser.add_argument('--dry', action='store_true', help='Do not actually download or store results.')
        parser.add_argument('--pickle', type=str, default='./.pickle/__script__.pickle', help='Pickle file containing all known urls.')
        parser.add_argument('--download_dir', type=str, default='./downloads/__script__/')
        parser.add_argument('--asset_dir', type=str, default='./assets/')
        parser.add_argument('--clear', action='store_true', help='Clear all known keys.')

        self.report = report
        self.args = parser.parse_args(argv[1:])

        if self.args.verbose and self.args.out == sys.stdout and not self.args.dry:
            raise ValueError('Should not use --verbose with stdout output.')

        self.script = os.path.splitext(os.path.basename(argv[0]))[0]
        self.pickle = self.args.pickle.replace('__script__', self.script)
        self.download_dir = self.args.download_dir.replace('__script__', self.script)

        self.keys = set()
        if os.path.exists(self.pickle):
            if self.args.clear:
                os.remove(self.pickle)
            else:
                with open(self.pickle, 'rb') as infile:
                    data = pickle.load(infile)
                    self.keys = data['keys']
                    self.say('Opened {:s} from {:s}'.format(self.pickle, data['date']))

        self.items = []
        self.firefox = None
        self.chrome = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.firefox:
            self.firefox.close()
        if self.chrome:
            self.chrome.close()
        if self.args.dry:
            return
        if exc_type:
            return

        # Write report.
        self.say('Report {:d} items.'.format(len(self.items)))
        self.report(self.items, self.args.out, self.args.report)

        # Write pickle.
        pickle_path = os.path.dirname(os.path.abspath(self.pickle))
        if not os.path.exists(pickle_path):
            os.makedirs(pickle_path)
        with open(self.pickle, 'wb') as outfile:
            pickle.dump({ 'keys': self.keys, 'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") }, outfile)

    def __contains__(self, key):
        return key in self.keys

    def download(self, url, dest=None, overwrite=False):
        if self.args.dry:
            return
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        if not dest:
            dest = url[url.rfind("/")+1:]
        dest_path = self.download_dir + dest
        if overwrite == False and os.path.exists(dest_path):
            raise ValueError('{:s} already exists.'.format(dest_path))
        urllib.request.urlretrieve(url, dest_path)

    def get_soup(self, url, parser='html.parser'):
        return BeautifulSoup(urllib.request.urlopen(url).read(), parser)

    def get_firefox(self, width=1024, heigth=768):
        if not self.firefox:
            options = webdriver.FirefoxOptions()
            options.headless = self.args.headless
            options.add_argument('--width={:d}'.format(width))
            options.add_argument('--height={:d}'.format(heigth))
            profile = webdriver.FirefoxProfile()
            for extension in os.listdir(self.args.asset_dir):
                if extension.endswith('.xpi'):
                    self.say('Add firefox extension: {:s}'.format(extension))
                    profile.add_extension(self.args.asset_dir + extension)
            self.firefox = webdriver.Firefox(executable_path=self.args.asset_dir + 'geckodriver', options=options, firefox_profile=profile)
        return self.firefox

    def get_chrome(self, width=1024, heigth=768):
        if not self.chrome:
            options = webdriver.ChromeOptions()
            if self.args.headless:
                options.add_argument('headless')
            for extension in os.listdir(self.args.asset_dir):
                if extension.endswith('.crx'):
                    self.say('Add chrome extension: {:s}'.format(extension))
                    options.add_extension(self.args.asset_dir + extension)
            options.add_argument('window-size={:d},{:d}'.format(width, heigth))
            self.chrome = webdriver.Chrome(self.args.asset_dir + 'chromedriver', chrome_options=options)
        return self.chrome

    def add(self, *, key, title='', url='', thumb='', tags=[], date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data=dict()):
        self.say('+ {:s}'.format(title if title else key))
        self.keys.add(key)
        item = dict()
        if title:
            item['title'] = title
        if url:
            item['url'] = url
        if thumb:
            item['thumb'] = thumb
        if tags:
            item['tags'] = tags
        if date:
            item['date'] = date
        if data:
            item.update(data)
        self.items.append(item)

    def say(self, msg):
        if self.args.verbose:
            print(msg)

# ------------------------------------------------------------------------------

def merge_results(inputs, output):
    items = dict()

    for file in inputs:
        with open(file, 'r', encoding='utf-8') as infile:
            items.update(json.load(infile))

    with open(output, 'w') as out:
        json.dump(items, out, indent=4)
