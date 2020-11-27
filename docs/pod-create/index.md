# kubernetes 中 pod 是如何启动的呢


## 导读
> Pod 应该算是 kubernetes 的基本盘，Pod 是 kubernetes 的最小调度单位，我这里有个问题，说通过 `kubectl apply -f `
> 创建一个 Pod ，从执行到 Pod 正常运行 kubernetes 做了什么事情呢？都有哪些组件参与呢？这篇文档主要讲述 Pod 的创建过程。

