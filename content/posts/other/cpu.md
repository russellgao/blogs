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
categories = [
    "linux"
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
在 unix 系统下查看 CPU 详细信息的方法为 `cat /proc/cpuinfo ` : 

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
上面这是一个 `1一个物理核心，一个物理核心只有一个核，一个核上有两个超线程` 的 CPU 详细信息。

关键指标说明: 

- processor: 逻辑核心的序号，默认从 0 开始，对于单核处理器，则可以认为是其CPU编号，对于多核处理器则可以是物理核、或者使用超线程技术虚拟的逻辑核。
- vendor_id: CPU 制造商
- cpu family: CPU 产品系列代号
- model: CPU属于其系列中的哪一代的代号
- model name: CPU属于的名字及其编号、标称主频
- stepping: CPU属于制作更新版本
- cpu MHz: CPU的实际使用主频
- cache size: CPU二级缓存大小
- physical id: 单个CPU的标号
- siblings: 单个CPU逻辑物理核数
- core id: 当前物理核在其所处CPU中的编号，这个编号不一定连续
- cpu cores: 该逻辑核所处CPU的物理核数
- apicid: 用来区分不同逻辑核的编号，系统中每个逻辑核的此编号必然不同，此编号不一定连续
- fpu: 是否具有浮点运算单元（Floating Point Unit）
- fpu_exception: 是否支持浮点计算异常
- cpuid level : 执行cpuid指令前，eax寄存器中的值，根据不同的值cpuid指令会返回不同的内容
- wp: 表明当前CPU是否在内核态支持对用户空间的写保护（Write Protection）
- flags: 当前CPU支持的功能
- bogomips: 在系统内核启动时粗略测算的CPU速度（Million Instructions Per Second）
- clflush size: 每次刷新缓存的大小单位
- cache_alignment: 缓存地址对齐单位
- address sizes: 可访问地址空间位数
- power management: 对能源管理的支持


对于 cpu 的常用操作如下:
> 查看 CPU 型号:
>```shell script
>[root@iZuf685opgs9oyozju9i2bZ ~]# cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c
>       2  Intel(R) Xeon(R) Platinum 8269CY CPU @ 2.50GHz
>```
> 查看物理 CPU 个数
>```shell script
>[root@iZuf685opgs9oyozju9i2bZ ~]# cat /proc/cpuinfo| grep "physical id"| sort| uniq| wc -l
> 1
>```
> 查看每个物理 CPU 中 core 的个数(即核数)
> ```shell script
>[root@iZuf685opgs9oyozju9i2bZ ~]# cat /proc/cpuinfo| grep "cpu cores"| uniq 
>cpu cores	: 1
> ```
> 查看逻辑 CPU 的个数
> ```shell script
>[root@iZuf685opgs9oyozju9i2bZ ~]# cat /proc/cpuinfo| grep "processor"| wc -l
>2
>```
> 查看 CPU 是运行在 32 位还是 64 位模式下
> ```shell script
>[root@iZuf685opgs9oyozju9i2bZ ~]# getconf LONG_BIT
> 64
> ```


## CPU 负载
在 unix 系统下可以通过 `top` 命令看到3个值 :
```shell script
[root@iZuf685opgs9oyozju9i2bZ ~]# top

top - 21:18:36 up 35 days, 12:39,  1 user,  load average: 0.00, 0.01, 0.05
Tasks:  99 total,   1 running,  98 sleeping,   0 stopped,   0 zombie
...
```

load average: 0.00, 0.01, 0.05 表示系统在最近 `1、5、15`分钟内的平均负载。那么什么是负载呢 ?

> CPU 负载指的是: 系统在一段时间内正在使用和等待使用CPU的平均任务数。描述的是任务的排队情况。

借用网上的一个例子：**公用电话**

把CPU比作电话亭，把任务比作排队打电话的人。有一堆人排队打电话，每个人只允许打1分钟的电话，如果时间到了还没有打完还是需要重新去排队。在打电话的时候，肯定会遇到排队等待电话的人，也有打完电话走掉的人，也有新来排队的人，也有打完1分钟后没打完又重新排队的人。那这个人数的变化就相当于任务的增减。为了统计平均负载状态，每分钟统计一次，计算最近`1、5、15`分钟的平均值。
load低并不意味着CPU的利用率低，有的人(任务)拿起电话(CPU)一直打完1分钟，这时候 cpu 使用率为100%，有的人(任务)拿起电话(CPU)一直犹豫是否要打或者在找手机号，30秒后才拨通了电话，只有后30秒是真正在打电话，这时候cpu使用率为50% ，当然实际情况可能会有偏差。


## CPU 使用率
CPU 使用率是程序在运行期间实时占用的CPU百分比。描述的是 cpu 的繁忙情况。

cpu 使用率高不一定负载高，看看下面的代码:
```go
func main() {
	for {
		num1 := 1
		num2 := 1
		num3 := num1 + num2
		fmt.Println(num3)
	}
}
```

这个程序会一直占着 cpu ，如果是单核的，cpu 使用率为 100%，负载为1。

## 负载与使用率分析
### 负载高、使用率低
说明等待执行的任务很多。很可能是进程僵死了。通过命令 `ps -aux` 查看是否存在D状态的进程，该状态为不可中断的睡眠状，态。处于D状态的进程通常是在等待IO，通常是IO密集型任务，如果大量请求都集中于相同的IO设备，超出设备的响应能力，会造成任务在运行队列里堆积等待，也就是D状态的进程堆积，那么此时Load Average就会飙高。

### 利用率高、负载低
说明任务少，但是任务执行时间长，有可能是程序本身有问题，如果没有问题那么计算完成后则利用率会下降。这种场景，通常是计算密集型任务，即大量生成耗时短的计算任务。

### 使用率低、负载低、IOPS 高
通常是低频大文件读写，由于请求数量不大，所以任务都处于R状态(表示正在运行，或者处于运行队列，可以被调度运行)，负载数值反映了当前运行的任务数，不会飙升，IO设备处于满负荷工作状态，导致系统响应能力降低。

## 总结
- CPU 就是计算机的中央处理器(Central Processing Unit)，其功能主要是解释计算机指令以及处理计算机软件中的数据
- 总核数 = 物理核数 * 每个物理核心的核数 * 超线程数
- CPU 负载是系统在一段时间内正在使用和等待使用CPU的平均任务数。描述的是任务的排队情况。
- CPU 使用率是程序在运行期间实时占用的CPU百分比。描述的是 cpu 的繁忙情况。
- CPU 负载高并不能说明 CPU 使用率高，反之亦然。
