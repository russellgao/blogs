+++
title = "细谈 Golang 中那些设计优美的细节-defer"
description = "Hugo, the world's fastest framework for building websites"
date = "2020-11-08"
aliases = ["about-me"]
author = "russellgao"
draft = false
tags = [
    "golang",
    "defer"
,]
+++

## 背景
在学习和使用 Go 的过程中发现，Go 在语言层面的设计有很多有趣的地方，所以准备用一个系列来细数这些有趣的地方。写这个系列一是为了加深自己的理解，二是愿意分享，分享 Go 中有趣的设计细节。每篇都会通过一个例子讲述一个细节，感兴趣的话可以关注一下哟！

## Go 介绍
Go（又称 Golang）是 Google 的 Robert Griesemer，Rob Pike 及 Ken Thompson 开发的一种静态强类型、编译型语言。Go 语言语法与 C 相近，但功能上有：内存安全，GC（垃圾回收），结构形态及 CSP-style 并发计算。

Go 是由这3位大佬从2007年9月开始设计Go，2009年正式推出，到目前为止已经发了15个大版本，最新版为1.15.4。Go 现在广泛应用于云原生、中间件、还有各个业务平台，如 docker、kubernetes、etcd等都是Go语言编写。所以还是很有必要了解一下哟！

下面简单说说Go的优缺点，俗话说：一万个人眼中有一万个哈姆雷特，所以优缺点都是相对而言，就谈谈自己使用过程中的感受，具体的优缺点会在后面的系列文章中一一提到，这里是抛砖引玉。

## Go 优点
- 语言层面支持并发：一个 go 关键字即可实现并发，其他编程语言依赖于库实现并发，这是有本质的区别
- 高性能
- 编译完之后生成二进制文件，可免去环境依赖
- defer 机制
- 内置runtime
- 内嵌C支持，Go里面也可以直接包含C代码，利用现有的丰富的C库
- 跨平台编译
- 。。。

## Go 缺点
- 包管理
- 。。。

## defer
说起 Go 语言的最强大的地方，不得不说 Go 的并发机制和调度原理，但是今天不讲这些高深的理论，先从简单的开始。先思考这么几个问题（可以用自己熟悉的语言思考如何解决）: 

- 对于文件的打开关闭，网络连接的建立断开场景，当打开时候应该何时关闭?
- 当调用一个函数，希望在函数返回时修改它的值，该如何解决?

先看看defer 的官方定义 ：
```
A "defer" statement invokes a function whose execution is deferred to the moment the surrounding function returns, either because the surrounding function executed a return statement, reached the end of its function body, or because the corresponding goroutine is panicking.
```

意思是说，当包裹defer 的函数返回时或者包裹defer的函数执行到末尾时或者所在的goroutine发生panic时才会执行。

换句话说就是当函数执行完之后或者发生异常时再执行defer语句，就是说在被调函数返回之后，赋值给调用函数之前，还有机会执行其他指令，是不是很神奇。先看一段python 代码 :
```python
def f(x,y) :
    z = x / y
    z += 1
    return z
​
if __name__ == "__main__" :
    result = f(4 /2)
```
当调用函数f，f返回给z并且赋值给result，在这时间，是没有任何机会执行其他的函数代码的。再看一段go代码:
```go
package main
func main() {
  result := f(4, 2)
  fmt.Println(result)
}
​
func f(x, y int) (r int) {
  r = x / y
  r += 1
  defer func() {
    r += 2
  }()
  return
}
```

当调用函数f，f返回之后，在赋值之前执行了r +=2 。现在回想一下之前的两个问题，如果有defer 机制，是不是可以很好的解决。如对于第一个问题，在defer 语句中处理文件的关闭，连接的释放等，而不用考虑一些异常情况。

那defer的实现原理是怎样的呢? 

defer 其实是调用runtime.deferproc 进行实现，在defer 出现的地方，插入了call runtime.deferproc，然后在函数返回之前的地方，插入指令call runtime.deferreturn。

普通函数返回时，汇编代码类似于:
```
add xx SP
return
```
如果包含了defer 语句，汇编代码类似于:
```
call runtime.deferreturn，
add xx SP
return
```
goroutine的控制结构中，有一张表记录defer，调用runtime.deferproc时会将需要defer的表达式记录在表中，而在调用runtime.deferreturn的时候，则会依次从defer表中出栈并执行。


defer 在使用过程中也存在一些坑，看几个例子: 

例1:
```go
func f() (result int) {
  defer func() {
    result++
  }()
  return 10
}
```
例2:
```go
func f() (result int) {
  t := 10
  defer func() {
    t = t + 1
  }()
  return t
}
```
例3:
```go
func f() (result int) {
  defer func(result int) {
    result = result + 1
  }(result)
  return 10
}
```

大家可以先心里默默算一下他们的结果
第一个是11，第二个是10，第三个是10。

defer表达式可能会在设置函数返回值之后，在返回到调用函数之前，修改返回值，使最终的函数返回值与你想象的不一致。其实使用defer时，用一个简单的转换规则改写一下，就不会迷糊了。改写规则是将return语句拆成两句写，return xxx会被改写成: 
```
返回值 = xxx
调用defer函数
空的return
```

例1 会被改写成:
```go
func f() (result int) {
  result = 10 // return语句不是一条原子调用，return xxx其实是赋值＋ret指令
  defer func() {
    result++
  }()
  return  // 空的return指令
}
```
所以返回值是11

例2 会被改写成:
```go
func f() (result int) {
  t := 10
  result = t // 赋值指令
  defer func() {
    t = t + 1 //defer被插入到赋值与返回之间执行，这个例子中返回值 result没被修改过
  }()
  return // 空的return指令
}
```
所以返回值是10

例3 就留给大家自己改写一下啦，有兴趣可以私我沟通哟！

## 总结

这篇主要做了对Go语言的介绍和优缺点，分析了defer 的用法以及实现原理，最后用例子展示了使用过程中可能会存在的坑。下篇预告: Go 的调度模型，欢迎关注!!!

如果有理解不正确的地方，欢迎指出。
