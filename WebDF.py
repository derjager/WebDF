
"""WebDF.py: An application to crawl a spoofed website and collect forensics information as evidence.
                It uses three scripts to compare images based on its pixels (imagecomparer.py), crawl
                the original and spoofed website and populate a sqlite database (crawler.py) and
                capture screenshots of the spoofed site for evidence Web_Capturer.py
"""

__author__ = "Eduardo Chavarro Ovalle"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Eduardo Chavarro @ CSIETE"
__email__ = "eduardo.chavarro@csiete.org"
__status__ = "Development"

import time
import scrapy
import sys, os, json
import argparse
from subprocess import call
import sqlite3
import hashlib, urllib, json, ssl
import thread
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers

from colorama import init
from termcolor import colored


datecrwl = (time.strftime("%d%m%Y"))

sqlcs = ''' INSERT INTO wfcase(analyst, casename, casenum, casedate, spfdomain)
          VALUES(?,?,?,?,?) '''
sqlimg= ''' INSERT INTO images(url,imghash,imgpath)
          VALUES(?,?,?) '''
sqlwp = ''' INSERT INTO requests(url,referer,response_headers,images_data,wphash,wppath,screen)
          VALUES(?,?,?,?,?,?,?) '''
sqlimo= ''' INSERT INTO imageso(url,imghash,imgpath)
          VALUES(?,?,?) '''
sqlwpo= ''' INSERT INTO requestso(url,referer,response_headers,images_data,wphash,wppath,screen)
          VALUES(?,?,?,?,?,?,?) '''

websites = {}

def clear(): 
    _ = call('clear' if os.name =='posix' else 'cls') 

def imgget(url,context):
    try:
        websites[url] = urllib.urlopen(url, context=context).read()
    except:
        logging.info(colored("Erro downloading "+ url,"red"))
        websites[url] = "error"

def sha256sum(filename):
    h = hashlib.sha256()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()

def querydb(conn,sql):
    casedb = conn.cursor()
    return casedb.execute(sql)


def create_case_db(database):
    conn=sqlite3.connect(database)
    casedb = conn.cursor()
    casedb.execute("CREATE TABLE requests (url VARCHAR(500), referer VARCHAR(500), response_headers clob, images_data clob, wphash varchar(500), wppath varchar(500), screen varchar(500))")
    casedb.execute("CREATE TABLE images (url VARCHAR(500), imghash varchar(500), imgpath varchar(500))")
    casedb.execute("CREATE TABLE results (url_original VARCHAR(500), url_spoofed varchar(500), details varchar(100))")
    casedb.execute("CREATE TABLE wfcase (analyst VARCHAR(255), casename varchar(100), casenum varchar(100),casedate VARCHAR(100),spfdomain VARCHAR(255), crawled_urls clob)")
    casedb.execute("CREATE TABLE requestso (url VARCHAR(500), referer VARCHAR(500), response_headers clob, images_data clob, wphash varchar(500), wppath varchar(500), screen varchar(500))")
    casedb.execute("CREATE TABLE imageso (url VARCHAR(500), imghash varchar(500), imgpath varchar(500))")
    
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def insert(conn, sql, values):
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()

def populate_requests(domain,folder, conn, sql):
    print "\tPopulating database with information about request for domain ",domain
    site_crawl = json.load(open(folder+'.json'))
    columnswp = ['url', 'referer', 'response_headers', 'images_data']

    for data in site_crawl:
        values=[]
        for c in columnswp:
            values.append(str(data[c]));
        filename = './' + folder + '/' + data['url'].split("/")[-1].split("?")[0]
        screen= './' + folder + '/screen/' + data['url'].split("/")[-1].split("?")[0] +'.png'
        if os.path.exists(filename):
            values.append(sha256sum(filename))
            values.append((filename))
            values.append(screen)
        insert(conn, sql, tuple(values))

def populate_images(folder, conn, sql):
    logging.info("\tPopulating images database ...")

    site_crawl = json.load(open(folder+'.json'))
    logging.info("\tidentifying unique images from URLs responses ...")
    images=[]
    for data in site_crawl:
        for img in data['images_data']:
            if not (img in images):
                images.append(img)

    logging.info("\tDownloading images and populating images table ...")
    context = ssl._create_unverified_context()
    for img in images: thread.start_new_thread(imgget, (img, context,))
    print (colored("\n - Total images to download: "+ str(len(images))+ "\n","yellow"))
    t=0
    while len(websites.keys()) != len(images):
        logging.info(colored("\tDownloaded "+str(len(websites.keys()))+ " images of "+ str(len(images)),"yellow"))
        time.sleep(5)
        t=t+1
        if t > 24: break

    for img in images:
        values=[]
        filename='./' + folder + '/images/' + img.split("/")[-1].split("?")[0]
        try:
            if websites[img]!='error':
                with open(filename,'wb') as f:
                    f.write(websites[img])
                values.append(img)
                values.append(sha256sum(filename))
                values.append(filename)
                insert(conn, sql, tuple(values))
        except:
            logging.info(colored('\tImage '+ img + ' couldn\'t be saved',"red"))

init()

log = logging.getLogger('')
log.setLevel(logging.DEBUG)
format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(format)
log.addHandler(ch)

fh = RotatingFileHandler('./WebDF_'+datecrwl+'.log', maxBytes=(1048576*5), backupCount=7)
fh.setFormatter(format)
log.addHandler(fh)

