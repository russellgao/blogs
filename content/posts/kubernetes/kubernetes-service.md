+++
title = "kubernetes Service 原理剖析"
description = "kubernetes Service 原理剖析"
date = "2021-01-21"
aliases = ["kubernetes Service 原理剖析"]
author = "russellgao"
draft = false
tags = [
    "kubernetes",
    "service" ,
    "kube-proxy"
]
+++

## 导读
> 本篇文章主要带大家看看从集群内部或者外部发起一个请求如何流转到一个具体的后端服务(POD)。

