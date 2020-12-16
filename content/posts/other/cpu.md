+++
title = "深入浅出的聊聊 cpu 负载与使用率"
description = "深入浅出的聊聊 cpu 负载与使用率"
date = "2020-12-15"
aliases = ["深入浅出的聊聊 cpu 负载与使用率"]
author = "russellgao"
draft = false
tags = [
    "linux",
    "cpu"
]
+++

## 导读
> 在定位性能问题时，一个绕不开的话题就是 CPU ，会觉得 CPU 不够用了，或者是瓶颈了，那么怎么来确定是 CPU 的问题呢？衡量 CPU 的指标有两个，CPU 负载(load average) 和 使用率，这两者有什么关系和区别呢？
>这篇文章带大家深层次的了解一下 CPU 。
>

## 什么是CPU
CPU 就是计算机的中央处理器(Central Processing Unit)，其功能主要是解释计算机指令以及处理计算机软件中的数据。CPU是计算机中负责读取指令，对指令译码并执行指令的核心部件。中央处理器主要包括两个部分，即控制器、运算器，其中还包括高速缓冲存储器及实现它们之间联系的数据、控制的总线。电子计算机三大核心部件就是CPU、内部存储器、输入/输出设备。中央处理器的功效主要为处理指令、执行操作、控制时间、处理数据。

> 来自百度百科上的定义。

## CPU 结构

![](https://gitee.com/russellgao/blogs-image/raw/master/images/linux/cpu-core.svg)

上面这张图片描述了现在的CPU的基本情况，一个物理核心中包含多个核心(多核结构)。这张图表示一个物理核心中包含4个核心，而现在的 CPU 都会用到超线程技术，Inter 一般是把一个核分成2个，所以上这个就代表 `8` 核(8=1 * 4 * 2) 。

> **超线程技术**把多线程处理器内部的两个逻辑内核模拟成两个物理芯片，让单个处理器就能使用线程级的并行计算，进而兼容多线程操作系统和软件。超线程技术充分利用空闲CPU资源，在相同时间内完成更多工作。
> 
> 超线程技术主要的出发点是，当处理器在运行一个线程，执行指令代码时，很多时候处理器并不会使用到全部的计算能力，部分计算能力就会处于空闲状态。而超线程技术就是通过多线程来进一步“压榨”处理器。举个例子，如果一个线程运行过程中，必须要等到一些数据加载到缓存中以后才能继续执行，此时CPU就可以切换到另一个线程，去执行其他指令，而不用去处于空闲状态，等待当前线程的数据加载完毕。
>通常，一个传统的处理器在线程之间切换，可能需要几万个时钟周期。而一个具有HT超线程技术的处理器只需要1个时钟周期。因此就大大减小了线程之间切换的成本，从而最大限度地让处理器满负荷运转。

所以得出一个结论: **总核数 = 物理核数 * 每个物理核心的核数 * 超线程数**

### cpu 信息查看
在 unix 系统下查看 cpu 详细信息的方法为 : 

```shell script
[root@iZuf685opgs9oyozju9i2bZ ~]# cat /proc/cpuinfo 
processor	: 0
vendor_id	: GenuineIntel
cpu family	: 6
model		: 85
model name	: Intel(R) Xeon(R) Platinum 8269CY CPU @ 2.50GHz
stepping	: 7
microcode	: 0x1
cpu MHz		: 2499.998
cache size	: 36608 KB
physical id	: 0
siblings	: 2
core id		: 0
cpu cores	: 1
apicid		: 0
initial apicid	: 0
fpu		: yes
fpu_exception	: yes
cpuid level	: 22
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc rep_good nopl nonstop_tsc eagerfpu pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch invpcid_single fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm mpx avx512f avx512dq rdseed adx smap avx512cd avx512bw avx512vl xsaveopt xsavec xgetbv1 arat avx512_vnni
bogomips	: 4999.99
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:

processor	: 1
vendor_id	: GenuineIntel
cpu family	: 6
model		: 85
model name	: Intel(R) Xeon(R) Platinum 8269CY CPU @ 2.50GHz
stepping	: 7
microcode	: 0x1
cpu MHz		: 2499.998
cache size	: 36608 KB
physical id	: 0
siblings	: 2
core id		: 0
cpu cores	: 1
apicid		: 1
initial apicid	: 1
fpu		: yes
fpu_exception	: yes
cpuid level	: 22
wp		: yes
flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc rep_good nopl nonstop_tsc eagerfpu pni pclmulqdq ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch invpcid_single fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm mpx avx512f avx512dq rdseed adx smap avx512cd avx512bw avx512vl xsaveopt xsavec xgetbv1 arat avx512_vnni
bogomips	: 4999.99
clflush size	: 64
cache_alignment	: 64
address sizes	: 46 bits physical, 48 bits virtual
power management:
```

## CPU 负载
在 unix 系统下可以通过 `top` 命令看到3个值 :
```shell script
[root@iZuf685opgs9oyozju9i2bZ ~]# top

top - 21:18:36 up 35 days, 12:39,  1 user,  load average: 0.00, 0.01, 0.05
Tasks:  99 total,   1 running,  98 sleeping,   0 stopped,   0 zombie
...
```

load average: 0.00, 0.01, 0.05 表示系统在最近 `1、5、15`分钟内的平均负载。那么什么是负载呢 ?

> cpu 负载指的是: 系统在一段时间内正在使用和等待使用CPU的平均任务数。描述的是任务的排队情况。

借用网上的一个例子：**公用电话**


## CPU 使用率
cpu使用率是程序在运行期间实时占用的CPU百分比。描述的是 cpu 的繁忙情况。

## 总结

