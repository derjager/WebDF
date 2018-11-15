import numpy as np
import os
from PIL import Image
import pandas as pd
import argparse
import thread, time
from colorama import init
from termcolor import colored
import logging

values=[]
compared=[]

def compare(file1, path2):
  im = [None, None]
  im[0] = (np.array(Image.open(file1))).astype(np.int)
  for file2 in os.listdir(path2):
    compared.append(file1 + ' - ' + file2)
    try:
      im[1] = (np.array(Image.open(path2+'/'+file2))).astype(np.int)   
      c=np.abs(im[0] - im[1]).sum()
      if c <= 500:
        values.append((file1.split("/")[-1],file2,c))
        logging.warning(colored("\tPositive (<treshold): "+ file1 + " " + file2 + "Treshold: "+str(c), "yellow", "on_blue"))
    except:
      logging.warning(colored("\tComparisson error: "+file1+ " vs "+ file2, "yellow", "on_blue"))

def thumbnails(path):
  for file1 in os.listdir(path):
    try:
      img=Image.open(path + "/" + file1).convert('L').resize((32,32), resample=Image.BICUBIC)
      img.save(path + "../thumbX/" + file1)
    except:
      pass
  

if __name__=='__main__':
  import sys
  init()
  logging.warning(colored('image comparer. Identify equal or similar images in two folders', "green"))
  parser = argparse.ArgumentParser(description='image comparer. Identify equal or similar images in two folders.')
  parser.add_argument('-p1','--path1', help='path for the first folder containing only images', required=True)
  parser.add_argument('-p2','--path2', help='path for the second folder containing only images', required=True)
  parser.add_argument('-c','--case', help='casename, for results filename', required=True)
  args = parser.parse_args()
  argsdict = vars(args)
  path1 = argsdict['path1']
  path2 = argsdict['path2']
  logging.warning(colored("Comparing images using resize(32x32), Gray Scale and verifying pizel by pixel. (Treshold < 500)","yellow"))
  logging.warning(colored("\tpaths: "+ path1 + " " + path2, "yellow"))
  values.append((path1,path2,"compare"))
  logging.warning("\tCreating thumbnails for images on paths ")

  for path in values[0][:2]:
    if not os.path.exists(path + "../thumbX/"):
      os.makedirs(path + "../thumbX/")
    logging.warning(colored("\t - Working on path "+path, "yellow"))
    thumbnails(path)

  logging.warning("\tComparing thumbails ...")
  num_files=len(os.listdir(path1 + "../thumbX/"))*len(os.listdir(path2 + "../thumbX/"))
  logging.warning(colored("\n - Total images to compare: "+ str(num_files) + "\n", "yellow"))
  for file1 in os.listdir(path1 + "../thumbX/"):
     thread.start_new_thread(compare, (path1+"../thumbX/"+file1, path2+"../thumbX/"))
  p=0     
  while len(compared) != num_files:
    p=p+1
    if p%2==0:
      logging.warning("\tCompared files: "+str(len(compared)))
    time.sleep(5)

  with open(argsdict['case']+'.txt', 'w') as f:
      for img in values:
        f.write("%s\n" %str(img) )

  logging.warning(colored("Comparison finished.","green"))
