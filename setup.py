from setuptools import setup
import newsscraper

with open('README.rst', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as fh:
    requirements = fh.read().splitlines()

setup(name='newsscraper',
      version=newsscraper.__version__,
      description='News scraping and reporting.',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='https://github.com/wichern/newsscraper',
      author='Paul Wichern',
      author_email='paul@menphis.de',
      license='MIT',
      keywords=['python3', 'webscraping', 'selenium', 'beautifulsoup4'],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent',
      ],
      python_requires='>=3.6',
      packages=['newsscraper'],
      install_requires=requirements)