log.addHandler(fh)
logging.info(colored(' === Web crawler for DFIR. ===', 'green'))
parser = argparse.ArgumentParser(description='Web crawler for DFIR.')
parser.add_argument('-s','--spoofed', help='Spoofed domain to be analyzed', required=True)
parser.add_argument('--compare', help='compare to real domain', action='store_true')
parser.add_argument('-u','--urlsfile', help='File with URLs to analyze', required=True, default='')
args = parser.parse_args()
if (args.compare):
    domain = raw_input(' + Original domain to compare content to: ')
    urlsdomain = raw_input(' + file to original domain urls to crawl: ')
    
argsdict = vars(args)
spoofdomain = argsdict['spoofed']

logging.info(colored("Case information\n", 'yellow'))
caseInfo = {
    'analyst': raw_input(' + Analysts\'s Name: '),
    'case name': raw_input(' + Case name: '),
    'case number': raw_input(' + Case number: '),
    'Date': (time.strftime("%c")),
    'Domain':spoofdomain
    }

logging.info(colored("\nCase information:", 'yellow', "on_blue"))
logging.info(colored(" Analyst: \t" + caseInfo['analyst'], 'yellow'))
logging.info(colored(" CaseName:\t" + caseInfo['case name'], 'yellow'))
logging.info(colored(" Case #: \t" + caseInfo['case number'], 'yellow'))
print "\n"
logging.info(colored(" - Spoofed domain to crawl and collect:"+ spoofdomain, 'yellow', 'on_red'))
#print (colored(" - Urls to crawl on spoofed domain:"
#for u in urls:
#    print "     ",u
if args.compare:
    logging.info(colored(" - Original domain to compare collected elements:"+ domain, 'yellow', 'on_blue'))

raw_input('\n|- If the information is correct, press enter to start crawling.')

datecrwl = (time.strftime("%d%m%Y"))
folder=spoofdomain+'_'+datecrwl
os.system("python crawler.py -s " + spoofdomain + " -u " + argsdict['urlsfile'])
if args.compare:
    os.system("python crawler.py -s " + domain + " -u " + urlsdomain)
raw_input()
clear()
database=folder+'.db'
logging.info(colored("\tCreating case database: "+ database, 'yellow'))
create_case_db(database)
conn = create_connection(database)
insert(conn, sqlcs, (caseInfo['analyst'], caseInfo['case name'], caseInfo['case number'], caseInfo['Date'], spoofdomain))
populate_requests(spoofdomain,folder, conn, sqlwp)

clear()
logging.info(colored("\nStarting screenshot capture ... ", 'yellow'))
os.system("python web_capturer.py -c " + folder)

if args.compare:
    populate_requests(domain,domain+'_'+datecrwl, conn, sqlwpo)
populate_images(folder, conn, sqlimg)
if args.compare:
    websites = {}
    populate_images(domain+'_'+datecrwl, conn, sqlimo)
    clear()
    logging.info(colored("- Exact images used on spoofed site:/n", 'yellow'))
    columns=('Image spoofed','Image original','HASH')
    logging.info(colored(columns, 'red','on_yellow'))
    rows=querydb(conn, 'select images.url, imageso.url, images.imghash from images inner join imageso on images.imghash = imageso.imghash')
    for row in rows:
        logging.info(colored(row, 'red','on_yellow'))
        insert(conn, 'INSERT INTO results(url_original, url_spoofed, details) VALUES(?,?,?) ', (row[0],row[1],"HASH: "+row[2]))

    clear()
    logging.info(colored("\n- Exact pages used on spoofed site:/n", 'yellow'))
    columns=('URL original','URL spoofed','HASH')
    logging.info(colored(columns, 'red','on_yellow'))
    rows=querydb(conn, 'select requests.url, requestso.url from requests inner join requestso on requests.wphash = requestso.wphash')
    for row in rows:
        logging.info(colored(row, 'red','on_yellow'))
        insert(conn, 'INSERT INTO results(url_original, url_spoofed, details) VALUES(?,?,?) ', (row[0],row[1],"HASH: "+row[2]))

    clear()
    logging.info(colored("\nVerifying similar images using ImageCompare and populating table results ... \n", 'yellow'))
    
    os.system("python ImageCompare.py -p1 " + domain+'_'+datecrwl + "/images/ -p2 " + spoofdomain+'_'+datecrwl + '/images/ -c ' + spoofdomain)
    with open(spoofdomain+'.txt', 'r') as f:
        lines=f.readlines()

    for line in lines[1::]:
        values=[]
        for r in (("[", ""),("]", ""),("(", ""),(")", ""),("'", "")):
            line = line.replace(*r)
        clear()
        rows=querydb(conn,'select url from imageso where imgpath like \'%' + line.split(', ')[0] + '%\'')
        img=line.split(', ')[0]
        for row in rows:
            img=row[0]
        values.append(img)
        rows=querydb(conn,'select url from images where imgpath like \'%' + line.split(', ')[1] + '%\'')
        img=line.split(', ')[1]
        for row in rows:
            img=row[0]
        values.append(img)
        values.append('Treshold: ' + line.split(', ')[2])
        insert(conn, 'INSERT INTO results(url_original, url_spoofed, details) VALUES(?,?,?) ', tuple(values))
        logging.info(colored(line.split(', ')[0]+','+ line.split(', ')[1]+','+ 'Treshold: '+ line.split(', ')[2]+','+ values[0]+','+ values[1], 'red','on_yellow'))     

conn.close()
logging.info(colored("Database population finished and saved at "+database,"green"))
