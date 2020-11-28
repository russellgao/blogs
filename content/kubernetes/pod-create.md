+++
title = "kubernetes 中 pod 是如何启动的呢"
description = "kubernetes 中 pod 是如何启动的呢"
date = "2020-11-24"
aliases = ["kubernetes 中 pod 是如何启动的呢"]
author = "russellgao"
draft = false
tags = [
    "kubernetes",
    "pod",
    "kubectl",
    "kubelet" ,
    "schedule"
]
+++

## 导读
> Pod 应该算是 kubernetes 的基本盘，Pod 是 kubernetes 的最小调度单位，我这里有个问题，说通过 `kubectl apply -f `
> 创建一个 Pod ，从执行到 Pod 正常运行 kubernetes 做了什么事情呢？都有哪些组件参与呢？这篇文档主要讲述从提交 Pod 的创建请求到
>Pod 的正常运行的这个过程追踪。

## kubectl 阶段
`kubectl apply` 阶段其实分为两个过程 ，先调用 get 方法，查看资源是否存在，存在则调用 `patch`, 否则执行 `create` 方法。
这个过程可以参考源码（文章中所有源码都截取了部分，详细可以在在给出的链接中查看）: 

vendor/k8s.io/kubectl/pkg/cmd/apply/apply.go
```go
// NewCmdApply creates the `apply` command
func NewCmdApply(baseName string, f cmdutil.Factory, ioStreams genericclioptions.IOStreams) *cobra.Command {
	o := NewApplyOptions(ioStreams)

	cmd := &cobra.Command{
		Use:                   "apply (-f FILENAME | -k DIRECTORY)",
		DisableFlagsInUseLine: true,
		Short:                 i18n.T("Apply a configuration to a resource by filename or stdin"),
		Long:                  applyLong,
		Example:               applyExample,
		Run: func(cmd *cobra.Command, args []string) {
			cmdutil.CheckErr(o.Complete(f, cmd))
			cmdutil.CheckErr(validateArgs(cmd, args))
			cmdutil.CheckErr(validatePruneAll(o.Prune, o.All, o.Selector))
			cmdutil.CheckErr(o.Run())
		},
	}

	...
}
```

```go
// Run executes the `apply` command.
func (o *ApplyOptions) Run() error {
	...
	// Iterate through all objects, applying each one.
	for _, info := range infos {
		if err := o.applyOneObject(info); err != nil {
			errs = append(errs, err)
		}
	}
	...
	return nil
}
```

```go
func (o *ApplyOptions) applyOneObject(info *resource.Info) error {
	...
	// Get the modified configuration of the object. Embed the result
	// as an annotation in the modified configuration, so that it will appear
	// in the patch sent to the server.
	modified, err := util.GetModifiedConfiguration(info.Object, true, unstructured.UnstructuredJSONScheme)
	if err != nil {
		return cmdutil.AddSourceToErr(fmt.Sprintf("retrieving modified configuration from:\n%s\nfor:", info.String()), info.Source, err)
	}

	if err := info.Get(); err != nil {
		if !errors.IsNotFound(err) {
			return cmdutil.AddSourceToErr(fmt.Sprintf("retrieving current configuration of:\n%s\nfrom server for:", info.String()), info.Source, err)
		}

		// Create the resource if it doesn't exist
		// First, update the annotation used by kubectl apply
		if err := util.CreateApplyAnnotation(info.Object, unstructured.UnstructuredJSONScheme); err != nil {
			return cmdutil.AddSourceToErr("creating", info.Source, err)
		}

		if o.DryRunStrategy != cmdutil.DryRunClient {
			// Then create the resource and skip the three-way merge
			obj, err := helper.Create(info.Namespace, true, info.Object)
			if err != nil {
				return cmdutil.AddSourceToErr("creating", info.Source, err)
			}
			info.Refresh(obj, true)
		}

		if err := o.MarkObjectVisited(info); err != nil {
			return err
		}

		if o.shouldPrintObject() {
			return nil
		}

		printer, err := o.ToPrinter("created")
		if err != nil {
			return err
		}
		if err = printer.PrintObj(info.Object, o.Out); err != nil {
			return err
		}
		return nil
	}

	if err := o.MarkObjectVisited(info); err != nil {
		return err
	}

	if o.DryRunStrategy != cmdutil.DryRunClient {
		metadata, _ := meta.Accessor(info.Object)
		annotationMap := metadata.GetAnnotations()
		if _, ok := annotationMap[corev1.LastAppliedConfigAnnotation]; !ok {
			fmt.Fprintf(o.ErrOut, warningNoLastAppliedConfigAnnotation, o.cmdBaseName)
		}

		patcher, err := newPatcher(o, info, helper)
		if err != nil {
			return err
		}
		patchBytes, patchedObject, err := patcher.Patch(info.Object, modified, info.Source, info.Namespace, info.Name, o.ErrOut)
		if err != nil {
			return cmdutil.AddSourceToErr(fmt.Sprintf("applying patch:\n%s\nto:\n%v\nfor:", patchBytes, info), info.Source, err)
		}

		info.Refresh(patchedObject, true)

		if string(patchBytes) == "{}" && !o.shouldPrintObject() {
			printer, err := o.ToPrinter("unchanged")
			if err != nil {
				return err
			}
			if err = printer.PrintObj(info.Object, o.Out); err != nil {
				return err
			}
			return nil
		}
	}
	...
	return nil
}
```

