# PyTestReport
一个由`HTMLTestRunner`项目为灵感，并基于`HTMLTestRunner`进行二次开发的一个项目。主要在API调用、报告样式、扩展性等方面进行了增强。

点击查看`HTMLTestRunner`的[官网](http://tungwaiyip.info/software/HTMLTestRunner.html)。


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

```bash
git clone https://git.corpautohome.com/ad-qa/tea.git
cd tea
python setup.py build
python setup.py install
```

## 使用
TEA可用通过多种方式运行，分别如下：
### 命令行
```bash
tea business-eco.yaml
```

### lib库引入项目
```python
from TEA.api import Installer

json_conf = {'kind': 'eco'}
Installer.apply_eco(json_conf)
```

### REST API
```bash
tea.web 8003
```

> 更多配置文件使用方式见下方`配置说明`部分


# 业务逻辑
## 概念说明
TEA项目架构设计和配置设计上均参考k8s，其一可以借鉴k8s成熟的设计思路和理念，其二为以后无缝切入到k8s环境使用做准备。
TEA主要核心对象（概念）：service、eco、module、node、hc、rcmd。

### module
最基础也是最核心的对象，代表需要安装的具体服务。比如：mysql、kafka、adfront、autoax-adpos。
是环境搭建最小的操作粒度。

### eco
表示一个生态圈，是多个module的集合。eco内通常是一组业务相关的模块。比如：业务系统、引擎系统、基础服务。

![001](https://git.corpautohome.com/ad-qa/tea/raw/master/file/image/detail-01.png)

### service
代表一个可用服务的集合，每个service可提供一个完整的服务。service通常有一或多个eco组成。

![002](https://git.corpautohome.com/ad-qa/tea/raw/master/file/image/detail-02.png)

### node
实际部署module的设备，可以是物理机、虚拟机等。

![003](https://git.corpautohome.com/ad-qa/tea/raw/master/file/image/detail-03.png)

### hc
即health check的缩写，用于检查并回复服务、模块进程。

### rcmd
即run command的缩写，主要用于执行远程cmd命令。


# 设计架构
![004](https://git.corpautohome.com/ad-qa/tea/raw/master/file/image/detail-04.png)


# 配置说明
## service
```yaml
apiVersion: v1:beta
kind: service           # 可选值：service、eco、module、hc、rcmd
metadata:               # 服务元数据
  name: service         # 可选值：business、engine、essential
  labels:
    service: service-01
spec:
  ecoSelector:          # 选择组成service的eco
  - business-01
  - engine-01
  - essential-01
  moduleSelector:        # 选择组成service的module，二期版本扩展需求
  - nginx-01
  - mysql-01
  - adfront-01
  - autoax-adpos-01
```

## eco
```yaml
apiVersion: v1:beta
kind: eco           # 可选值：service、eco、module、hc、rcmd
metadata:           # 生态元数据
  name: business    # 可选值：business、engine、essential
  labels:
    eco: business-01
spec:
  modules:
  - name: autoax-adpos
    processName: autoax-adpos
    type: jar
    version: 3.5.0-135
    uri: http://10.168.0.146/online/autoax-adpos-3.5.0-135.x86_64.rpm
    command: ["/home/w/adplatform/adfront/bin/restart.sh"]
    args: ["$(MESSAGE)"]
    log: /home/w/adplatform/adfront/click/log/adfront_click.log-%(date)
    parent: 0
    restartPolicy: Always
    nodeSelector:
      zone: node1
    env:
    - name: ENV
      value: "test"
    config:
      template: ${MESSAGE}
      location: /path/to/location
      data:
      - port: 80
    connect:
      host: 10.168.100.138
      port: 22
      username: testlog
      password: testlog@123
      authType: password
    healthCheck:
      type: tcp
      host: 10.168.100.138
      port: 80
```

## module
```yaml
apiVersion: v1:beta
kind: module        # 可选值：service、eco、module、hc、rcmd、node
metadata:           # 模块元数据
  name: autoax-adpos       # 模块名称 e.g. adx、mysql
  labels:
    module: autoax-adpos-01
spec:
  - name: autoax-adpos
    processName: autoax-adpos
    type: jar
    version: 3.5.0-135
    uri: http://10.168.0.146/online/autoax-adpos-3.5.0-135.x86_64.rpm
    command: ["/home/w/adplatform/adfront/bin/restart.sh"]
    args: ["$(ENV)"]
    log: /home/w/adplatform/adfront/click/log/adfront_click.log-%(date)
    parent: 0
    restartPolicy: Always
    nodeSelector:
    - business-node-01
    env:
    - name: ENV
      value: "test"
    config:
      template: ${MESSAGE}
      location: /path/to/location
      data:
      - port: 80
    healthCheck:
      type: tcp
      host: 10.168.100.138
      port: 80
```

## node
```yaml
apiVersion: v1:beta
kind: node
metadata:           # 模块元数据
  name: node       # 模块名称 e.g. adx、mysql
  labels:
    node: node-01
spec:
  - name: business-node-01
    authType: password
    host: 10.168.100.138
    port: 22
    username: testlog
    password: testlog@123
    moduleAllowed:
    - autoax-adpos
    - autoax-api
    - autoax-creative
  - name: business-node-01
    authType: password
    host: 10.168.100.138
    port: 22
    username: testlog
    password: testlog@123
    moduleAllowed:
    - autoax-adpos
    - autoax-api
    - autoax-creative
```
## hc
```yaml
apiVersion: v1:beta
kind: hc        # 可选值：service、eco、module、hc、rcmd、node
metadata:           # 模块元数据
  name: hc       # 模块名称 e.g. adx、mysql
  labels:
    module: hc-01
spec:
  - name: autoax-adpos
    processName: autoax-adpos
    type: jar
    version: 3.5.0-135
    uri: http://10.168.0.146/online/autoax-adpos-3.5.0-135.x86_64.rpm
    command: ["/home/w/adplatform/adfront/bin/restart.sh"]
    args: ["$(MESSAGE)"]
    log: /home/w/adplatform/adfront/click/log/adfront_click.log-%(date)
    parent: 0
    restartPolicy: Always
    nodeSelector:
    - business-node-01
    env:
    - name: ENV
      value: "test"
    config:
      template: ${MESSAGE}
      location: /path/to/location
      data:
      - port: 80
    healthCheck:
      type: tcp
      host: 10.168.100.138
      port: 80
```

## rcmd
```yaml
apiVersion: v1:beta
kind: rcmd          # 可选值：service、eco、module、hc、rcmd、node
metadata:           # 元数据
  name: getlog
spec:
  - name: adfront-log
    command: ["tailf"]
    args: ["/home/w/adplatform/adfront/click/log/adfront_click.log-%(date)"]
    nodeSelector:
    - business-node-01
    env:
    - name: ENV
      value: "test"

```

# 开发相关
# 如何为node机器添加一个ssh用户
```bash
useradd testlog
passwd testlog
# 输入密码: testlog@123

vim /etc/sudoers
# 文件尾部添加
testlog    ALL=(ALL)    NOPASSWD: ALL

# 将 Defaults    requiretty 修改为
Defaults:testlog    !requiretty
```
