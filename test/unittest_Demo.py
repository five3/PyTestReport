import unittest
import pytestreport


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


class UTestPass(unittest.TestCase):
    def testTrue(self):
        self.assertTrue(True)


class UTestFail(unittest.TestCase):
    def testFalse(self):
        self.assertFalse(True)


class UTestError(unittest.TestCase):
    def testError(self):
        1 / 0
        self.assertFalse(True)


class UTestSkip(unittest.TestCase):
    def testSkip(self):
        self.skipTest("Skip Test")


if __name__ == '__main__':
    pytestreport.main(verbosity=2)
