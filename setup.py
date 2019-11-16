from setuptools import setup

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(name='newsscraper',
      version='0.1.0',
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
      install_requires=[
          'selenium',
          'beautifulsoup4'
      ])
