#from pillow import Image

from django.test import TestCase
from django.conf import settings
from django.db import models
from media_helper.models import TestModel
from media_helper.tools.resizers import resize
from .settings import Settings
#from football.models import Test

class ResizerTest(TestCase):
    scaling_factors = {
            '2': 0.1,
            '10': 0.5,
            '20': 1.0
        }
    sizes = [2, 10, 20]


    def test_find_models_with_field(self):
        from media_helper.tools.finders import find_models_with_field
    
        m = TestModel
        n = find_models_with_field(models.ImageField)

        self.assertTrue(n.count(m) == 1)

    def test_find_field_attribute(self):
        from media_helper.tools.finders import find_field_attribute
        
        self.assertTrue(["image"], find_field_attribute("name", TestModel))

    def test_resize(self):
        import media_helper
        import os
        from PIL import Image
        from media_helper.tools.helpers import construct_paths
        
        settings.MEDIA_URL = '/test-files/'
        
        root = settings.MEDIA_ROOT = os.path.join(os.getcwd(), 'test-files')

        new_image_path = os.path.join(root, 'media-helper/upload/image.png/30.png"',)
        image_path = os.path.join(root, "upload/image.png")
        paths = construct_paths(image_path)

        resize(image_path, 3)
        resized = os.path.join(paths['response_system_path'], '30.png')
        #self.assertEqual(paths['response_system_path'], image_path)
        self.assertTrue(os.path.isfile(new_image_path))

        image = Image.open(new_image_path)
        self.assertEqual((30, 30), image.size)

        os.remove(new_image_path)
        
        image_path = os.path.join(media_root, "upload/image.txt")
        media_helper.resizer.resize(media_root, "path", .75, image_path)
        self.assertFalse(os.path.isfile(os.path.join(media_root, "path/upload/image.txt")))
    
    def test_resize_on_save(self):
        import os
        
        from django.core.files import File
        from django.db.models.signals import post_save
        
        import media_helper 
        from media_helper.resizer import resize_on_save
        from media_helper.models import TestModel
        

        settings.MEDIA_ROOT = os.path.join(media_helper.__path__[0], "test-files/")
        settings.MEDIA_URL = '/test-files/'
        #settings.MEDIA_HELPER_SIZES = [200, 300]
        #settings.MEDIA_HELPER_AUTO = False
        #settings.MEDIA_HELPER_STEP_SIZE = [100]


        image_path = os.path.join(settings.MEDIA_ROOT, "upload/image.png")
        #image = Image.open(os.path.join(settings.MEDIA_ROOT, "path/upload/image.png"))
        image = open(image_path)

        test = TestModel()
        #post_save.connect(resize_on_save, sender = TestModel)
        
        test.image.save(image_path, File(image))
        test.save()
        post_save.send(resize_on_save, instance = test)
        

        self.assertTrue(True)

    def test_create_directories(self):
        import os
        import shutil
        from django.conf import settings
        from media_helper.tools.helpers import create_directories
        new = os.path.join(os.getcwd(), 'pathname')
        create_directories(os.getcwd(), "pathname")

        self.assertTrue(os.path.isdir(new))
        shutil.rmtree(new)

    def test_default_settings(self):
        from settings import Settings
        
        settings = Settings()
        self.assertTrue(settings.auto)
        self.assertEqual(
            settings.sizes, 
            [0.3, 0.3125, 0.4, 0.426953125, 0.45, 0.5, 0.53125, 0.546875, 0.5625, 0.6, 0.625, 0.65625, 0.75, 0.8, 1.0]
        )

        self.assertEqual(settings.minimum, 800)
        self.assertEqual(settings.default, .5)
        self.assertEqual(settings.quality, 50)
        self.assertEqual(settings.allowed_encodings, ['jpg', 'jpeg', 'png'])



class HelpersTest(TestCase):
    def test_construct_paths(self):
        import os.path
        from media_helper.tools.helpers import construct_paths
        settings.MEDIA_URL = '/test-files/'
        settings.MEDIA_ROOT = '/junky-butter/peanuts/'

        paths = construct_paths("doo/1.jpg")

        self.assertEqual(paths['image_name'], 'doo/1.jpg')
        self.assertEqual(paths['request_path'], '/test-files/doo/1.jpg')
        self.assertEqual(paths['request_system_path'], '/junky-butter/peanuts/doo/1.jpg')
        self.assertEqual(paths['response_path'], '/test-files/media-helper/doo/1.jpg')
        self.assertEqual(paths['media_helper_root'], '/junky-butter/peanuts/media-helper')
        self.assertEqual(paths['backup_path'], '/junky-butter/peanuts/media-helper/doo/1.jpg/original.jpeg')
        self.assertEqual(paths['backup_response_path'], '/test-files/media-helper/doo/1.jpg/original.jpeg')
        self.assertEqual(paths['response_system_path'], '/junky-butter/peanuts/media-helper/doo/1.jpg')