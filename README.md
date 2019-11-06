# pyscraper
My wrapper for selenium.

## Installation

```bash
sudo apt-get install python3 python3-pip
pip3 install selenium
```

Install the Chrome browser.

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
```

Get matching chromedriver from https://sites.google.com/a/chromium.org/chromedriver/downloads and put it in `./assets/chromedriver` subdirectory.

```
mkdir assets
cd assets
wget https://chromedriver.storage.googleapis.com/78.0.3904.70/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
rm chromedriver_linux64.zip
```
