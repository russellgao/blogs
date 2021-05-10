+++
title = "如何利用python优化解析xml文件"
description = "如何利用python优化解析xml文件"
date = "2021-03-02"
aliases = ["如何利用python优化解析xml文件"]
author = "russellgao"
draft = false
tags = [
    "python",
    "xml" ,
    "pom" ,
    "maven"
]

categories = [
    "python"
]

+++

## 导读
> 本篇文章意在演示如何利用 python 解析 xml 文件。这篇文章的引出背景是，在程序开发过程中，一贯坚持的做法是「约定优于配置」，
>但怎么取检测有没有按照约定去做的，以 maven 为例，maven 提供了 `maven-enforcer-plugin` 插件，可以用这个插件定制一系列
>规则。所以我们需要做的就是用 python 在 pom 文件中插入 `maven-enforcer-plugin` 的配置 。
>
> python 环境: 3.8
> 
> 本文首发于 [https://russellgao.cn/python-maven-enforcer-plugins/](https://russellgao.cn/python-maven-enforcer-plugins/) ,转载请注明原文出处。

## 目标
拿到一个 pom.xml 文件之后，python 实现对其插入 `maven-enforcer-plugin` ，然后进行 `mvn validate` 。
pom.xml 选取以开源项目 arthas 为例 : [https://raw.githubusercontent.com/alibaba/arthas/master/pom.xml](https://raw.githubusercontent.com/alibaba/arthas/master/pom.xml) 

maven-enforcer-plugin 配置如下 :
```xml
<plugin>
<groupId>org.apache.maven.plugins</groupId>
<artifactId>maven-enforcer-plugin</artifactId>
<version>3.0.0-M3</version>
<executions>
  <execution>
    <id>enforce-no-snapshots</id>
    <goals>
      <goal>enforce</goal>
    </goals>
    <configuration>
      <rules>
        <requireReleaseDeps>
          <message>No Snapshots Allowed!</message>
        </requireReleaseDeps>
      </rules>
      <fail>true</fail>
    </configuration>
  </execution>
</executions>
</plugin>
```

需要实现的就是 `maven-enforcer-plugin` 的内容集成到 pom.xml 文件中。接下来主要介绍如何用 python 自动化的实现。

## 解析 
解析主要用到了 `xml` 库进行解析，详细用法可以参考 [官方文档](https://docs.python.org/zh-cn/3/library/xml.etree.elementtree.html)

加载数据: 
```python
import xml.etree.ElementTree as ET
tree = ET.parse('pom.xml')
root = tree.getroot()
```

或者
```python
import xml.etree.ElementTree as ET
tree = ET.fromstring(open('pom.xml').read())
root = tree.getroot()
```

迭代子节点: 

```python
for child in root :
    print(child.tag)

### 输出如下: 
{http://maven.apache.org/POM/4.0.0}modelVersion
{http://maven.apache.org/POM/4.0.0}parent
{http://maven.apache.org/POM/4.0.0}licenses
{http://maven.apache.org/POM/4.0.0}scm
{http://maven.apache.org/POM/4.0.0}developers
{http://maven.apache.org/POM/4.0.0}groupId
{http://maven.apache.org/POM/4.0.0}artifactId
{http://maven.apache.org/POM/4.0.0}version
{http://maven.apache.org/POM/4.0.0}packaging
{http://maven.apache.org/POM/4.0.0}name
{http://maven.apache.org/POM/4.0.0}description
{http://maven.apache.org/POM/4.0.0}url
{http://maven.apache.org/POM/4.0.0}modules
{http://maven.apache.org/POM/4.0.0}profiles
{http://maven.apache.org/POM/4.0.0}properties
{http://maven.apache.org/POM/4.0.0}dependencyManagement
{http://maven.apache.org/POM/4.0.0}build
```

可以到看到前面多了一段 `{http://maven.apache.org/POM/4.0.0}` ，这是什么情况？

原来这个 pom 文件是带了namespace :
```xml
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
```

xmlns 指定 namespace 为 : `http://maven.apache.org/POM/4.0.0` ，所以我们后续寻找子节点时需要带上 namespace 。 

查找子节点(子元素): ET 提供 `findall()` 和 `find()` 方法可以找出 xml 中的子元素，其中 ：

- findall 仅查找当前元素的直接子元素中带有指定标签的元素
- 找带有特定标签的 第一个 子级，然后可以用 Element.text 访问元素的文本内容。 Element.text 访问元素的属性

```shell script
build_node = root.find('%sbuild' % pomNamespace)
plugins_node = build_node.find('{}plugins'.format(pomNamespace))
plugins_node_all = plugins_node.findall('{}plugin'.format(pomNamespace))
```

新增一个节点: 
```python
def build_plugin_node(e: ET.Element, namespace: str) -> None:
    """
    新增子元素
    :param e: 父节点
    :param namespace: namespace
    :return: 
    """
    node = ET.SubElement(e, '{}plugin'.format(namespace))
    ET.SubElement(node, "{}groupId".format(namespace)).text = 'org.apache.maven.plugins'
    ET.SubElement(node, "{}artifactId".format(namespace)).text = 'maven-enforcer-plugin'
    ET.SubElement(node, "{}version".format(namespace)).text = '3.0.0-M3'
    _n4 = ET.SubElement(node, "{}executions".format(namespace))
    _e = ET.SubElement(_n4, '{}execution'.format(namespace))
    _e_id = ET.SubElement(_e, "{}id".format(namespace)).text = 'enforce-versions'
    _e_phase = ET.SubElement(_e, "{}phase".format(namespace)).text = 'validate'
    _e_goals = ET.SubElement(_e, "{}goals".format(namespace))
    _e_cfg = ET.SubElement(_e, "{}configuration".format(namespace))
    _e_rules = ET.SubElement(_e_cfg, "{}rules".format(namespace))
    _e_fail = ET.SubElement(_e_cfg, "{}fail".format(namespace)).text = 'true'
    _e_requireReleaseDeps = ET.SubElement(_e_rules, "{}requireReleaseDeps".format(namespace))
    ET.SubElement(_e_requireReleaseDeps, '{}message'.format(namespace)).text = 'No Snapshots Allowed!'
    _e_excludes = ET.SubElement(_e_requireReleaseDeps, "{}excludes".format(namespace))
    ET.SubElement(_e_excludes, '{}exclude'.format(namespace)).text = '${project.groupId}:*'
    _e_goal = ET.SubElement(_e_goals, "{}goal".format(namespace)).text = 'enforce'
build_plugin_node(plugins_node, pomNamespace)
```

把修改后写到 新的文件 :
```python
tree.write('pom-new.xml')
```
写到文件大家会惊奇的发现好像不太对哎:

```xml
<ns0:plugin>
    <ns0:groupId>org.apache.maven.plugins</ns0:groupId>
    <ns0:artifactId>maven-enforcer-plugin</ns0:artifactId>
    <ns0:version>3.0.0-M3</ns0:version>
    <ns0:executions>
        <ns0:execution>
            <ns0:id>enforce-versions</ns0:id>
            <ns0:phase>validate</ns0:phase>
            <ns0:goals>
                <ns0:goal>enforce</ns0:goal>
            </ns0:goals>
            <ns0:configuration>
                <ns0:rules>
                    <ns0:requireReleaseDeps>
                        <ns0:message>No Snapshots Allowed!</ns0:message>
                        <ns0:excludes>
                            <ns0:exclude>${project.groupId}:*</ns0:exclude>
                        </ns0:excludes>
                    </ns0:requireReleaseDeps>
                </ns0:rules>
                <ns0:fail>true</ns0:fail>
            </ns0:configuration>
        </ns0:execution>
    </ns0:executions>
</ns0:plugin>
```

为啥会多 `ns0` ? 还是因为 namespace 的原因，需要注册一下namespace :
```python
ns_name = ""
ns_value = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace(ns_name, ns_value)
tree.write('pom-new.xml')
```
这时才会得到满意的结果。

整体的脚本如下 :
```python
# !/usr/bin/env python

import xml.etree.ElementTree as ET

def build_plugin_node(e: ET.Element, namespace: str) -> None:
    """
    新增子元素
    :param e: 父节点
    :param namespace: namespace
    :return:
    """
    node = ET.SubElement(e, '{}plugin'.format(namespace))
    ET.SubElement(node, "{}groupId".format(namespace)).text = 'org.apache.maven.plugins'
    ET.SubElement(node, "{}artifactId".format(namespace)).text = 'maven-enforcer-plugin'
    ET.SubElement(node, "{}version".format(namespace)).text = '3.0.0-M3'
    _n4 = ET.SubElement(node, "{}executions".format(namespace))
    _e = ET.SubElement(_n4, '{}execution'.format(namespace))
    _e_id = ET.SubElement(_e, "{}id".format(namespace)).text = 'enforce-versions'
    _e_phase = ET.SubElement(_e, "{}phase".format(namespace)).text = 'validate'
    _e_goals = ET.SubElement(_e, "{}goals".format(namespace))
    _e_cfg = ET.SubElement(_e, "{}configuration".format(namespace))
    _e_rules = ET.SubElement(_e_cfg, "{}rules".format(namespace))
    _e_fail = ET.SubElement(_e_cfg, "{}fail".format(namespace)).text = 'true'
    _e_requireReleaseDeps = ET.SubElement(_e_rules, "{}requireReleaseDeps".format(namespace))
    ET.SubElement(_e_requireReleaseDeps, '{}message'.format(namespace)).text = 'No Snapshots Allowed!'
    _e_excludes = ET.SubElement(_e_requireReleaseDeps, "{}excludes".format(namespace))
    ET.SubElement(_e_excludes, '{}exclude'.format(namespace)).text = '${project.groupId}:*'
    _e_goal = ET.SubElement(_e_goals, "{}goal".format(namespace)).text = 'enforce'


def main() :
    pomNamespace = '{http://maven.apache.org/POM/4.0.0}'
    ns_name = ""
    ns_value = "http://maven.apache.org/POM/4.0.0"
    ET.register_namespace(ns_name, ns_value)
    tree = ET.parse('pom.xml')
    root = tree.getroot()
    build_node = root.find('%sbuild' % pomNamespace)
    plugins_node = build_node.find('{}plugins'.format(pomNamespace))
    build_plugin_node(plugins_node, pomNamespace)
    tree.write('pom-new.xml')

if __name__ == "__main__" :
    main()
```


得到了新的文件 `pom-new.xml` 之后就可以愉快的调用 maven 命令进行检查了 ,如 :
```shell script
mvn validate -f pom-new.xml
```

这个流程常用于 `CI` 过程中，可以帮助检查开发人员有没有遵守相关代码规范。

## 扩展
### maven-enforcer-plugin 常用规则
官方提供的常用规则参考： [http://maven.apache.org/enforcer/enforcer-rules/index.html](http://maven.apache.org/enforcer/enforcer-rules/index.html)

- 是否在 relase 版本中依赖了 SNAPSHOT 版本
- java version
- maven version
- 检查环境变量
- ....

### xml.etree.ElementTree 的其他用法
修改元素文本字段

```python
plugins_node.text = 'plugins-test'
```

给元素增加属性:

```python
plugins_node.set('k1', 'v1')
plugins_node.set('k2', 4)
plugins_node.set('k3', True)
```

删除元素 :
```python
modelVersion = root.find('{}modelVersion'.format(pomNamespace))
root.remove(modelVersion)
```

## 参考
- https://docs.python.org/zh-cn/3/library/xml.etree.elementtree.html
- http://maven.apache.org/enforcer/enforcer-rules/index.html
