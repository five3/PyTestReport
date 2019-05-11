import unittest


class UTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testTrue(self):
        self.assertTrue(True)

    def testFalse(self):
        self.assertFalse(True)

    def testError(self):
        1 / 0
        self.assertFalse(True)

    def testSkip(self):
        self.skipTest("Skip Test")
