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
pip install PyTestReport-0.1.X-py3-none-any.whl
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

# 使用
PyTestReport可用通过多种方式运行，分别如下：
- 单元测试 
- lib库引入
- 命令行
- REST API

## 样例说明
### 单元测试样例
```python
import unittest
import pytestreport

class MyTest(unittest.TestCase):
    def testTrue(self):
        self.assertTrue(True)
        
if __name__ == '__main__':
    pytestreport.main(verbosity=2)
```
以这种方式执行之后，默认会在当前文件夹下生成一个`PyTestReport.html`日志文件，且这个文件名和样式模板都不可以重新指定的。

> 注意：这种方式执行时，如果使用Pycharm等IDE，确保不是以IDE的内建单元测试框架来执行的；或者直接通过命令行来执行。

```python
import unittest
from pytestreport import TestRunner

class MyTest(unittest.TestCase):
    def testTrue(self):
        self.assertTrue(True)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MyTest))
    
    with open(r'/path/to/report.html', 'wb') as fp:
        runner = TestRunner(fp, title='测试标题', description='测试描述', verbosity=2)
        runner.run(suite)
```
这种方式适合批量加载和执行测试用例，从测试文件的外部来导入测试用例并执行。这里可以指定具体的结果文件路径和测试标识等信息。

> 这里使用的是默认模板主题，如果想要使用其它模板主题，可以通过制定模板的主题文件了实现。比如：使用遗留模板的方式如下所示。
```python
from pytestreport import TestRunner
...
runner = TestRunner(fp, title='测试标题', description='测试描述', verbosity=2, 
                    htmltemplate='legency.html', stylesheet='legency.css', javascript='legency.js')
```

### Lib库引入样例
```bash
暂未支持
```

### 命令行样例
```python
暂未支持
```

### REST API样例
```bash
暂未支持
```

# 开发相关
`PyTestReport`对原项目进行了改进，使用了Jinjia2作为模板引擎。且CSS、JS、HTML文件都进行了分离，所以可以通过改变单独或者全部文件来达到修改模板的目的。当然这里的修改通常指的新增一个文件，而在执行时只要指定使用新文件即可。

该项目目前默认保留了2个主题的模板：一个是`HTMLTestRunner`原来的模板样式(legency)，一个是依据原模板进行UI优化的模板样式(default)。

> 另外，后期会收集和添加其它更丰富的模板，也欢迎大家来踊跃的为该项目来添加新模板和样式。

## 如何更新样式
样式文件被存放在`static/css/`目录下，默认保留了2个样式：default.css, legency.css。想要修改样式的方式2两种：
- 直接修改当前主题对应的css文件
- 复制当前主题的css文件，在进行修改（推荐）

第一种方式修改之后重新执行单元测试会直接生效。第二种方式则需要修改下实例化`PyTestReport.TestRunner`的style参数。比如：
```python
from pytestreport import TestRunner
...
runner = TestRunner(fp, title='测试标题', description='测试描述', verbosity=2, stylesheet='new_style.css')
```

## 如何更新JS
JS文件被存放在`static/js/`目录下，默认保留了2个JS：default.js, legency.js。修改JS的方式和修改样式一样有2种，同样我们推荐复制并修改新JS文件的方式。指定新JS文件的使用方式如下：
```python
from pytestreport import TestRunner
...
runner = TestRunner(fp, title='测试标题', description='测试描述', verbosity=2, javaScript='new_js.js')
```



## 如何更新模板
HTML的模板被存放在`templates`目录下，默认保留了2个模板：default.html, legency.html。

> 如果你选择修改模板，那么一般情况下你可能同时也需要修改CSS或JS文件。所以我们更推荐的方式是直接新增一个主题（包括html、css、js），并且在主题功能完善之后发送一个pull request，贡献到本项目中提供给更多的人使用！

```python
from pytestreport import TestRunner
...
runner = TestRunner(fp, title='测试标题', description='测试描述', verbosity=2,
                    htmltemplate='new_theme.html', stylesheet='new_theme.css', javascript='new_theme.js')
```

> 这里需要注意的是，如果新模板需要引用第三方库（js、css），请优先使用CDN链接而非本地静态文件。

# 模板展示
## 默认主题
![默认主题]()

# 合作
对此项目感兴趣的朋友，欢迎为加入我们的行列，贡献你的一份力量。你可以：
- 添加新的测试报告模板
- 添加新的测试报告样式
- 开发并扩展可用功能
- 提出需求和宝贵意见

另外使用过程中如果有任何问题或疑惑，你可以：
- 在[testqa.cn](http://www.testqa.cn/team/detail/PyTestReport)`PyTestReport`的小组进行提问和讨论
- 在github上给本项目提ISSUE
