# WebDF
An application to crawl a spoofed website and collect forensics information as evidence.

                It uses three scripts to compare images based on its pixels (imagecomparer.py), crawl
                the original and spoofed website and populate a sqlite database (crawler.py) and
                capture screenshots of the spoofed site for evidence Web_Capturer.py
                
Requeriments:
 
- scrapy
- sqlite3
- colorama
- termcolor
- selenium
- twisted
- numpy
- pillow

usage:

    python WebDF.py -s <spoof domain> -u <file with urls to analyze> 

if you want to compare two domains use:

    python WebDF.py -s <spoof domain> -u <file with urls to analyze> --compare
  
once you start the script it will ask for the original domain to compare and a file with the urls to crawl in the original domain.

Results:

Once finished, this script will create the following folders and files:

- Folder: <spoof_date> this folder contains a copy of the html for each page linked in the domain and urls analyzed. This folder also contains images, thumbnails and screeshot for each page.
- Folder: <original_date> this folder contains a copy of the html for each page linked in the domain and urls analyzed. This folder also contains images and thumbnails.
- Database <spoof_date>.db this is a sqlite database that stores all the responses for each request por spoof and original domain, images, case info and results for comparisons.
- Logs <domain_date>.json all the information collected using scrapy for each domain crawled.
- file <spoof domain>.txt, contains information fo images that, once compared, had a treshold lower than 500, it means these images have the same content.
  
  
To export sqlite tables to csv:
  
    sqlite3 -header -csv <database>.db "select * from requests;" > requests.csv
