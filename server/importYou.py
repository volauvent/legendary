pathToYou = r'/media/hunter/BC4E58CF4E5883D4/download_you/download_you/images'
import database
db=database.databaseAPI('test.db','data')
labels=['None',
        'amusement',
        'awe',
        'contentment',
        'anger',
        'disgust',
        'excitement',
        'fear',
        'sadness']
for i in range(1,9):
	print("uploading %s" %labels[i])
	db.insertMultipleImagesParallel(pathToYou+'/%s'%labels[i],hashThreadNum=4,source='You',label=i,confidence=5)
db.close()
