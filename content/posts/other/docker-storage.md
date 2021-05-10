+++
title = "docker 原理之存储驱动"
description = "docker 原理之存储驱动"
date = "2020-12-05"
author = "russellgao"
draft = false
tags = [
    "docker"
]
categories = [
    "docker"
]

+++

## 导读
> 提起 docker 大家应该耳熟能详，如使用 docker 所带来的持续集成、版本控制、可移植性、隔离性、安全性等诸多好处。docker
>的使用也很方便，但是其内部原理是什么样的？都有哪些组件？之间是如何相互协作的呢？这是 docker 系列文章，每篇讲解一个知识点，可以更好的消化。
>这篇谈谈 docker 的存储驱动。受限作者水平，如有不对之处，欢迎批评之处。

## 什么是 docker 存储驱动
如果执行过 `docker info` 命令，那么肯定看到过这些信息:
```shell script
...
Server:
 Server Version: 19.03.13
 Storage Driver: overlay2
  Backing Filesystem: extfs
  Supports d_type: true
  Native Overlay Diff: true
...
```
请注意 **Storage Driver: overlay2** ，看到这些可能会有几个疑问: 什么是 `Storage Driver` ？除了 `overlay2` 还有其他的吗？原理是什么？

我们知道 docker 的特别是分层的，层叠镜像是 docker 最具特色的特性之一。想象这么一个场景，docker 启动容器是依赖于镜像的，假设要一个 `JDK` 的镜像
要启动 10 个，这个镜像本身500M，那么 10 个这些容器是共享这一个镜像呢还是把每个镜像都复制一份呢，如果是共享模式，那么如果一个容器修改了镜像中的内容
岂不是会影响其他容器？如果是各自复制一份，那岂不是会造成存储空间的浪费?

>存储驱动(Storage Driver) 就是解决这个问题，到现在也有好几种解决方案。总的解决思路就是**镜像是只读的，启动容器时就是镜像上面叠加一个读写层。**

在了解具体的存储驱动之前先铺垫几个知识点：

### 写时复制（CoW）
所有驱动都用到的技术——写时复制（CoW）。CoW就是copy-on-write，表示只在需要写时才去复制，这个是针对已有文件的修改场景。比如基于一个image启动多个Container，如果为每个Container都去分配一个image一样的文件系统，那么将会占用大量的磁盘空间。而CoW技术可以让所有的容器共享image的文件系统，所有数据都从image中读取，只有当要对文件进行写操作时，才从image里把要写的文件复制到自己的文件系统进行修改。所以无论有多少个容器共享同一个image，所做的写操作都是对从image中复制到自己的文件系统中的复本上进行，并不会修改image的源文件，且多个容器操作同一个文件，会在每个容器的文件系统里生成一个复本，每个容器修改的都是自己的复本，相互隔离，相互不影响。使用CoW可以有效的提高磁盘的利用率。

### 用时分配（allocate-on-demand）
而写时分配是用在原本没有这个文件的场景，只有在要新写入一个文件时才分配空间，这样可以提高存储资源的利用率。比如启动一个容器，并不会为这个容器预分配一些磁盘空间，而是当有新文件写入时，才按需分配新空间。

### 联合文件系统
联合文件系统（UnionFS）是一种分层、轻量级并且高性能的文件系统，它支持对文件系统的修改作为一次提交来一层层的叠加，同时可以将不同目录挂载到同一个虚拟文件系统下。

## 现有的存储驱动及其特点
### AUFS
AUFS（AnotherUnionFS）是一种Union FS，是文件级的存储驱动。AUFS能透明覆盖一或多个现有文件系统的层状文件系统，把多层合并成文件系统的单层表示。简单来说就是支持将不同目录挂载到同一个虚拟文件系统下的文件系统。这种文件系统可以一层一层地叠加修改文件。无论底下有多少层都是只读的，只有最上层的文件系统是可写的。当需要修改一个文件时，AUFS创建该文件的一个副本，使用CoW将文件从只读层复制到可写层进行修改，结果也保存在可写层。在Docker中，底下的只读层就是image，可写层就是Container。结构如下图所示：

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-storage-aufs.jpg)

### Overlay
Overlay是Linux内核3.18后支持的，也是一种Union FS，和AUFS的多层不同的是Overlay只有两层：一个upper文件系统和一个lower文件系统，分别代表Docker的镜像层和容器层。当需要修改一个文件时，使用CoW将文件从只读的lower复制到可写的upper进行修改，结果也保存在upper层。在Docker中，底下的只读层就是image，可写层就是Container。结构如下图所示：

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-storage-overlay.jpg)

OverlayFS有两种存储驱动，它们使用了相同的OverlayFS技术，但却有着不同的实现，在磁盘使用上也并不互相兼容。因为不兼容，两者之间的切换必须重新创建所有的镜像。overlay驱动是最原始的OverlayFS实现，并且，在Docker1.11之前是仅有的OverlayFS驱动选择。overlay驱动在inode消耗方面有着较明显的限制，并且会损耗一定的性能。overlay2驱动解决了这种限制，不过只能在Linux kernel 4.0以上使用它。

>目前 `Overlay2` 是默认的存储驱动

