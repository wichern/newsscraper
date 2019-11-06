#!/usr/bin/env python3

import pickle
import json
import os
import urllib.request
import datetime
import selenium

class PyScraper(object):
    def __init__(self, script):
        self.known_urls = set()
        self.script = script
        self.pickle_dir = './pickle/'
        self.pickle_path_script = self.pickle_dir + script + '.pickle'
        self.pickle_path_global = self.pickle_dir + 'pyscraper.pickle'
        self.download_dir = './downloads/' + script
        self.report_dir = './reports/'
        self.items = dict()
        self.report_id = 1
        self.driver = None

        if os.path.exists(self.pickle_path_script):
            with open(self.pickle_path_script, 'rb') as infile:
                data = pickle.load(infile)
                self.known_urls = data['urls']
        if os.path.exists(self.pickle_path_global):
            with open(self.pickle_path_global, 'rb') as infile:
                data = pickle.load(infile)
                self.report_id = data['report_id'] + 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.driver:
            self.driver.close()

        if len(self.items) == 0:
            print('No new items found.')
            return

        report_dir = self.report_dir + str(self.report_id) + '/'
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        reportPath = report_dir + self.script + '.json'
        print('Report over {:d} items written to {:s}'.format(len(self.items), reportPath))
        with open(reportPath, 'w') as outfile:
            json.dump(self.items, outfile)

        if not os.path.exists(self.pickle_dir):
            os.makedirs(self.pickle_dir)
        with open(self.pickle_path_script, 'wb') as outfile:
            pickle.dump({ 'urls': self.known_urls }, outfile)
        with open(self.pickle_path_global, 'wb') as outfile:
            pickle.dump({ 'report_id': self.report_id }, outfile)

    def get_webdriver(self, headless=True):
        if self.driver:
            return self.driver
        options = selenium.webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')
        self.driver = selenium.webdriver.Chrome('./assets/chromedriver', chrome_options=options)
        return self.driver

    def download(self, url, dest = None, overwrite=False):
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

    def add_item(self, url, title = '', date = datetime.datetime.now().strftime("%Y-%m-%d")):
        print('New item: {:s}'.format(url))
        self.known_urls.add(url)
        self.items[url] = { 'title': title, 'date': date }
