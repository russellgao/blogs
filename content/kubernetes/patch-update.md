+++
title = "kubernetes 中patch与update比较"
description = "kubernetes 中patch与update比较"
date = "2020-11-21"
aliases = ["kubernetes 中patch与update比较"]
author = "russellgao"
draft = false
tags = [
    "kubernetes",
    "api",
    "patch",
    "update"
]
+++

## 导读
> 不知道你有没有想过一个问题：对于一个 K8s 资源对象比如 Deployment，我们尝试在修改其中 image 镜像时，如果有其他人同时也在对这个 Deployment 做修改，会发生什么？
>
>当然，这里还可以引申出两个问题：
>
>- 如果双方修改的是同一个字段，比如 image 字段，结果会怎样？
>- 如果双方修改的是不同字段，比如一个修改 image，另一个修改 replicas，又会怎么样？
>
> 其实，对一个 Kubernetes 资源对象做“更新”操作，简单来说就是通知 kube-apiserver 组件我们希望如何修改这个对象。而 K8s 为这类需求定义了两种“通知”方式，分别是 update 和 patch。在 update 请求中，我们需要将整个修改后的对象提交给 K8s；而对于 patch 请求，我们只需要将对象中某些字段的修改提交给 K8s。

## Update 机制
Kubernetes 中的所有资源对象，都有一个全局唯一的版本号（metadata.resourceVersion）。每个资源对象从创建开始就会有一个版本号，而后每次被修改（不管是 update 还是 patch 修改），版本号都会发生变化。

