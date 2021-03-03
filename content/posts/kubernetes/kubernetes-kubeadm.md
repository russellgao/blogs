+++
title = "使用 kubeadm 部署集群"
description = "使用 kubeadm 部署集群"
date = "2021-02-21"
aliases = ["使用 kubeadm 部署集群"]
author = "russellgao"
draft = true
tags = [
    "kubernetes",
    "kubeadm" ,
    "集群部署"
]
+++

## kubeadm 前置检查
安装 `kubeadm` 之前需要进行如下检查:

* 操作系统
    - Ubuntu 16.04+
    - Debian 9+
    - CentOS 7+
    - Red Hat Enterprise Linux (RHEL) 7+
    - Fedora 25+
    - HypriotOS v1.0.1+
    - Flatcar Container Linux (tested with 2512.3.0)
* 内存: 最少2G
* CPU: 最少2核
* 集群中的网络必须连通
* 唯一的 hostname、mac 地址、product_uuid
* 确定的端口
* 关闭 swap 

### MAC 地址和 product_uuid 的唯一性 
- mac 地址: `ip link 或 ifconfig -a`
可以使用 sudo cat /sys/class/dmi/id/product_uuid 命令对 product_uuid 校验

### 检查所需端口
控制平面节点

协议 | 方向 | 端口范围 | 作用 | 使用者
:-:|:-:|:-:|:-:|:-:
TCP | 入站 | 6443 | Kubernetes API 服务器 | 所有组件
TCP | 入站 | 2379-2380 | etcd 服务器客户端 API | kube-apiserver, etcd
TCP | 入站 | 10250 | Kubelet API | kubelet 自身、控制平面组件
TCP | 入站 | 10251 | kube-scheduler | kube-scheduler 自身
TCP | 入站 | 10252 | kube-controller-manager | kube-controller-manager 自身

工作节点

协议 | 方向 | 端口范围 | 作用 | 使用者
:-:|:-:|:-:|:-:|:-:
TCP | 入站 | 10250 | Kubelet API | kubelet 自身、控制平面组件
TCP | 入站 | 30000-32767 | NodePort 服务† | 所有组件


## 参考
- https://github.com/kubernetes/kubeadm
- https://kubernetes.io/zh/docs/setup/production-environment/tools/kubeadm/install-kubeadm/