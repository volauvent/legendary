pathToYou = 'images'
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
	db.insertMultipleImagesParallel('images/%s'%labels[i],hashThreadNum=4,source='You',label=i,confidence=5)
db.close()