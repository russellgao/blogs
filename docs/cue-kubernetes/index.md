# CUE 是如何在 Kubernetes 中使用的


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

## 参考
- https://github.com/cuelang/cue/tree/master/doc/tutorial/kubernetes


