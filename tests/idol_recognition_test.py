import unittest

from millicord.modules.recognition.idol_recognition import IdolRecognition


class IdolRecognitionTest(unittest.TestCase):
    def setUp(self):
        self.ir = IdolRecognition()

    def test_idol_recognition(self):
        url = "https://millionlive.idolmaster.jp/theaterdays/images/top/a/aa04.png"
        name = 'mirai'
        is_mirai = self.ir.recognize_idol(url, name)
        self.assertEqual(True, is_mirai)


if __name__ == "__main__":
    unittest.main()
