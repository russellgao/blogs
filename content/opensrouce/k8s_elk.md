+++
title = "ELK stack on kubernetes"
description = "在k8s 中运行EKL"
date = "2020-01-04"
aliases = ["elk on k8s"]
author = "russellgao"
draft = false
tags = [
    "kubernetes",
    "ELK"
,]
+++

## 作用
如何在Kubernetes环境中运行ELK Stack

## 项目地址
[https://github.com/russellgao/k8s_elk](https://github.com/russellgao/k8s_elk)

## 用法

- `manifests` Can run in production environment
- `experimental` In the experimental stage

使用之前需要修改各个yaml文件的Storage，Service相关的参数，根据实际情况选择合适的介质，修改完之后执行`kubectl -f manifests` 即可。

详细信息参考 [github](https://github.com/russellgao/k8s_elk) 

## 支持的组件
- es
- logstash
- kibana
- kafka
- zookeeper

## More
- [https://mp.weixin.qq.com/s/93_Jf8P69Q0nkw1Ip7MsFQ](https://mp.weixin.qq.com/s/93_Jf8P69Q0nkw1Ip7MsFQ)
