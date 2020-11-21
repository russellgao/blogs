+++
title = "kubectl 常用命令"
description = "kubectl 常用命令指南"
date = "2020-11-20"
aliases = ["kubectl 常用命令指南"]
author = "russellgao"
draft = false
tags = [
    "kubernetes",
    "kubectl"
]
+++

## 导读
> kubectl 应该是每个接触 kubernetes 的人都会接触的一个组件，它带给我们强大的命令行体验，本篇文章就是介绍 kubectl 
中的一些常用命令，在结合一些具体的使用场景说说如何利用 kubectl 实现。好记性不如烂笔头，在这里尽可能全的罗列，方便后续
用的时候查找。如果能帮到您就收藏起来吧(:smile:)。
>
>本次实验环境是 kubernetes-1.16.9，本篇文档的写作思路是按照平时
的使用场景进行写作，不会详细介绍 kubectl 的命令，kubectl 详细的帮助文档参考 `kubectl --help ` or `kubectl command --help` 。

## kubectl 支持的命令
```shell script
kubectl --help
kubectl controls the Kubernetes cluster manager.

 Find more information at: https://kubernetes.io/docs/reference/kubectl/overview/

Basic Commands (Beginner):
  create         Create a resource from a file or from stdin.
  expose         使用 replication controller, service, deployment 或者 pod 并暴露它作为一个 新的
Kubernetes Service
  run            在集群中运行一个指定的镜像
  set            为 objects 设置一个指定的特征

Basic Commands (Intermediate):
  explain        查看资源的文档
  get            显示一个或更多 resources
  edit           在服务器上编辑一个资源
  delete         Delete resources by filenames, stdin, resources and names, or by resources and label selector

Deploy Commands:
  rollout        Manage the rollout of a resource
  scale          为 Deployment, ReplicaSet, Replication Controller 或者 Job 设置一个新的副本数量
  autoscale      自动调整一个 Deployment, ReplicaSet, 或者 ReplicationController 的副本数量

Cluster Management Commands:
  certificate    修改 certificate 资源.
  cluster-info   显示集群信息
  top            Display Resource (CPU/Memory/Storage) usage.
  cordon         标记 node 为 unschedulable
  uncordon       标记 node 为 schedulable
  drain          Drain node in preparation for maintenance
  taint          更新一个或者多个 node 上的 taints

Troubleshooting and Debugging Commands:
  describe       显示一个指定 resource 或者 group 的 resources 详情
  logs           输出容器在 pod 中的日志
  attach         Attach 到一个运行中的 container
  exec           在一个 container 中执行一个命令
  port-forward   Forward one or more local ports to a pod
  proxy          运行一个 proxy 到 Kubernetes API server
  cp             复制 files 和 directories 到 containers 和从容器中复制 files 和 directories.
  auth           Inspect authorization

Advanced Commands:
  diff           Diff live version against would-be applied version
  apply          通过文件名或标准输入流(stdin)对资源进行配置
  patch          使用 strategic merge patch 更新一个资源的 field(s)
  replace        通过 filename 或者 stdin替换一个资源
  wait           Experimental: Wait for a specific condition on one or many resources.
  convert        在不同的 API versions 转换配置文件
  kustomize      Build a kustomization target from a directory or a remote url.

Settings Commands:
  label          更新在这个资源上的 labels
  annotate       更新一个资源的注解
  completion     Output shell completion code for the specified shell (bash or zsh)

Other Commands:
  api-resources  Print the supported API resources on the server
  api-versions   Print the supported API versions on the server, in the form of "group/version"
  config         修改 kubeconfig 文件
  plugin         Provides utilities for interacting with plugins.
  version        输出 client 和 server 的版本信息

Usage:
  kubectl [flags] [options]

Use "kubectl <command> --help" for more information about a given command.
Use "kubectl options" for a list of global command-line options (applies to all commands).
```

从上面的帮助文档可以看出， kubectl 基本格式为 `kubectl verb resource options` , kubectl 后跟谓语动词，
再跟要操作的资源，可以加 options ，如：

要看 monitoring namespace 下面有哪些pod :
```shell script
 kubectl -n monitoring get po 
```

## pod
pod 场景下，可能会有如下需求: 
### 查看某个 namespace 下，所有的pod
```shell script
# 先查看有哪些namespace
kubectl get namespace
# 查看 pod
kubectl -n $namespace get po 
# 或者
kubectl get po -n $namespace
```
上面查看两种写法在达到的效果上是一样的，但是有一个细节可以注意一下，如果环境有命令自动补全的话，资源对象又比较多
的情况下，第一种写法将会有极大的优势，可以思考这么个一个场景，如：要查看 monitoring namespace 下的某个pod 详情,
就可以通过: `kubectl -n monitoring get po ` 加 tab 健，列出这个namespace 下的所有 pod 供筛选。

centos 下命令自动补全需要安装 `bash-completion` ，方法为 `yum install -y bash-completion`

如果不加 `-n $namespace` ，则默认是 default namespace 

### 查看所有namespace 的pod
```shell script
kubectl get po --all-namespaces 
# or
kubectl get po -A
```

