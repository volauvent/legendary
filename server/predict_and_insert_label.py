from os import listdir
import sys
import os
from os.path import isfile, join
sys.path.append(os.path.abspath('./'))
from server.baseClient import dbClient

'''
this is outdated. will remove soon
'''
client = dbClient()
mypath = "frontend/upload"
onlyfiles = [f for f in listdir(mypath) if (
    isfile(join(mypath, f)) and ('.jpg' in f or '.png' in f))]

for f in onlyfiles:
    # print(f)
    print(f+str(client.predict_and_insert(f)))
print("Done")
