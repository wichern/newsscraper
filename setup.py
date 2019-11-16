from setuptools import setup

setup(name='newsscraper',
      version='0.0.1',
      description='News scraping and reporting.',
      url='https://github.com/wichern/newsscraper',
      author='Paul Wichern',
      author_email='paul@menphis.de',
      license='MIT',
      packages=['newsscraper'],
      install_requires=[
          'selenium',
          'beautifulsoup4'
      ],
      zip_safe=False)
