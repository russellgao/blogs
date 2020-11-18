# python中的多线程与多进程


## 导读
在编码的过程，多线程、多进程、并发、并行这些概念肯定不止一次的出现在我们面前。概念理解是一回事，但是能真正用好又是另一回事。不同的编程语言，并发编程难易程度相差还是很大的，正好这几天梳理了他们之间的关系与区别，分享给大家。（基于自己的理解谈谈，如果不对欢迎指出）

> 灵魂拷问：什么是线程？什么是进程？

## 进程
进程是资源分配的最小单位。

## 线程
线程是 cpu 调度的最小调度。线程又分为内核线程，用户线程。

内核线程只运行在内核态，不受用户态的拖累。

用户线程是完全建立在用户空间的线程库，用户线程的创建、调度、同步和销毁在用户空间完成，不需要内核的帮助。用户线程又称为协程。

一个线程只能属于一个进程，但是一个进程可以有多个线程，多线程处理就是一个进程可以有多个线程在同一个时刻执行多个任务。

这些是比较官方的定义，简单理解就是运行一段程序，需要一定的资源，如cpu，系统内核会分配给进程，至于怎么分配这些资源可由线程去抢，如果某个线程占用资源(cpu)时间太长，内核为了平衡，会强行中断，切换给其他的线程执行，但是每次切换都是有代价的，需要把执行现场保留以确保后续恢复的时候可以正常执行，这就有了内核和用户态的切换（进程和线程都是受内核控制的）。那么问题来了，如果只在用户态切换，岂不是很好？还真是这样，go 语言就是这样实现。

## python 多线程时遇到的坑
python 中如果要用多线程或者多进程时需要自己创建线程或者进程，这和go语言不一样，go语言只需要通过 go 关键字创建出协程，然后由runtime 进行调度（不需要自己处理进程与线程）。今天先看看python 中如何使用多线程与多进程。python 环境为 2.7.15 。

先看一段简单的代码
```python
import threading
import time
​
lock = threading.Lock()
​
def runner(i, p1, p2, p3="", p4="", **kwargs):
    """
    :return:
    """
    count = 0
    print("线程{} param1:====".format(i), p1)
    print("线程{} param2:====".format(i), p2)
    print("线程{} param3:====".format(i), p3)
    print("线程{} param3:====".format(i), p4)
    while True:
        with lock:
            count += 1
            print("线程{} 第 {} 秒 后: ......".format(i, count))
            time.sleep(1)
            if count == 5:
                break
                
def main_thread():
    """
    主线程的运行代码
    :return:
    """
    print("主线程开始执行")
    time.sleep(1)
    print("主线程执行结束")
​
def main():
    """
    :return:
    """
    for i in range(5):
        thread = threading.Thread(target=runner, args=(i, "a1", "a2"), kwargs={"p3": "p2", "p4": "p4"})
        thread.setName("线程{}".format(i))
        thread.start()
​
    main_thread()
​
if __name__ == "__main__":
    main()
​
```

这个应该能想的出来不同的线程的输出是交叉打印出来的，说明这是多个线程并发执行的。

现在假设有这么一个场景，有10台机器，每个机器上有10个容器需要重启，如果要并发的执行应该怎么做呢? 看看下面的代码有没有问题? 
```python
import os
​
import threading
​
def runnner(hostip) :
    appIds = [ "app-{}".format(i) for i in range(10)]
    cmd = "docker restart {}".format(" ".join(appIds))
    print(cmd)
    os.system("ssh {hostip} {cmd}".format(hostip=hostip,cmd=cmd))
​
hosts = ["10.0.0.1", "10.0.0.2", "10.0.0.3" , "10.0.0.4", "10.0.0.5","10.0.0.6", "10.0.0.7", "10.0.0.8" , "10.0.0.9", "10.0.0.10"]
​
for hostip in hosts :
    thread = threading.Thread(target=runnner, args=(hostip,))
    thread.start()
```

看起来应该是没有问题的，然而真正执行的还是串行，没有到达并发执行的目的。问题出在哪里呢？

在python 中线程执行需要先获取GIL锁（全局解释器锁），看起来是创建了多个线程，但是同一个时间点每个进程只能有一个线程获取这个锁并且执行，是一种伪多线程，如果在密集计算的场景，就会频繁的发生线程切换，这个是很耗时间的，还没有单线程效果好。那么问题又来了，什么会发生线程切换呢?
如果遇到io等待或者sleep 时肯定会发生切换，还有就是每100条指令切换一次线程。可以通过如下指令设置:
```python
sys.setcheckinterval
```

上面这里例子就没有触发线程的切换，当前面的线程执行完退出之后释放GIL锁，后续的线程才能执行，所以才有看起来是多线程的写法，但是确实单线程的效果。

改进的方法当然使用多进程，每个进程都有自己的GIL锁，可以真正的实现并发。进程并不是越多越好，创建进程开销比线程要大很多，如果进程之间有数据交换也比线程复杂，并且真正执行还是要落到cpu上去执行，进程多了也会造成排队，理论上和创建和cpu相同个数的进程性能最好。下面看看多进程的写法。
```python
import os
from multiprocessing import Process
​
def runnner(hostip) :
    appIds = [ "app-{}".format(i) for i in range(10)]
    cmd = "docker restart {}".format(" ".join(appIds))
    print(cmd)
    os.system("ssh {hostip} {cmd}".format(hostip=hostip,cmd=cmd))
​
​
hosts = ["10.0.0.{}".format(i) for i in range(10)]
​
​
for hostip in hosts :
    process = Process(target=runnner, args=(hostip,))
    process.start()
```

当然可以用进程池控制进程的个数，如:

```python
import os
​
from multiprocessing import Pool
​
def runnner(hostip) :
    appIds = [ "app-{}".format(i) for i in range(10)]
    cmd = "docker restart {}".format(" ".join(appIds))
    print(cmd)
    os.system("ssh {hostip} {cmd}".format(hostip=hostip,cmd=cmd))
​
​
hosts = ["10.0.0.{}".format(i) for i in range(10)]
​
p = Pool(4)
​
for hostip in hosts :
    p.apply_async(runnner, args=(hostip,)) # 异步执行
p.close()
p.join()
```

## 参考
- https://docs.python.org/2/library/sys.html#sys.setcheckinterval
