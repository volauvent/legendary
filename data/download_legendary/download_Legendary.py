import os
import re
import csv
import urllib.request
import time
from multiprocessing import Pool
from functools import reduce

def download_from_csv(file_name):
    file_name = file_name
    print("file "+file_name+" loaded")
    with open(file_name, newline='') as csvfile:
        
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        #print (spamreader.line_num)
        download_count=0
        failed_count=0
        one=True
        for row in spamreader:
                if one:
                    one=False
                    continue
                name = row[0].split('/')[-1]
                location = './images/'+row[1].lower()+'/'+name

                if os.path.exists(location):
                    print(name+" already exist")
                    continue
                try:
                        urllib.request.urlretrieve(row[0], location)
                        #print(name+" downloaded")
                        download_count+=1
                except:
                            print(name+" can not be downloaded")
                            failed_count+=1
        print("file %s, downloaded %d, failed %d"%(file_name,download_count,failed_count))
        return (download_count,failed_count)

if __name__ =="__main__":
    #create folder
    types=['amusement', 'fear', 'anger', 'awe','contentment','disgust','sadness','excitement']
    for folder in types:
        if not os.path.exists('./images/'+folder):
            os.makedirs('./images/'+folder)

    #find all csv and call download method
    download_from_csv("Legendary_Image_Emotion_Validation_Set1.csv")

    #for file in csv_files:
    #    download_from_csv(file)