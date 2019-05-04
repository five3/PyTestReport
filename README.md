# PyTestReport
一个由`HTMLTestRunner`项目为灵感，并基于`HTMLTestRunner`进行二次开发的一个项目。主要在API调用、报告样式、扩展性等方面进行了增强。

点击查看`HTMLTestRunner`的[官网](http://tungwaiyip.info/software/HTMLTestRunner.html)。`HTMLTestRunner`是基于Python单元测试官方实现的`TextTestResult`为参考，实现了对应的`HTMLTestResult`版本。


# 安装与使用
## 安装
### 通过pip安装
```bash
pip install PyTestReport 
```

### 通过安装包
可通过发布的安装包进行安装，具体安装包可在dist目录查找。
```bash
pip install PyTestReport-0.1-py3-none-any.whl
```

### 通过源码
```bash
pip install git+https://github.com/five3/PyTestReport.git
```
或者
```bash
git clone https://github.com/five3/PyTestReport.git
cd PyTestReport
python setup.py build
python setup.py install
```

## 使用
PyTestReport可用通过多种方式运行，分别如下：
### 单元测试 
```python
from pytestreport import TestRunner

TestRunner(fp, title='单元测试标题', description='单元测试描述', verbosity=2).run(suite)
```

### lib库引入项目
```python
from pytestreport import api
```

### 命令行
```bash
PyTestReport.shell data.json
```

### REST API
```bash
PyTestReport.web 80
```

> 更多样例使用方式见下方`样例说明`部分


# 样例说明
## 单元测试样例
```python
import unittest
from PyTestReport import TestRunner

class MyTest(unittest.TestCase):
    def testTrue(self):
        self.assertTrue(True)

suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MyTest))

with open(r'/path/to/report.html', 'wb') as fp:
    runner = TestRunner(fp, title='测试标题', description='测试描述', verbosity=2)
    runner.run(suite)
```

## 命令行样例
```bash

```

## API样例
```python

```

## Web服务样例
```bash

```

# 开发相关
## 如何改变样式
```bash

```

## 如何新增模板
```bash

```

## 合作
对此项目感兴趣的朋友，欢迎为加入我们的行列，贡献你的一份力量。你可以：
- 添加新的测试报告模板
- 添加新的测试报告样式
- 开发并扩展可用功能
- 提出需求和宝贵意见

另外使用过程中如果有任何问题或疑惑，你可以：
- 在[testqa.cn](http://www.testqa.cn)对应的小组进行提问和讨论
- 在github上给本项目提ISSUE
