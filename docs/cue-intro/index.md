# CUE是何方神圣?


## 导读
> 本片文章主要介绍 CUE 的基本概念，CUE 是什么以及可以做些什么，通过一些 demo 演示了基本的用法，适合小白入门阅读。

## 什么是CUE
C(Configure：配置) , U(Unify：统一) , E(Execute：执行) 。

CUE是一种开源的数据约束语言，旨在简化涉及定义和使用数据的任务。

它是JSON的超集，允许熟悉JSON的用户快速上手。

> 换言之，他和JSON、YAML 等类似，但是比他们的功能强大，可以和 JSON、YAML 等工具对比着来理解。

## CUE 可以用来做什么
我们可以用CUE ： 

- 定义一个详细的验证模式
- 减少数据中的模版
- 从代码中提取模式
- 产生类型定义和验证代码
- 以一种有原则的方式合并JSON
- 定义和运行声明性脚本

## How
CUE合并了模式和数据的概念。同一个CUE定义可以同时用于验证数据和作为模板来减少模板。模式定义通过细粒度的值定义和缺省值得到了丰富。同时，通过删除这些详细定义所隐含的值，可以简化数据。这两个概念的合并使得许多任务能够以一种原则性的方式被处理。

约束提供了一个简单的、定义明确的、但功能强大的、替代继承的方法，而继承是配置语言中常见的复杂性来源。

### CUE脚本
CUE脚本层定义了声明性的脚本，用CUE表达，在数据之上。这解决了三个问题：解决了CUE定义的封闭性（我们说CUE是密封的），提供了一个简单的方法来分享使用数据的通用脚本和工作流程，并让CUE知道如何使用数据来优化验证。

有很多工具可以解释数据或者为特定领域使用专门的语言（Kustomize, Ksonnet）。这在一个层面上解决了处理数据的问题，但它解决的问题在工作流程中整合其他系统时可能会在更高的层面上重复出现。CUE脚本是通用的，允许用户定义任何工作流程。

## 安装
如果是 Mac 环境 ，执行下面的命令安装:
```shell script
brew install cuelang/tap/cue
```

其他环境通过 golang 安装（当然 mac 也是可以的）
```shell script
# go 1.16 之前
GO111MODULE=on go get cuelang.org/go/cmd/cue

# go 1.16 之后
go install cuelang.org/go/cmd/cue@latest
```