### Device mapper
Device mapper是Linux内核2.6.9后支持的，提供的一种从逻辑设备到物理设备的映射框架机制，在该机制下，用户可以很方便的根据自己的需要制定实现存储资源的管理策略。前面讲的AUFS和OverlayFS都是文件级存储，而Device mapper是块级存储，所有的操作都是直接对块进行操作，而不是文件。Device mapper驱动会先在块设备上创建一个资源池，然后在资源池上创建一个带有文件系统的基本设备，所有镜像都是这个基本设备的快照，而容器则是镜像的快照。所以在容器里看到文件系统是资源池上基本设备的文件系统的快照，并不有为容器分配空间。当要写入一个新文件时，在容器的镜像内为其分配新的块并写入数据，这个叫用时分配。当要修改已有文件时，再使用CoW为容器快照分配块空间，将要修改的数据复制到在容器快照中新的块里再进行修改。Device mapper 驱动默认会创建一个100G的文件包含镜像和容器。每一个容器被限制在10G大小的卷内，可以自己配置调整。结构如下图所示：

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-storage-devicemapper.jpg)

### Btrfs
Btrfs被称为下一代写时复制文件系统，并入Linux内核，也是文件级级存储，但可以像Device mapper一直接操作底层设备。Btrfs把文件系统的一部分配置为一个完整的子文件系统，称之为subvolume 。那么采用 subvolume，一个大的文件系统可以被划分为多个子文件系统，这些子文件系统共享底层的设备空间，在需要磁盘空间时便从底层设备中分配，类似应用程序调用 malloc()分配内存一样。为了灵活利用设备空间，Btrfs 将磁盘空间划分为多个chunk 。每个chunk可以使用不同的磁盘空间分配策略。比如某些chunk只存放metadata，某些chunk只存放数据。这种模型有很多优点，比如Btrfs支持动态添加设备。用户在系统中增加新的磁盘之后，可以使用Btrfs的命令将该设备添加到文件系统中。Btrfs把一个大的文件系统当成一个资源池，配置成多个完整的子文件系统，还可以往资源池里加新的子文件系统，而基础镜像则是子文件系统的快照，每个子镜像和容器都有自己的快照，这些快照则都是subvolume的快照。

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-storage-btrfs.jpg)

当写入一个新文件时，为在容器的快照里为其分配一个新的数据块，文件写在这个空间里，这个叫用时分配。而当要修改已有文件时，使用CoW复制分配一个新的原始数据和快照，在这个新分配的空间变更数据，变结束再更新相关的数据结构指向新子文件系统和快照，原来的原始数据和快照没有指针指向，被覆盖。

### ZFS
ZFS 文件系统是一个革命性的全新的文件系统，它从根本上改变了文件系统的管理方式，ZFS 完全抛弃了“卷管理”，不再创建虚拟的卷，而是把所有设备集中到一个存储池中来进行管理，用“存储池”的概念来管理物理存储空间。过去，文件系统都是构建在物理设备之上的。为了管理这些物理设备，并为数据提供冗余，“卷管理”的概念提供了一个单设备的映像。而ZFS创建在虚拟的，被称为“zpools”的存储池之上。每个存储池由若干虚拟设备（virtual devices，vdevs）组成。这些虚拟设备可以是原始磁盘，也可能是一个RAID1镜像设备，或是非标准RAID等级的多磁盘组。于是zpool上的文件系统可以使用这些虚拟设备的总存储容量。

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-storage-zfs-1.jpg)

下面看一下在Docker里ZFS的使用。首先从zpool里分配一个ZFS文件系统给镜像的基础层，而其他镜像层则是这个ZFS文件系统快照的克隆，快照是只读的，而克隆是可写的，当容器启动时则在镜像的最顶层生成一个可写层。如下图所示：

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-storage-zfs-2.jpg)

当要写一个新文件时，使用按需分配，一个新的数据快从zpool里生成，新的数据写入这个块，而这个新空间存于容器（ZFS的克隆）里。
当要修改一个已存在的文件时，使用写时复制，分配一个新空间并把原始数据复制到新空间完成修改。

## 存储驱动对比
存储驱动 |	特点 | 	优点 |	缺点	| 适用场景
:-: | :-: | :-: | :-: | :-: 
AUFS	|联合文件系统、未并入内核主线、文件级存储|	作为docker的第一个存储驱动，已经有很长的历史，比较稳定，且在大量的生产中实践过，有较强的社区支持	|有多层，在做写时复制操作时，如果文件比较大且存在比较低的层，可能会慢一些	|大并发但少IO的场景
overlayFS|	联合文件系统、并入内核主线、文件级存储	|只有两层	|不管修改的内容大小都会复制整个文件，对大文件进行修改显示要比小文件消耗更多的时间	|大并发但少IO的场景
Devicemapper	|并入内核主线、块级存储	|块级无论是大文件还是小文件都只复制需要修改的块，并不是整个文件	|不支持共享存储，当有多个容器读同一个文件时，需要生成多个复本，在很多容器启停的情况下可能会导致磁盘溢出|	适合io密集的场景
Btrfs|	并入linux内核、文件级存储	|可以像devicemapper一样直接操作底层设备，支持动态添加设备	|不支持共享存储，当有多个容器读同一个文件时，需要生成多个复本	|不适合在高密度容器的paas平台上使用
ZFS	|把所有设备集中到一个存储池中来进行管理	|支持多个容器共享一个缓存块，适合内存大的环境	|COW使用碎片化问题更加严重，文件在硬盘上的物理地址会变的不再连续，顺序读会变的性能比较差|	适合paas和高密度的场景

## 设置存储驱动
docker 安装时会有自己的默认存储驱动，在新版本的 docker 中，默认是 `overlay2`，centos，mac 是这样的，其他的没有验证过。

如果要更改存储驱动，方法为:
```shell script
dockerd --storage-driver=aufs
```
设置完成后可通过 `docker info` 进行验证。

## 参考
- http://dockone.io/article/1513
- https://gitbook.cn/gitchat/column/5d68b823de93ed72d6eca1bc/topic/5db26784bae3b42c1fa84d5f
