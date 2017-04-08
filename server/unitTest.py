import os.path
import shutil
import unittest
from PIL import Image
import sys
#sys.path.append('../')
import dbUtility
from database import databaseAPI


class TestDataBase(unittest.TestCase):
    """
    unit tests
    all the tests should individually create temp folder, temp file and delete them in the end
    """
    def test_insert_delete_image(self):
        dbUtility.utility.checkFolder('testDatabase')
        db = databaseAPI('testDatabase/test.db', 'testDatabase/data')
        try:
            im = Image.new("RGB", (512, 512), "red")
            im.save('testDatabase/test.jpg')
            # print(utility.hashImage(im))

            db.insertImage('testDatabase/test.jpg')
            self.assertTrue(os.path.isfile('testDatabase/data/images/other/0100000000000000.jpg'))
            self.assertEqual(db.query_meta('SELECT * FROM images where id = "0100000000000000"'), [
                ('0100000000000000', 'testDatabase/data/images/other/0100000000000000.jpg', 0, 5, 'other', 'NULL')])
            db.removeImage('0100000000000000')
            self.assertFalse(os.path.isfile('testDatabase/data/images/other/0100000000000000.jpg'))
            self.assertEqual(db.query_meta('SELECT * FROM images where id = "0100000000000000"'), [])
        finally:
            shutil.rmtree('testDatabase')

    def test_sync(self):
        dbUtility.utility.checkFolder('testDatabase/data/images/you')
        db = databaseAPI('testDatabase/test.db', 'testDatabase/data')
        try:
            im = Image.new("RGB", (512, 512), "red")

            im.save('testDatabase/test.jpg')
            db.insertImage('testDatabase/test.jpg')
            im2 = Image.new("RGB", (512, 512))
            data = [(i // 3, 0, i // 3) for i in range(512)]
            im2.putdata(data)
            im2.save('testDatabase/data/images/you/asd.jpg')
            shutil.rmtree('testDatabase/data/images/other')
            db.synchronize()
            self.assertTrue(os.path.isfile('testDatabase/data/images/you/d1d1d1d1d1d1d1d1.jpg'))
            self.assertFalse(os.path.isfile('testDatabase/data/images/you/asd.jpg'))
            self.assertEqual(db.query_meta("SELECT * FROM images"), [
                ('d1d1d1d1d1d1d1d1', 'testDatabase/data/images/you/d1d1d1d1d1d1d1d1.jpg', 0, 5, 'you', 'NULL')])
        finally:

            shutil.rmtree('testDatabase')

    def test_insert_remove_model(self):
        pass

    def test_insert_remove_model_labels(self):
        dbUtility.utility.checkFolder('testDatabase/data/images/you')
        db = databaseAPI('testDatabase/test.db', 'testDatabase/data')
        try:
            db.insertModelLabel('model1', 'image1', 0, 1.0)
            db.insertModelLabel('model2', 'image1', 1, 1.0)
            db.insertModelLabel('model1', 'image2', 2, 1.0)
            db.insertModelLabel('model1', 'image3', 2, 1.0)
            self.assertEqual(len(db.query_meta("SELECT model, image_id, label, confidence FROM modelLabels")), 4)
            db.removeModelLabel(model='model1', image_id='image1')
            self.assertEqual(len(db.query_meta("SELECT model, image_id, label, confidence FROM modelLabels")), 3)
            db.removeModelLabel(model='model1')
            self.assertEqual(len(db.query_meta("SELECT model, image_id, label, confidence FROM modelLabels")), 1)
            db.removeModelLabel(image_id='image1')
            self.assertEqual(len(db.query_meta("SELECT model, image_id, label, confidence FROM modelLabels")), 0)

        finally:
            shutil.rmtree('testDatabase')

    def test_update(self):
        pass

if __name__ == '__main__':
    unittest.main()