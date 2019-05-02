import unittest

from millicord.recognition.idol_recognition import IdolRecognition

class IdolRecognitionTest(unittest.TestCase):
    def setUp(self):
        self.ir = IdolRecognition()
    
    def test_idol_recognition(self):
        url = 'http://hoge.image.com'
        name = 'mirai'
        is_mirai = self.ir.recognize_idol(url,name)
        self.assertEqual(True, is_mirai)