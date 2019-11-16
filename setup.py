import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(name='newsscraper',
      version='0.1.0',
      description='News scraping and reporting.',
      long_description=README,
      url='https://github.com/wichern/newsscraper',
      author='Paul Wichern',
      author_email='paul@menphis.de',
      license='MIT',
      keywords=['python3', 'webscraping', 'selenium', 'beautifulsoup4'],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers'
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.7',
      ],
      packages=['newsscraper'],
      install_requires=[
          'selenium',
          'beautifulsoup4'
      ],
      zip_safe=False)
