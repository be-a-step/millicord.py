import unittest
import asyncio


class AsyncTestMixin(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.loops = []

    def tearDown(self):
        for l in self.loops:
            if not l.is_closed():
                l.close()

    def get_event_loop(self):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None
        if loop is None or loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self.loops.append(loop)
        return loop
