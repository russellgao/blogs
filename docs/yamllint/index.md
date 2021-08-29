# yamllint 用法



## 导读
> yaml 文件现在是比较流行的一种配置文件，在使用的时候发现配置很容易出错，导致无法使用，这篇文章主要推荐一种检查 yaml 基本语法的工具--yamllint 。
> 文章中内容主要参考官方文档。

## 简介
- 作用: yaml 语法检查工具，可以帮助使用者快速发现 yaml 的文件错误。
- 开发语言: python


## 安装
### Fedora / CentOS
sudo dnf install yamllint

### Debian 8+ / Ubuntu 16.04+
sudo apt-get install yamllint

### Mac OS 10.11+
brew install yamllint

### FreeBSD
pkg install py36-yamllint

### pip 安装
pip install --user yamllint

## 基本用法
第一次使用可以通过 `-h` 查看基本的帮助
```shell script
yamllint -h
usage: yamllint [-h] [-] [-c CONFIG_FILE | -d CONFIG_DATA]
                [-f {parsable,standard,colored,github,auto}] [-s]
                [--no-warnings] [-v]
                [FILE_OR_DIR [FILE_OR_DIR ...]]

A linter for YAML files. yamllint does not only check for syntax validity, but
for weirdnesses like key repetition and cosmetic problems such as lines
length, trailing spaces, indentation, etc.

positional arguments:
  FILE_OR_DIR           files to check

optional arguments:
  -h, --help            show this help message and exit
  -                     read from standard input
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        path to a custom configuration
  -d CONFIG_DATA, --config-data CONFIG_DATA
                        custom configuration (as YAML source)
  -f {parsable,standard,colored,github,auto}, --format {parsable,standard,colored,github,auto}
                        format for parsing output
  -s, --strict          return non-zero exit code on warnings as well as
                        errors
  --no-warnings         output only error level problems
  -v, --version         show program's version number and exit
```

```shell script
# 检查单个文件
yamllint file.yml other-file.yaml
```

```shell script
# 检查当前文件夹下所有的文件
yamllint .
```

从输入流中检查
```shell script
echo -e 'this: is\nvalid: YAML' | yamllint -
```
输出类似这样 ![](https://gitee.com/russellgao/blogs-image/raw/master/images/yaml/yamllint1.png)

在终端中默认是带颜色的，可以通过 `-f` 参数控制是否带颜色， `-f standard` 表示标准输出不带颜色， `-f colored` 带颜色

yamllint 默认检查的比较多，可以通过 -c 指定 配置文件，配置yamllint 的检查规则，-c 的默认文件为： `./.yamllint` ，所以默认可以在项目的根路径下增加 `.yamllint`。

## 配置
如果没有指定 `-c` ，则会按照如下规则进行查找配置文件

- 在当前文件夹下找 `.yamllint`, `.yamllint.yaml` ,`.yamllint.yml`
- 通过环境变量 `$YAMLLINT_CONFIG_FILE` 查找
- $XDG_CONFIG_HOME/yamllint/config
- ~/.config/yamllint/config

默认的配置如下: 
```yaml
---

yaml-files:
  - '*.yaml'
  - '*.yml'
  - '.yamllint'

rules:
  braces: enable
  brackets: enable
  colons: enable
  commas: enable
  comments:
    level: warning
  comments-indentation:
    level: warning
  document-end: disable
  document-start:
    level: warning
  empty-lines: enable
  empty-values: disable
  hyphens: enable
  indentation: enable
  key-duplicates: enable
  key-ordering: disable
  line-length: enable
  new-line-at-end-of-file: enable
  new-lines: enable
  octal-values: disable
  quoted-strings: disable
  trailing-spaces: enable
  truthy:
    level: warning
```

除了这个默认的配置还有一个预定于的 `relaxed` 配置，看名字应该可以看出这是一个宽松的配置，`-d relaxed` 进行使用
```yaml
---

extends: default

rules:
  braces:
    level: warning
    max-spaces-inside: 1
  brackets:
    level: warning
    max-spaces-inside: 1
  colons:
    level: warning
  commas:
    level: warning
  comments: disable
  comments-indentation: disable
  document-start: disable
  empty-lines:
    level: warning
  hyphens:
    level: warning
  indentation:
    level: warning
    indent-sequences: consistent
  line-length:
    level: warning
    allow-non-breakable-inline-mappings: true
  truthy: disable
```

如: 
```shell script
yamllint -d relaxed  file1.yaml file2.yaml 
```
![](https://gitee.com/russellgao/blogs-image/raw/master/images/yaml/yamllint2.png)

### 扩展默认配置
如果想写一个定制化的配置，可以扩展默认配置，如：只想 disable `comments-indentation` ，则配置可以这样写：
```yaml
extends: default

rules:
  comments-indentation: disable  # don't bother me with this rule
```

### YAML files extensions
可以配置 yamllint 检查哪些文件 
```yaml
yaml-files:
  - '*.yaml'
  - '*.yml'
  - '.yamllint'
```

### 忽略部分文件
可以通过 `ignore` 字段进行忽略不想检查的文件
```yaml
# For all rules
ignore: |
  *.dont-lint-me.yaml
  /bin/
  !/bin/*.lint-me-anyway.yaml

extends: default

rules:
  key-duplicates:
    ignore: |
      generated
      *.template.yaml
  trailing-spaces:
    ignore: |
      *.ignore-trailing-spaces.yaml
      ascii-art/*
```

## 最佳实践
yamllint 可以集成在 VCS 的 hook 中，如 项目使用 gitlab 做代码管理，可以使用在 git hook 中增加 yamllint 流程，在代码提交时强制检查，不符合规范不能提交，
或者 CI 流程中增加 yamllint 检查，趁早发现一些问题，避免引发线上问题。

## 参考
- https://yamllint.readthedocs.io/en/stable/