详细可参考 [安装文档](https://github.com/cuelang/cue/blob/master/doc/install.md)

安装完之后可以通过命令行执行 `cue --help` 查看基本的帮助文档。

```shell script
cue --help
cue evaluates CUE files, an extension of JSON, and sends them
to user-defined commands for processing.

Commands are defined in CUE as follows:

	import "tool/exec"
	command: deploy: {
		exec.Run
		cmd:   "kubectl"
		args:  [ "-f", "deploy" ]
		in:    json.Encode(userValue) // encode the emitted configuration.
	}

cue can also combine the results of http or grpc request with the input
configuration for further processing. For more information on defining commands
run 'cue help cmd' or go to cuelang.org/pkg/cmd.

For more information on writing CUE configuration files see cuelang.org.

Usage:
  cue [command]

Available Commands:
  cmd         run a user-defined shell command
  completion  Generate completion script
  def         print consolidated definitions
  eval        evaluate and print a configuration
  export      output data in a standard format
  fix         rewrite packages to latest standards
  fmt         formats CUE configuration files
  get         add dependencies to the current module
  help        Help about any command
  import      convert other formats to CUE files
  mod         module maintenance
  trim        remove superfluous fields
  version     print CUE version
  vet         validate data

Flags:
  -E, --all-errors   print all available errors
  -h, --help         help for cue
  -i, --ignore       proceed in the presence of errors
  -s, --simplify     simplify output
      --strict       report errors for lossy mappings
      --trace        trace computation
  -v, --verbose      print information about progress

Additional help topics:
  cue commands   user-defined commands
  cue filetypes  supported file types and qualifiers
  cue flags      common flags for composing packages
  cue injection  inject files or values into specific fields for a build
  cue inputs     package list, patterns, and files

Use "cue [command] --help" for more information about a command.
```

下面通过一些具体的例子看看如何使用 CUE 。

## JSON 超集
CUE是JSON的一个超集。它增加了以下的便利性。

- C风格的注释。
- 引号可以从字段名中省略，没有特殊字符。
- 字段末尾的逗号是可选的。
- 列表中最后一个元素后的逗号是允许的。
- 外层大括号是可选的。

JSON对象在CUE中被称为结构。一个对象的成员被称为一个字段。

假设我们有 `json.cue` 文件如下 : 

```
one: 1
two: 2

// A field using quotes.
"two-and-a-half": 2.5

list: [
	1,
	2,
	3,
]

m: {
    key1: "v1"
    key2: "v2"
}
```

可以通过 `cue export json.cue ` 看看生成之后的 json 数据 :
```json
{
    "one": 1,
    "two": 2,
    "two-and-a-half": 2.5,
    "list": [
        1,
        2,
        3
    ],
    "m": {
        "key1": "v1",
        "key2": "v2"
    }
}
``` 

- cue export 可以把 cue 文件转化成 `json`、`yaml`、`text` 等类型的文件
    - 转化成 json `cue export json.cue --out json`
    - 转化成 yaml `cue export json.cue --out yaml`
    - 转化成 text `cue export json.cue --out text`
- 输出到文件 `cue export json.cue --out json --outfile json.cue.json`

可以通过 `cue help export` 查看详细的帮助文档 


## 类型是值
CUE合并了值和类型的概念。下面是这个demo的演示，分别展示了一些数据，这个数据的可能模式，以及介于两者之间的东西：一个典型的CUE约束条件。

Data
```
moscow: {
  name:    "Moscow"
  pop:     11.92M
  capital: true
}
```

Schema
```
municipality: {
  name:    string
  pop:     int
  capital: bool
}
```

CUE：
```
largeCapital: {
  name:    string
  pop:     >5M
  capital: true
}
```

一般来说，在CUE中，人们从一个广义的模式定义开始，描述所有可能的实例，然后针对特定的用例缩小这些定义的范围，直到剩下一个具体的数据实例。

## 重复的字段
- CUE允许重复的字段定义，只要它们不冲突。
- 对于基本类型的值，这意味着它们必须是相等的。
- 对于结构，字段被合并，重复的字段被递归处理。
- 对于列表，所有的元素必须相应地匹配

假设的 `dup.cue` 内容如下 : 
```
a: 4
a: 4

s: { b: 2 }
s: { c: 2 }

l: [ 1, 2 ]
l: [ 1, 2 ]
``` 

通过 `cue eval dup.cue` 可以得到合并后的内容 ：
```
a: 4
s: {
    b: 2
    c: 2
}
l: [1, 2]
```

- 也可以通过 `export` 命令生成 json/yaml 等文件看一下

如果key一样，但是value 不一样，会有什么样的情况呢 ，修改 `dup.cue` 的文件内容如下 : 

```
a: 4
a: 5

s: { b: 2 }
s: { c: 2 }

l: [ 1, 2 ]
l: [ 1, 3 ]
```

这时再次执行 `cue eval dup.cue `，则会报错 :
``` 
a: conflicting values 5 and 4:
    ./dup.cue:1:4
    ./dup.cue:2:4
l.1: conflicting values 3 and 2:
    ./dup.cue:7:9
    ./dup.cue:8:9
```

## 限制条件
约束规定了哪些值是允许的。对CUE来说，它们只是像其他东西一样的值，但在概念上，它们可以被解释为介于类型和具体值之间的东西。

但是约束也可以减少模板。如果一个约束定义了一个具体的值，那么就没有必要在这个约束所适用的值中指定它。

假设 `check.cue` 文件如下 :
```
schema: {
    name:  string
    age:   int
    human: true // always true
}

viola: schema
viola: {
    name: "Viola"
    age:  38
}
```

这个文件的含义如下 : 

- `schema` 定义了约束， `human` 只能为 true ，后续在赋值时不能修改为其他的值，否则会报错
- `viola: schema` 表示继承了 `schema` 的定义，引用了 `schema` 的约束
- `viola: { ...` 是真正的赋值

执行 ` cue eval check.cue` 可以看到渲染之后的数据 

```
schema: {
    name:  string
    age:   int
    human: true
}
viola: {
    name:  "Viola"
    age:   38
    human: true
}
```

这时把 `check.cue` 修改成如下这样会有什么样的输入呢 ?
```
schema: {
    name:  string
    age:   int
    human: true // always true
}
viola: schema
viola: {
    name: "Viola"
    age:  38
    human: false
}
```

执行 ` cue eval check.cue ` 
```
viola.human: conflicting values false and true:
    ./check.cue:4:12
    ./check.cue:6:8
    ./check.cue:10:12
```

可以看到给 human 赋值为 false 报错了

## Definitions
在CUE中，模式通常被写成 `定义` 。`定义` 是一个字段，其标识符以#或_#开头。这告诉CUE它们是用来验证的，不应该作为数据输出；它们可以不被指定。

一个 `定义` 也告诉CUE允许的全部字段。换句话说，`定义` 定义了 "封闭 "的结构。在结构中包括一个...可以使其保持开放。

假设 `schema.cue` 文件内容如下 : 
```
#Conn: {
    address:  string
    port:     int
    protocol: string
    // ...    // uncomment this to allow any field
}

lossy: #Conn & {
    address:  "1.2.3.4"
    port:     8888
    protocol: "udp"
    // foo: 2 // uncomment this to get an error
}
```

- `#Conn` 申明了一个定义
- `lossy` 引用了这个定义并且实例化数据，在实例化时会按照 schema 进行校验，在如下情况都会报错
    - 多了字段
    - 少了字段
    - 字段类型不匹配 

执行 `cue export schema.cue ` 查看 ：

```json
{
    "lossy": {
        "address": "1.2.3.4",
        "port": 8888,
        "protocol": "udp"
    }
}
```

## 验证
约束条件可以用来验证具体实例的值。它们可以应用于CUE数据，或直接应用于YAML或JSON。

假设 `schema.cue` 内容如下 ： 

```
#Language: {
	tag:  string
	name: =~"^\\p{Lu}" // Must start with an uppercase letter.
}
languages: [...#Language]
```

- `languages: [...#Language]` 可变长的一个列表 ，可以对照 `languages: [#Language]` 的 eval  输出看一下区别
    ```
    // languages: [...#Language] 的输出
    #Language: {
        tag:  string
        name: =~"^\\p{Lu}"
    }
    languages: []
   // languages: [#Language] 的输出
    #Language: {
        tag:  string
        name: =~"^\\p{Lu}"
    }
    languages: [{
        tag:  string
        name: =~"^\\p{Lu}"
    }]
    ```
`data.yaml` 的内容如下 : 

```yaml
languages:
  - tag: en
    name: English
  - tag: nl
    name: dutch
  - tag: no
    name: Norwegian
```

执行 `cue vet schema.cue data.yaml` 可以看到会报错 
```
languages.1.name: invalid value "dutch" (does not match =~"^\\p{Lu}"):
    ./schema.cue:3:8
    ./data.yaml:5:12
```

- dutch 验证失败，必须以大写字母开头

## 顺序不重要
CUE的基本操作是这样定义的：你结合两个配置的顺序与结果无关。

这是CUE的关键属性，它使人类和机器很容易对数值进行推理，并使高级工具和自动化成为可能。

假设 `order.cue` 内容如下 : 

```
a: {x: 1, y: int}
a: {x: int, y: 2}

b: {x: int, y: 2}
b: {x: 1, y: int}
```

执行 `cue eval order.cue ` 得到 ：

```
a: {
    x: 1
    y: 2
}
b: {
    x: 1
    y: 2
}
```

- 可以看到，定义和赋值谁先谁后都没有影响

## 单项结构的折叠
在JSON中，人们定义了嵌套值，一次一个值。另一种方式是，JSON配置是一组路径-值对。

在CUE中，人们定义了一组路径，并一次性地应用具体的值或约束条件。由于CUE的顺序独立性，数值会被合并。

这个例子显示了一些路径值对，以及一个应用于这些路径值的约束来验证它们。

`fold.cue` 内容如下 : 
```
// path-value pairs
outer: middle1: inner: 3
outer: middle2: inner: 7

// collection-constraint pair
outer: [string]: inner: int
```

执行 `cue export fold.cue` 
```json
{
    "outer": {
        "middle1": {
            "inner": 3
        },
        "middle2": {
            "inner": 7
        }
    }
}
```

## 总结
这里简单的介绍了什么是CUE以及基本用法，可以和 JSON、YAML 等工具进行对比理解。后面的文档会介绍 kubernetes 是如何使用 CUE 工具的。

## 参考
- https://cuelang.org/docs/tutorials/tour/intro/
- https://github.com/cuelang/cue


