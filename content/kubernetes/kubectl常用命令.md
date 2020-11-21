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
kubectl -n xxx get po 
# 或者
kubectl get po -n xxx
```
上面查看两种写法在达到的效果上是一样的，但是有一个细节可以注意一下，如果环境有命令自动补全的话，资源对象又比较多
的情况下，第一种写法将会有极大的优势，可以思考这么个一个场景，如：要查看 monitoring namespace 下的某个pod 详情,
就可以通过: `kubectl -n monitoring get po ` 加 tab 健，列出这个namespace 下的所有 pod 供筛选。

centos 下命令自动补全需要安装 `bash-completion` ，方法为 `yum install -y bash-completion`

如果不加 `-n xxx` ，则默认是 default namespace 

### 查看所有namespace 的pod
```shell script
kubectl get po --all-namespaces 
# or
kubectl get po -A
```

### 查看某个具体的 pod 信息 ，以 wide、json、yaml 的格式输出
```shell script
kubectl -n xxx get po xxx -o wide/json/yaml
# 如 查看 monitoring 下的 prometheus-0 pod 信息，并以yaml 形式输出。
kubectl -n monitoring get po prometheus-0 -o yaml
```

### 查看某个 pod 的某个字段信息


### 通过标签选择查看 pod

### 查看某个node 上部署的所有 pod

## 参考
- https://kubernetes.io/zh/docs/reference/kubectl/cheatsheet/