[官方文档](https://kubernetes.io/docs/reference/using-api/api-concepts/#resource-versions) 告诉我们，这个版本号是一个 K8s 的内部机制，用户不应该假设它是一个数字或者通过比较两个版本号大小来确定资源对象的新旧，唯一能做的就是通过比较版本号相等来确定对象是否是同一个版本（即是否发生了变化）。而 resourceVersion 一个重要的用处，就是来做 update 请求的版本控制。

K8s 要求用户 update 请求中提交的对象必须带有 resourceVersion，也就是说我们提交 update 的数据必须先来源于 K8s 中已经存在的对象。因此，一次完整的 update 操作流程是：


- 首先，从 K8s 中拿到一个已经存在的对象（可以选择直接从 K8s 中查询；如果在客户端做了 list watch，推荐从本地 informer 中获取）；
- 然后，基于这个取出来的对象做一些修改，比如将 Deployment 中的 replicas 做增减，或是将 image 字段修改为一个新版本的镜像；
- 最后，将修改后的对象通过 update 请求提交给 K8s；
- 此时，kube-apiserver 会校验用户 update 请求提交对象中的 resourceVersion 一定要和当前 K8s 中这个对象最新的 resourceVersion 一致，才能接受本次 update。否则，K8s 会拒绝请求，并告诉用户发生了版本冲突（Conflict）。

![](https://gitee.com/russellgao/blogs-image/raw/master/images/k8s/kubernetes_update-83783283732.png)

上图展示了多个用户同时 update 某一个资源对象时会发生的事情。而如果如果发生了 Conflict 冲突，对于 User A 而言应该做的就是做一次重试，再次获取到最新版本的对象，修改后重新提交 update。

因此，我们上面的两个问题也都得到了解答：

- 用户修改 YAML 后提交 update 失败，是因为 YAML 文件中没有包含 resourceVersion 字段。对于 update 请求而言，应该取出当前 K8s 中的对象做修改后提交；
- 如果两个用户同时对一个资源对象做 update，不管操作的是对象中同一个字段还是不同字段，都存在版本控制的机制确保两个用户的 update 请求不会发生覆盖。

## Patch 机制
相比于 update 的版本控制，K8s 的 patch 机制则显得更加简单。

当用户对某个资源对象提交一个 patch 请求时，kube-apiserver 不会考虑版本问题，而是“无脑”地接受用户的请求（只要请求发送的 patch 内容合法），也就是将 patch 打到对象上、同时更新版本号。

不过，patch 的复杂点在于，目前 K8s 提供了 4 种 patch 策略：json patch、merge patch、strategic merge patch、apply patch（从 K8s 1.14 支持 server-side apply 开始）。通过 kubectl patch -h 命令我们也可以看到这个策略选项（默认采用 strategic）：

```shell script
$ kubectl patch -h
# ...
  --type='strategic': The type of patch being provided; one of [json merge strategic]
```

篇幅限制这里暂不对每个策略做详细的介绍了，我们就以一个简单的例子来看一下它们的差异性。如果针对一个已有的 Deployment 对象，假设 template 中已经有了一个名为 app 的容器：

- 如果要在其中新增一个 nginx 容器，如何 patch 更新？
- 如果要修改 app 容器的镜像，如何 patch 更新？

### json patch
新增容器：

```shell script
kubectl patch deployment/foo --type='json' -p \
  '[{"op":"add","path":"/spec/template/spec/containers/1","value":{"name":"nginx","image":"nginx:alpine"}}]'
```

修改已有容器 image：

```shell script
kubectl patch deployment/foo --type='json' -p \
  '[{"op":"replace","path":"/spec/template/spec/containers/0/image","value":"app-image:v2"}]'
```

这样一来，如果我们 patch 之前这个对象已经被其他人修改了，那么我们的 patch 有可能产生非预期的后果。比如在执行 app 容器镜像更新时，我们指定的序号是 0，但此时 containers 列表中第一个位置被插入了另一个容器，则更新的镜像就被错误地插入到这个非预期的容器中。

### merge patch
merge patch 无法单独更新一个列表中的某个元素，因此不管我们是要在 containers 里新增容器、还是修改已有容器的 image、env 等字段，都要用整个 containers 列表来提交 patch：

```shell script
kubectl patch deployment/foo --type='merge' -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"app","image":"app-image:v2"},{"name":"nginx","image":"nginx:alpline"}]}}}}'
```

显然，这个策略并不适合我们对一些列表深层的字段做更新，更适用于大片段的覆盖更新。

不过对于 labels/annotations 这些 map 类型的元素更新，merge patch 是可以单独指定 key-value 操作的，相比于 json patch 方便一些，写起来也更加直观：

kubectl patch deployment/foo --type='merge' -p '{"metadata":{"labels":{"test-key":"foo"}}}'

### strategic merge patch
这种 patch 策略并没有一个通用的 RFC 标准，而是 K8s 独有的，不过相比前两种而言却更为强大的。

我们先从 K8s 源码看起，在 K8s 原生资源的数据结构定义中额外定义了一些的策略注解。比如以下这个截取了 podSpec 中针对 containers 列表的定义

```go
// ...
// +patchMergeKey=name
// +patchStrategy=merge
Containers []Container `json:"containers" patchStrategy:"merge" patchMergeKey:"name" protobuf:"bytes,2,rep,name=containers"`
```

可以看到其中有两个关键信息：patchStrategy:"merge" patchMergeKey:"name" 。这就代表了，containers 列表使用 strategic merge patch 策略更新时，会把下面每个元素中的 name 字段看作 key。

简单来说，在我们 patch 更新 containers 不再需要指定下标序号了，而是指定 name 来修改，K8s 会把 name 作为 key 来计算 merge。比如针对以下的 patch 操作：
```shell script
kubectl patch deployment/foo -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:mainline"}]}}}}'
```
如果 K8s 发现当前 containers 中已经有名字为 nginx 的容器，则只会把 image 更新上去；而如果当前 containers 中没有 nginx 容器，K8s 会把这个容器插入 containers 列表。

此外还要说明的是，目前 strategic 策略只能用于原生 K8s 资源以及 Aggregated API 方式的自定义资源，对于 CRD 定义的资源对象，是无法使用的。这很好理解，因为 kube-apiserver 无法得知 CRD 资源的结构和 merge 策略。如果用 kubectl patch 命令更新一个 CR，则默认会采用 merge patch 的策略来操作。

### kubectl 封装
了解完了 K8s 的基础更新机制，我们再次回到最初的问题上。为什么用户修改 YAML 文件后无法直接调用 update 接口更新，却可以通过 kubectl apply 命令更新呢？

其实 kubectl 为了给命令行用户提供良好的交互体感，设计了较为复杂的内部执行逻辑，诸如 apply、edit 这些常用操作其实背后并非对应一次简单的 update 请求。毕竟 update 是有版本控制的，如果发生了更新冲突对于普通用户并不友好。以下简略介绍下 kubectl 几种更新操作的逻辑，有兴趣可以看一下 link:https://github.com/kubernetes/kubectl[kubectl] 封装的源码。

### apply
在使用默认参数执行 apply 时，触发的是 client-side apply。kubectl 逻辑如下：

首先解析用户提交的数据（YAML/JSON）为一个对象 A；然后调用 Get 接口从 K8s 中查询这个资源对象：

- 如果查询结果不存在，kubectl 将本次用户提交的数据记录到对象 A 的 annotation 中（key 为 kubectl.kubernetes.io/last-applied-configuration），最后将对象 A提交给 K8s 创建；
- 如果查询到 K8s 中已有这个资源，假设为对象 B：1. kubectl 尝试从对象 B 的 annotation 中取出 kubectl.kubernetes.io/last-applied-configuration 的值（对应了上一次 apply 提交的内容）；2. kubectl 根据前一次 apply 的内容和本次 apply 的内容计算出 diff（默认为 strategic merge patch 格式，如果非原生资源则采用 merge patch）；3. 将 diff 中添加本次的 kubectl.kubernetes.io/last-applied-configuration annotation，最后用 patch 请求提交给 K8s 做更新。

### edit
kubectl edit 逻辑上更简单一些。在用户执行命令之后，kubectl 从 K8s 中查到当前的资源对象，并打开一个命令行编辑器（默认用 vi）为用户提供编辑界面。

当用户修改完成、保存退出时，kubectl 并非直接把修改后的对象提交 update（避免 Conflict，如果用户修改的过程中资源对象又被更新），而是会把修改后的对象和初始拿到的对象计算 diff，最后将 diff 内容用 patch 请求提交给 K8s。

## 总结
看了上述的介绍，大家应该对 K8s 更新机制有了一个初步的了解了。接下来想一想，既然 K8s 提供了两种更新方式，我们在不同的场景下怎么选择 update 或 patch 来使用呢？这里我们的建议是：

- 如果要更新的字段只有我们自己会修改（比如我们有一些自定义标签，并写了 operator 来管理），则使用 patch 是最简单的方式；
- 如果要更新的字段可能会被其他方修改（比如我们修改的 replicas 字段，可能有一些其他组件比如 HPA 也会做修改），则建议使用 update 来更新，避免出现互相覆盖。


## 参考
- https://aijishu.com/a/1060000000118183