### 查看某个具体的 pod 信息 ，以 wide、json、yaml 的格式输出
```shell script
kubectl -n $namespace get po xxx -o wide/json/yaml
# 如 查看 monitoring 下的 prometheus-0 pod 信息，并以yaml 形式输出。
kubectl -n monitoring get po prometheus-0 -o yaml
```

### 查看某个 pod 的某个字段信息
如果我们只想知道 pod 的 hostIP 或者其他的 一些字段， 可以通过 `-o jsonpath` or `-o template` or `-o go-template`

- 其中template 语法遵循 golang template
- 需要对 pod 的对象模型有一定的了解，如果不了解，可以 `-o yaml` or `-o json` 直接查看。

查看 hostIP 的方法如下: 
```shell script
# -o jsonpath
kubectl -n monitoring get po prometheus-k8s-0 -o jsonpath="{.status.hostIP}" 
# -o template
kubectl -n monitoring get po prometheus-k8s-0 -o template --template="{{.status.hostIP}}"
# -o go-template
kubectl -n monitoring get po prometheus-k8s-0 -o go-template="{{.status.hostIP}}" 
```

如果需要查看其他的字段照猫画虎即可。

### 通过标签选择查看 pod
通过 `-l key1=value1,key2=value2` 进行选择，如
```shell script
kubectl -n monitoring get po -l app=prometheus
kubectl -n monitoring get po -l app=prometheus,prometheus=k8s
```

### 查看某个node 上部署的所有 pod
```shell script
#先获取集群内所有的node
kubectl get node -o wide
# 假设其中一个 node 的名称为 node-0001
kubectl  get po -A  -o wide | grep node-0001
```

通过 `kubectl  get po -A  -o wide | grep` 可以做很多事情，具体可以根据情况而定，比如查看所有状态异常的 pod （非 Running）
```shell script
kubectl  get po -A  -o wide | grep -v Running 
```

### 查看 pod 的详细信息
```shell script
kubectl -n monitoring describe po prometheus-k8s-0 
```
这个命令在查看 pod 的基本信息和问题定位时特别有用，当 pod 异常，可以查看 Events 或许就能发现问题所在。

### 查看 pod log
```shell script
kubectl -n $namespace  logs -f $podName $containerName
# 其中 $namespace，$podName，$containerName 替换成真实值即可，当 pod 中只有一个 容器时可省略 $containerName，如：
kubectl -n monitoring  logs -f prometheus-k8s-0 prometheus
```

### 进入容器
```shell script
kubectl -n $namespace exec -it $podName -c $containerName sh
# 其中 $namespace，$podName，$containerName 替换成真实值即可，当 pod 中只有一个 容器时可省略 -c $containerName，如：
kubectl -n monitoring exec -it prometheus-k8s-0 -c prometheus sh
```

### 查看 pod 的资源使用情况
```shell script
kubectl -n $namespace top pod
# 其中 $namespace 替换成真实值即可，如：
kubectl -n monitoring top pod
```

### 删除 pod
```shell script
kubectl -n $namespace delete po $podName 
kubectl -n monitoring delete po prometheus-k8s-0
# 在某些异常情况下删除 pod 会卡住，删不掉，需要强制才能删除 ，强制删除需要增加 --grace-period=0 --force ，
kubectl -n monitoring delete po prometheus-k8s-0 --grace-period=0 --force 
```

>原理如下， 默认执行 `delete po` 时，kubectl 会增加--grace-period=30 参数，表示预留30秒的时间给 pod 处理当前的请求，
但同时也不接收新的请求了，以一种相对优雅的方式停止容器，注意这个参数在创建 pod 时可以指定，默认是30秒。强制删除时需要把--grace-period
设置为0，表示不等待马上删除，否则强制删除就会失效。


### pod 标签管理
pod 的大多数的情况都会 `deployment` or `statefulset` 来管理，所以标签也会通过它们管理，实际情况下很少会通过
kubectl 对 pod label 做增删改，如有需要可参考 下面 node 的用法，只需要把资源对象换成 pod 即可。
## node
在 pod 一节 已经了解了 `kubectl get` ,`kubectl describe` , 等相关的用法，node 的操作很 pod 类似，只是后面接的资源对象不同。

### 查看有哪些node已经基本信息
```shell script
kubectl get node -o wide
```

### 查看 node 上的详细情况

```shell script
# 查看所有 node 的详细信息
kubectl describe node 
# 也可以查看某个 node 的信息
kubectl describe node xxx ...
```

这个命令在定位 node 的问题很有用，会输出如下信息: 

- Labels
- Annotations
- Non-terminated Pods (正在运行的 pod)
- Allocated resources (已经分配的资源)
- ...

### 查看 node 的资源使用情况
```shell script
kubectl top node
```

### node 的标签管理
1. 增加标签
```shell script
kubectl label node $nodename  key1=value1 key2=value2
# 如
kubectl label node node-0001  a1=bbb a2=ccc
```
2. 更新标签
```shell script
# 在 增加标签的基础 加 --overwrite 参数
kubectl label node node-0001  a1=bbb --overwrite
# 当标签不存在也可以 加 --overwrite 参数
kubectl label node node-0001  a10=bbb --overwrite
```
3.
```shell script
kubectl label node $nodename key1- key2-
kubectl label node node-0001 a10- a3-
```

## 参考
- https://kubernetes.io/zh/docs/reference/kubectl/cheatsheet/