+++
title = "harbor gc 时遇到的坑"
description = "harbor gc 时遇到的坑"
date = "2020-11-29"
aliases = ["harbor gc 时遇到的坑"]
author = "russellgao"
draft = false
tags = [
    "云原生",
    "harbor"
]
categories = [
    "other"
]

+++

## 导读
> Harbor 是为企业用户设计的容器镜像仓库开源项目，包括了权限管理(RBAC)、LDAP、审计、安全漏洞扫描、镜像验真、管理界面、自我注册、HA 等企业必需的功能，同时针对中国用户的特点，设计镜像复制和中文支持等功能。
> 
> 在使用的过程会有 GC 的需求，可以想象下这几种场景:
>
> - 在 CI 的过程，同一个版本（SNAPSHOT/latest）编译很多次，只有最后一次产生的才有 tag ，那么之前的产生 blob 去哪了，或者还有用吗 ？
> - 镜像的生命周期已经结束，需要从仓库中删除，应该怎么操作？要知道在 Harbor 界面上删除只是标记删除，并不会释放存储空间。
> 
> Harbor / Docker 官方已经提供比较完善的 GC 方案，可以解决 80% 的问题，但是 GC 的过程中还可能出现一些奇怪的现象，本文主要记录在 Harbor GC
>过程中踩过的坑。

## GC原理
用一个官方例子说明:

```
A -----> a <----- B
    \--> b     |
         c <--/
```

假设镜像 A 引用了层a,b ，镜像 B 引用了层 a,c ，在这个阶段，是不需要做 GC 的，接下来把 B 给删掉，如下: 

```
A -----> a     B
    \--> b
         c
```

在这个阶段层 c 是不属于任何镜像了，适合去 GC ，GC 完之后效果如下：

```
A -----> a
    \--> b
```

看着还是挺简单，很容易理解的对吧，但是当镜像数为 `10,000+` 以上，存储在 TB 级别以上时，事情可能又不那么简单了。

## Harbor 存储的目录结构
Harbor 底层还是 Docker Registry，所以它们的存储结构是一样的，可以先看看它们在磁盘上存储结构:

```
# tree docker/registry/v2/
docker/registry/v2
    │   │   ├── blogs
    │   │   │   └── sha256
    │   │   │       └── 00
    │   │   │           └── 000098c48e5c8502460fd4427fe19d9def6c3d245b46e4d3dd86a00c79ca3111
    │   │   │               └── data
    │   │   │           └── 000098c48e5c8502460fd4427fe19d9def6c3d245b46e4d3dd86a00c79ca3112
    │   │   │               └── data
    │   │   │       └── 01
    │   │   │           └── 010098c48e5c8502460fd4427fe19d9def6c3d245b46e4d3dd86a00c79ca3111
    │   │   │               └── data
    │   │   │           └── 010098c48e5c8502460fd4427fe19d9def6c3d245b46e4d3dd86a00c79ca3112
    │   │   │               └── data
    │   │   ├── repositories
    │   │   │   └── golang
    │   │   │       └── golang-centos
    │   │   │           └── _layers
    │   │   │               └── sha256
    │   │   │           └── _manifests
    │   │   │               └── revisions
    │   │   │                   └── sha256
    │   │   │               └── tags
    │   │   │                   └── 1.14
    │   │   │                   └── 1.15
```
可以看到存储结构主要分为两个部分 `blogs` 和 `repositories` ，作用如下 :

- blogs 是镜像数据的真正存储。
- repositories 是镜像数据的引用，换言之存储的是blogs的索引。每个镜像都会声明它引用 blogs 中的哪些层。

## GC过程
有了上面的铺垫，GC 的过程应该很容易理解了。Harbor GC 采用的两阶段标记清除，先遍历 repositories 下的镜像，并且对引用到blogs 
进行标记，遍历完成之后把没有标记的 blogs 进行删除。

看似完美的方案，在实际操作过程中却还有些坑，下面说说遇到的坑以及如何解决方案。

## 遇到的坑
### docker pull 失败
docker pull 的时候报错如下（unknown blob）：
```
docker pull russellgao/toolkit
...
daa258f4f8c0: Already exists 
0c9e9bbad61e: Already exists 
fa786f5d7be0: Already exists 
ebc05f08dcb7: Downloading 
f919a7128c9a: Downloading 
34dfbfa16f77: Download complete 
65588873bd66: Download complete 
fc1b74edeacc: Download complete 
099607f21531: Download complete 
09432885197f: Download complete 
259a4564bedf: Download complete 
ce223372b98e: Download complete 
...
unknown blob
```

这种情况主要的原因是在 `repositories` 中存在对 `blob` 的引用，但是 `blog` 中却不存在，造成这种可能的原因有：

- GC 的时候错误的删除了 blobs （大概率如此）
- blob 所在的磁盘损坏 （概率较小）
- blob 被人为删除（概率较小）

**请注意：这种情况重新推送镜像是没有用的，因为在推送的时候，harbor 认为缺失的层是存在的，因为 repositories中存在，只有在下载时才会发现。**

解决的方法:

- 通过docker build 编译镜像时增加 `--no-cache` 参数，生成一个全新的镜像推送到镜像仓库，方法可能会解决问题，但也有可能解决不了，可以
想象这么一个场景，缺失的层为基础镜像，如果基础镜像缺少层，那么这种方法就失效了。
- 可以在部署一个镜像仓库（一般都会最少有两个仓库做互备），把编译好的镜像推送到新的仓库，然后根据缺少的 blob id 在新的仓库中找到对应的 
blob 数据，然后把缺少的 copy 到之前仓库，问题即可得到解决。如：

缺少 `ebc05f08dcb7` 这一层，在新的仓库的中可以找到如下目录:

```
docker/registry/v2/blobs/sha256/eb/ 
```

通过 `ebc05f08dcb7` 前缀找到具体的 blob 目录，然后把找到的这个目录 copy 到对应的仓库日录，问题即可得到解决。

## 总结
这篇文章主要介绍了 harbor gc 的基本原理，然后记录在 GC 的过程中踩的坑，后续有其他坑持续补充。

## 参考
- https://github.com/docker/docker.github.io/blob/master/registry/garbage-collection.md