- apply 命令调用 `o.Run()` 执行 创建的动作
- `applyOneObject` 方法是真正执行创建 Pod 的动作
- 在 `applyOneObject` 方法中通过 `GetModifiedConfiguration` 函数执行 get 动作
- 如果是 `IsNotFound` 异常则 执行 `Create` 动作
- 否则执行 `Patch` 动作


> 上述过程除了用 kubectl ，当然也可以自己调用 api 去创建或者更新 。 

## apiserver 
通过客户端把请求提交到 apiserver 之后，接下来就是 apiserver 表演的时候了。

apiserver 会把 pod 数据存储到 etcd 中。

## Schedule
Schedule通过和API Server的watch机制，查看到新的Pod（通过 pod.spec.Node == nil 判断是否为新的Pod），尝试为Pod绑定Node。Schedle 的过程为 :

- 过滤主机：调度器用一组规则过滤掉不符合要求的主机，比如Pod指定了所需要的资源，那么就要过滤掉资源不够的主机
- 主机打分：对第一步筛选出的符合要求的主机进行打分，在主机打分阶段，调度器会考虑一些整体优化策略，比如把一个Replication Controller的副本分布到不同的主机上，使用最低负载的主机等
- 选择主机：选择打分最高的主机，进行binding操作
- 把调度结果通过apiserver 存储到 etcd 中

## kubelet
- kubelet从apiserver获取分配到其所在节点的Pod（watch 机制）
- kubelet调用Docker的 Api 创建容器，创建容器的过程为:
    - 先按顺序启动 `initContainers` 按照 `yaml` 中申明的顺序
    - 并发启动 `containers`
- kubelet将Pod状态更新到apiserver
- apiserver将状态信息写到etcd中


## 总结
> 上面每个步骤单拎出来都能有好多东西可以深入下去，这里从流程上简单的介绍了一个Pod 从发起创建请求到最终创建的一个文字版流程，仅供参考。
>
> 后续再详细分析每个组件。

Pod 的创建过程 :

- kubectl apply 执行过程: 
    - 先通过 get 查找资源对象，如果不存在则 `create pod` 否则 `patch pod`
- 通过 apply 提交请求到 apiserver ，apiserver 把 pod 数据存储到 etcd 中
- Schedule通过和API Server的watch机制，查看到新的Pod（通过 pod.spec.Node == nil 判断是否为新的Pod），尝试为Pod绑定Node。Schedle 的过程为:
    - 过滤主机：调度器用一组规则过滤掉不符合要求的主机，比如Pod指定了所需要的资源，那么就要过滤掉资源不够的主机
    - 主机打分：对第一步筛选出的符合要求的主机进行打分，在主机打分阶段，调度器会考虑一些整体优化策略，比如把一个Replication Controller的副本分布到不同的主机上，使用最低负载的主机等
    - 选择主机：选择打分最高的主机，进行binding操作
    - 把调度结果通过apiserver 存储到 etcd 中
- kubelet从apiserver获取分配到其所在节点的Pod（watch 机制）
- kubelet调用Docker的 Api 创建容器，创建容器的过程为:
    - 先按顺序启动 `initContainers` 按照 `yaml` 中申明的顺序
    - 并发启动 `containers`
- kubelet将Pod状态更新到apiserver
- apiserver将状态信息写到etcd中
