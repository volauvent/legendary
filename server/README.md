to start a Database Server, run "python dbServer.py"

change configurations in "config.ini"

to create a client, see example below:

from baseClient import dbClient
client = dbClient()

client.predict('test.jpeg')

client.query("SELECT * FROM images")

client.getRandomImageWithWeakLabel()

client.insertModelLabel(image_id,label=0,confidence=100,model='manual')

client.insertImage(path,source='other',label=0,confidence=5,comment="NULL")


Labels are represented by numbers:
                (0,'None');
                (1,'amusement');
                (2,'awe');
                (3,'contentment');
                (4,'anger');
                (5,'disgust');
                (6,'excitement');
                (7,'fear');
                (8,'sadness');