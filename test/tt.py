import pytest


class TestSample(object):
    def test_A(self):
        a = 1
        b = 2
        c = a + b
        assert c == 4

    def test_B(self):
        a = 1
        b = 2
        c = a + b
        assert c == 5

    def test_C(self):
        a = 1
        b = 2
        c = a + b
        assert c == 3


if __name__ == '__main__':
    pytest.main(["-s", "tt.py", "--pytest_report", "Pytest_Report.html"])
