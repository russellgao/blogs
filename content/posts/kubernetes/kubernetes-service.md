+++
title = "kubernetes Service 原理剖析"
description = "kubernetes Service 原理剖析"
date = "2021-01-21"
aliases = ["kubernetes Service 原理剖析"]
author = "russellgao"
draft = true
tags = [
    "kubernetes",
    "service" ,
    "kube-proxy"
]

categories = [
    "kubernetes"
]

+++

## 导读
> 本篇文章主要带大家看看从集群内部或者外部发起一个请求如何流转到一个具体的后端服务(POD)。

## 参考
- https://draveness.me/kubernetes-service/
- https://xigang.github.io/2019/07/21/kubernetes-service/
