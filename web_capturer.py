from selenium import webdriver
import os, json, sys
import argparse
from pyvirtualdisplay import Display

from colorama import init
from termcolor import colored
import logging

from selenium.webdriver.chrome.options import Options

init()
chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
logging.warning(colored('WebCapturer.py: Web Capture for forensics purposes.', "green"))
parser = argparse.ArgumentParser(description='Web Capture for forensics purposes.')
parser.add_argument('-c','--case', help='case name, usually <domain>_<date> without extension', required=True)
args = parser.parse_args()
argsdict = vars(args)
folder = argsdict['case']

if os.name =='posix':
    display = Display(visible=0, size=(800, 600))
    display.start()
    DRIVER = './chromedriver/chromedriver'
else:
    DRIVER = './chromedriver/chromedriver.exe'

driver = webdriver.Chrome(DRIVER,chrome_options=chrome_options)

if not os.path.exists('./' + folder + '/screens/'):
        os.makedirs('./' + folder + '/screens/')
path = './' + folder + '/screens/'

site_crawl = json.load(open("./" + folder + '.json'))
logging.warning(colored("Taking screenshots as evidence ...","yellow"))
for data in site_crawl:
    logging.warning("\tTaking screenshots for: "+data['url'])
    try:
        driver.get(data['url'])
        screenshot = driver.save_screenshot(path + data['url'].split("/")[-1].split("?")[0] + '.png')
    except:
        logging.warning(colored("\tError taking screenshot","red"))
driver.quit()
if os.name =='posix':
    display.stop()
