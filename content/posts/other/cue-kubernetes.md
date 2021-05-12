+++
title = "CUE 是如何在 Kubernetes 中使用的"
date = "2021-05-10"
author = "russellgao"
draft = false
tags = [
    "kubernetes",
    "cue" 
]
categories = [
    "cue" ,
    "kubernetes"
]

+++

## 导读
> 本文是基于上一篇 [CUE是何方神圣](https://russellgao.cn/cue-intro/) 基本介绍后，结合 kubernetes ，看看 kubernetes 是如何使用 CUE 的，内容主要来自 [官方教程](https://github.com/cuelang/cue/tree/master/doc/tutorial/kubernetes) 。
>
> 希望学完本篇内容之后可以对 CUE 有一个感性的认知。
>
> 我们将会从如下几个方面介绍 ：
>- 将给定的YAML文件转换为CUE
>- 将常见的模式提升到父目录
>- 使用工具重写CUE文件，删除不必要的字段
>- 对不同的子目录重复步骤2的内容
>- 定义命令，对配置进行操作
>- 直接从Kubernetes Go源代码中提取CUE模板
>- 手动调整配置
>

## 数据准备
本文需要用到的 demo 文件参见官方仓库 https://github.com/cuelang/cue/tree/master/doc/tutorial/kubernetes/original 。

> 由于 github 访问比较慢，可以从 [此处下载](https://gitee.com/russellgao/cue-tutorial/tree/master)

这个数据集是基于一个真实的案例，使用不同的服务名称。真实设置中的所有不一致之处都被复制到文件中，以获得对转换到CUE的实际行为的真实印象。

给出的YAML文件在以下目录中排序

```shell script
$ tree ./original | head
.
└── services
    ├── frontend
    │   ├── bartender
    │   │   └── kube.yaml
    │   ├── breaddispatcher
    │   │   └── kube.yaml
    │   ├── host
    │   │   └── kube.yaml
    │   ├── maitred
...
```
每个子目录包含相关的微服务，这些微服务通常具有类似的特征和配置。这些配置包括大量的Kubernetes对象，包括 `services`、`deployments`、`config maps`、`a daemon set`、`a stateful set`、 `a cron job`。

## 导入现有配置
首先把这个复制到临时目录 `tmp`
```shell script
$ cp -a original tmp
$ cd tmp
```
我们初始化一个模块，这样我们就可以把子目录中的所有配置文件作为一个包的一部分。稍后我们通过给所有的包起相同的名字来实现这一点。
```shell script
cue mod init
```
我们初始化一个Go模块，以便以后可以解决k8s.io/api/apps/v1 Go包的依赖性。
```shell script
go mod init russellgao.com
```
创建一个模块也允许我们的包导入外部包。

让我们尝试使用cue import命令将给定的YAML文件转换为CUE。

```shell script
$ cd services
$ cue import ./...
must specify package name with the -p flag
```
由于我们有多个包和文件，我们需要指定它们应该属于哪个包。

```shell script
$ cue import ./... -p kube
path, list, or files flag needed to handle multiple objects in file "./frontend/bartender/kube.yaml"
```
许多文件包含一个以上的Kubernetes对象。此外，我们正在创建一个包含所有文件的所有对象的单一配置。我们需要组织所有的Kubernetes对象，使每个对象在单个配置中可以单独识别。我们通过为每种类型定义一个不同的结构，将每个对象放在这个以其名称为关键的结构中。这允许不同类型的对象共享相同的名称，就像Kubernetes允许的那样。为了达到这个目的，我们告诉cue把每个对象放在配置树中，路径是 "种类 "为第一元素，"名称 "为第二元素。

```shell script
$ cue import ./... -p kube -l 'strings.ToCamel(kind)' -l metadata.name -f
```

添加的-l标志根据每个对象的值，使用通常的CUE语法为字段标签定义了每个对象的标签。在这种情况下，我们使用每个对象的kind字段的camelcase变体，并使用元数据部分的name字段作为每个对象的名称。我们还添加了-f标志，以覆盖之前成功的几个文件。

看看发生了什么 

```shell script
$ tree . | head
.
└── services
    ├── frontend
    │   ├── bartender
    │   │   ├── kube.cue
    │   │   └── kube.yaml
    │   ├── breaddispatcher
    │   │   ├── kube.cue
    │   │   └── kube.yaml
...
```
每个YAML文件都被转换为相应的CUE文件。YAML文件的注释被保留下来。

不过，结果并不完全令人满意。看看 `mon/prometheus/configmap.cue`

```shell script
$ cat mon/prometheus/configmap.cue
package kube

apiVersion: "v1"
kind:       "ConfigMap"
metadata: name: "prometheus"
data: {
    "alert.rules": """
        groups:
        - name: rules.yaml
...

```
配置文件仍然包含YAML嵌入其中一个字段的字符串值。原来的YAML文件可能看起来都是结构化的数据，但其中大部分是一个字符串，包含了希望是有效的YAML。

`-R` 选项试图检测嵌入在配置文件中的结构化YAML或JSON字符串，然后递归地转换这些字符串。
```shell script
$ cue import ./... -p kube -l 'strings.ToCamel(kind)' -l metadata.name -f -R
```

```shell script
$ cat mon/prometheus/configmap.cue
package kube

import "encoding/yaml"

configMap: prometheus: {
    apiVersion: "v1"
    kind:       "ConfigMap"
    metadata: name: "prometheus"
    data: {
        "alert.rules": yaml.Marshal(_cue_alert_rules)
        _cue_alert_rules: {
            groups: [{
...
```

这看起来好多了! 由此产生的配置文件取代了原来嵌入的字符串，调用yaml.Marshal将结构化的CUE源转换为具有同等YAML文件的字符串。以下划线(_)开头的字段在发送配置文件时不包括在内（当用双引号括起来时则包括在内）。

```shell script
$ cue eval ./mon/prometheus -e configMap.prometheus
apiVersion: "v1"
kind: "ConfigMap"
metadata: {
    name: "prometheus"
}
data: {
    "alert.rules": """
    groups:
    - name: rules.yaml
...
```
-e 表示只计算 configMap.prometheus 

## Quick 'n Dirty Conversion
在本教程中，我们展示了如何快速消除一组配置中的模板。人工定制通常会得到更好的结果，但需要相当多的思考，而采取快速和肮脏的方法可以让你基本达到目的。这种快速转换的结果也为更深思熟虑的手工优化打下了良好的基础。

### 创建顶层模板
现在我们已经导入了YAML文件，可以开始简化过程了。

在我们开始重组之前，让我们保存一个完整的评估，以便我们可以验证简化后的结果是相同的。

```shell script
cue eval -c ./... > snapshot
```
-c选项告诉cue，只允许具体的值，也就是有效的JSON。我们专注于各种kube.cue文件中定义的对象。快速检查发现，许多部署和服务共享共同的结构。

我们将包含这两者的文件之一复制到目录树的根部，作为创建我们模板的基础。
```shell script
$ cp frontend/breaddispatcher/kube.cue .
```
按以下方式修改该文件。
```
$ cat <<EOF > kube.cue
package kube

service: [ID=_]: {
    apiVersion: "v1"
    kind:       "Service"
    metadata: {
        name: ID
        labels: {
            app:       ID    // by convention
            domain:    "prod"  // always the same in the given files
            component: string  // varies per directory
        }
    }
    spec: {
        // Any port has the following properties.
        ports: [...{
            port:       int
            protocol:   *"TCP" | "UDP"      // from the Kubernetes definition
            name:       string | *"client"
        }]
        selector: metadata.labels // we want those to be the same
    }
}

deployment: [ID=_]: {
    apiVersion: "apps/v1"
    kind:       "Deployment"
    metadata: name: ID
    spec: {
        // 1 is the default, but we allow any number
        replicas: *1 | int
        template: {
            metadata: labels: {
                app:       ID
                domain:    "prod"
                component: string
            }
            // we always have one namesake container
            spec: containers: [{ name: ID }]
        }
    }
}
EOF
```
通过用 `[ID=_]` 替换服务和部署名称，我们把定义变成了一个匹配任何字段的模板。CUE将字段名与ID绑定作为结果。在导入过程中，我们使用metadata.name作为对象名称的关键，所以我们现在可以将这个字段设置为ID。

模板被应用于（与）它们所定义的结构中的所有条目统一，所以我们需要剥离面包分配器定义中的特定字段，概括它们，或者删除它们。

Kubernetes元数据中定义的一个标签似乎总是被设置为父目录名称。我们通过定义组件：字符串来强制执行，这意味着名称为组件的字段必须被设置为某个字符串值，然后在后面定义。任何未指定的字段在转换为例如JSON时都会导致错误。因此，只有当这个标签被定义后，部署或服务才会有效。

让我们比较一下合并我们的新模板和原始快照的结果。

```shell script
$ cue eval ./... -c > snapshot2
--- ./mon/alertmanager
service.alertmanager.metadata.labels.component: incomplete value (string):
    ./kube.cue:11:24
service.alertmanager.spec.selector.component: incomplete value (string):
    ./kube.cue:11:24
deployment.alertmanager.spec.template.metadata.labels.component: incomplete value (string):
    ./kube.cue:36:28
service."node-exporter".metadata.labels.component: incomplete value (string):
    ./kube.cue:11:24
...
```
警报管理器没有指定 `component` 的标签。这展示了如何用约束条件来捕捉你的配置中的不一致之处。

由于很少有对象不指定这个标签，我们将修改配置，使之包括所有地方。我们通过在每个目录中设置一个新定义的顶层字段来做这件事，并修改我们的主模板文件来使用它。

```shell script
# set the component label to our new top-level field
$ sed -i.bak 's/component:.*string/component: #Component/' kube.cue && rm kube.cue.bak

# add the new top-level field to our previous template definitions
$ cat <<EOF >> kube.cue

#Component: string
EOF

# add a file with the component label to each directory
$ ls -d */ | sed 's/.$//' | xargs -I DIR sh -c 'cd DIR; echo "package kube

#Component: \"DIR\"
" > kube.cue; cd ..'

# format the files
$ cue fmt kube.cue */kube.cue
```

让我们再试一次，看看它是否被修复。

```shell script
$ cue eval -c ./... > snapshot2
$ diff snapshot snapshot2
...
```
除了有更一致的标签和一些重新排序外，没有任何变化。我们很高兴，并把这个结果作为新的基线保存起来。

```shell script
$ cp snapshot2 snapshot
```

## 未完待续
> 后面还有一部分内容没有增加出来，请期待 。

## 参考
- https://github.com/cuelang/cue/tree/master/doc/tutorial/kubernetes

