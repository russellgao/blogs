+++
title = "python中的多线程与多进程（二）"
description = "python中的多线程与多进程（二）"
date = "2020-11-18 22:32:00"
aliases = ["python 多线程"]
author = "russellgao"
draft = false
tags = [
    "python",
    "多线程",
    "多进程"
,]
+++

## 导读
> 在上一篇["python中的多线程与多进程(一)](https://russellgao.cn/multithread/)中介绍了进程、线程的概念、基本用法和在 python 中使用遇到的一些坑，
这在一篇中会介绍一些高级的用法，当然更多的是遇到的坑，换言之这是一片避坑指南。

## concurrent.futures
我们都知道在 python 中，多线程的标准库是使用 `threading` , 如 ：

```python
# -*- coding: UTF-8 -*-

import threading
import time

def runner(index, param) :
    print("线程{} 开始运行: ------------".format(index))
    print("线程{} : {}".format(index,param))
    time.sleep(3)
    print("线程{} 运行结束: ------------".format(index))

for index,value in enumerate(["python", "java", "golang", "php"]) :
    thread = threading.Thread(target=runner,args=(index, value, ))
    thread.start()
```

多进程的库是 `multiprocessing` ,如： 
```python
# -*- coding: UTF-8 -*-

from multiprocessing import Process
import time

def runner(index, param) :
    print("线程{} 开始运行: ------------".format(index))
    print("线程{} : {}".format(index,param))
    time.sleep(3)
    print("线程{} 运行结束: ------------".format(index))

for index,value in enumerate(["python", "java", "golang", "php"]) :
    process = Process(target=runner,args=(index, value, ))
    process.start()
```

以上两个库已经 python2 已经支持，可以很少的实现我们多进程与多线程的需求。 python3.2 提供了 `concurrent.futures` 库，并且已经回溯到python2，这个库在 `threading` 
与 `multiprocessing` 的基础上提供了一层封装，使得使用多线程和多进程的行为上保持了一直，为什么这么说呢且看下面分析，请先看两段代码：

**多线程**
```python
# -*- coding: UTF-8 -*-

from concurrent.futures._base import TimeoutError
from concurrent.futures import ThreadPoolExecutor
import time

def runner(index, param) :
    print("线程{} 开始运行: ------------".format(index))
    print("线程{} : {}".format(index,param))
    time.sleep(3)
    print("线程{} 运行结束: ------------".format(index))

max_workers = 4
print("执行升级任务的并发数为为： {}".format(max_workers))
runners = ["python", "java", "golang", "php", "rust", "shell", "c"]
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    for index, value in enumerate(runners):
        result = executor.submit(runner, index, value)
    try:
        result.result(timeout=3 * 60 )
    except TimeoutError as err:
        print("任务超时,", err)

```

**多进程**
```python
# -*- coding: UTF-8 -*-

from concurrent.futures._base import TimeoutError
from concurrent.futures import ProcessPoolExecutor
import time

def runner(index, param) :
    print("线程{} 开始运行: ------------".format(index))
    print("线程{} : {}".format(index,param))
    time.sleep(3)
    print("线程{} 运行结束: ------------".format(index))

max_workers = 4
print("执行升级任务的并发数为为： {}".format(max_workers))
runners = ["python", "java", "golang", "php", "rust", "shell", "c"]
with ProcessPoolExecutor(max_workers=max_workers) as executor:
    for index, value in enumerate(runners):
        result = executor.submit(runner, index, value)
    try:
        result.result(timeout=3 * 60 )
    except TimeoutError as err:
        print("任务超时,", err)
```

可以看到多进程和多线程写法超级类似，一个使用的是 ProcessPoolExecutor ，一个使用的是 ThreadPoolExecutor，其他代码基本一直，查看源码可以发现

`concurrent.futures` 定义了一个 `Executor` 抽象基类，提供了 `submit` 、`map` 、`shutdown` 等方法

```python
class Executor(object):
    """This is an abstract base class for concrete asynchronous executors."""

    def submit(self, fn, *args, **kwargs):
        """Submits a callable to be executed with the given arguments.

        Schedules the callable to be executed as fn(*args, **kwargs) and returns
        a Future instance representing the execution of the callable.

        Returns:
            A Future representing the given call.
        """
        raise NotImplementedError()

    def map(self, fn, *iterables, **kwargs):
        """Returns a iterator equivalent to map(fn, iter).

        Args:
            fn: A callable that will take as many arguments as there are
                passed iterables.
            timeout: The maximum number of seconds to wait. If None, then there
                is no limit on the wait time.

        Returns:
            An iterator equivalent to: map(func, *iterables) but the calls may
            be evaluated out-of-order.

        Raises:
            TimeoutError: If the entire result iterator could not be generated
                before the given timeout.
            Exception: If fn(*args) raises for any values.
        """
        timeout = kwargs.get('timeout')
        if timeout is not None:
            end_time = timeout + time.time()

        fs = [self.submit(fn, *args) for args in itertools.izip(*iterables)]

        # Yield must be hidden in closure so that the futures are submitted
        # before the first iterator value is required.
        def result_iterator():
            try:
                for future in fs:
                    if timeout is None:
                        yield future.result()
                    else:
                        yield future.result(end_time - time.time())
            finally:
                for future in fs:
                    future.cancel()
        return result_iterator()

    def shutdown(self, wait=True):
        """Clean-up the resources associated with the Executor.

        It is safe to call this method several times. Otherwise, no other
        methods can be called after this one.

        Args:
            wait: If True then shutdown will not return until all running
                futures have finished executing and the resources used by the
                executor have been reclaimed.
        """
        pass
```

而 多进程（ProcessPoolExecutor）和 多线程（ThreadPoolExecutor）继承了 Executor ，并重写了 `submit` 和 `shutdown` 方法

**多线程**
```python
class ThreadPoolExecutor(_base.Executor):
    def __init__(self, max_workers):
        """Initializes a new ThreadPoolExecutor instance.

        Args:
            max_workers: The maximum number of threads that can be used to
                execute the given calls.
        """
        self._max_workers = max_workers
        self._work_queue = queue.Queue()
        self._threads = set()
        self._shutdown = False
        self._shutdown_lock = threading.Lock()

    def submit(self, fn, *args, **kwargs):
        with self._shutdown_lock:
            if self._shutdown:
                raise RuntimeError('cannot schedule new futures after shutdown')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._work_queue.put(w)
            self._adjust_thread_count()
            return f
    submit.__doc__ = _base.Executor.submit.__doc__

    def _adjust_thread_count(self):
        # When the executor gets lost, the weakref callback will wake up
        # the worker threads.
        def weakref_cb(_, q=self._work_queue):
            q.put(None)
        # TODO(bquinlan): Should avoid creating new threads if there are more
        # idle threads than items in the work queue.
        if len(self._threads) < self._max_workers:
            t = threading.Thread(target=_worker,
                                 args=(weakref.ref(self, weakref_cb),
                                       self._work_queue))
            t.daemon = True
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue

    def shutdown(self, wait=True):
        with self._shutdown_lock:
            self._shutdown = True
            self._work_queue.put(None)
        if wait:
            for t in self._threads:
                t.join(sys.maxint)
    shutdown.__doc__ = _base.Executor.shutdown.__doc__
```
可以看到submit 对 `threading` 进行了封装

**多进程**
```python
class ProcessPoolExecutor(_base.Executor):
    def __init__(self, max_workers=None):
        """Initializes a new ProcessPoolExecutor instance.

        Args:
            max_workers: The maximum number of processes that can be used to
                execute the given calls. If None or not given then as many
                worker processes will be created as the machine has processors.
        """
        _check_system_limits()

        if max_workers is None:
            self._max_workers = multiprocessing.cpu_count()
        else:
            self._max_workers = max_workers

        # Make the call queue slightly larger than the number of processes to
        # prevent the worker processes from idling. But don't make it too big
        # because futures in the call queue cannot be cancelled.
        self._call_queue = multiprocessing.Queue(self._max_workers +
                                                 EXTRA_QUEUED_CALLS)
        self._result_queue = multiprocessing.Queue()
        self._work_ids = queue.Queue()
        self._queue_management_thread = None
        self._processes = set()

        # Shutdown is a two-step process.
        self._shutdown_thread = False
        self._shutdown_lock = threading.Lock()
        self._queue_count = 0
        self._pending_work_items = {}

    def _start_queue_management_thread(self):
        # When the executor gets lost, the weakref callback will wake up
        # the queue management thread.
        def weakref_cb(_, q=self._result_queue):
            q.put(None)
        if self._queue_management_thread is None:
            self._queue_management_thread = threading.Thread(
                    target=_queue_management_worker,
                    args=(weakref.ref(self, weakref_cb),
                          self._processes,
                          self._pending_work_items,
                          self._work_ids,
                          self._call_queue,
                          self._result_queue))
            self._queue_management_thread.daemon = True
            self._queue_management_thread.start()
            _threads_queues[self._queue_management_thread] = self._result_queue

    def _adjust_process_count(self):
        for _ in range(len(self._processes), self._max_workers):
            p = multiprocessing.Process(
                    target=_process_worker,
                    args=(self._call_queue,
                          self._result_queue))
            p.start()
            self._processes.add(p)

    def submit(self, fn, *args, **kwargs):
        with self._shutdown_lock:
            if self._shutdown_thread:
                raise RuntimeError('cannot schedule new futures after shutdown')

            f = _base.Future()
            w = _WorkItem(f, fn, args, kwargs)

            self._pending_work_items[self._queue_count] = w
            self._work_ids.put(self._queue_count)
            self._queue_count += 1
            # Wake up queue management thread
            self._result_queue.put(None)

            self._start_queue_management_thread()
            self._adjust_process_count()
            return f
...
```
同样可以看到 `submit` 对 `multiprocessing` 进行了封装。

以上源码来自 `python 2.7.15` ，python 3和上面的有所不同，就不贴了。

## concurrent 使用过程中遇到的坑
执行环境为 `python-2.7.15`

假设有这么一个脚本 `multipy.py`
```python
# -*- coding: UTF-8 -*-

from concurrent.futures._base import TimeoutError
from concurrent.futures import ProcessPoolExecutor
import time

def runner(index, param) :
    print("线程{} 开始运行: ------------".format(index))
    print("线程{} : {}".format(index,param))
    time.sleep(3)
    print("线程{} 运行结束: ------------".format(index))

def main(max_workers=1) :
    print("执行升级任务的并发数为为： {}".format(max_workers))
    runners = ["python", "java", "golang", "php", "rust", "shell", "c"]
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for index, value in enumerate(runners):
            result = executor.submit(runner, index, value)
        try:
            result.result(timeout=3 * 60)
        except TimeoutError as err:
            print("任务超时,", err)

if __name__ == "__main__" :
    main(3)
```
通过在命令行执行 `python multipy.py` ，大家可以在心里想象一下会输出什么。

第二个场景是：同样的脚本， 通过 setuptools 安装后执行，部分代码（setup.py）如下: 

```python
#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="pyctl",
    
    entry_points='''
         [console_scripts]
         pyctl=pyctl.commands.shell:cli
     ''',
    classifiers=[
        ...
    ],
    install_requires=[
        ...
        'click==7.0'
    ],
)
```

安装完成之后可以在命令行通过 `pyctl xxx ...` 执行，和执行系统命令是一样的，如果不熟悉 `setuptools` 可以先了解一下，文档参考[https://pypi.org/project/setuptools/](https://pypi.org/project/setuptools/)

言归正传，通过 setuptools 打包之后再执行这个脚本，我们可以假设打包之后的执行方式为 `pyctl multipy` ，执行后会发生什么呢？大家也可以在心里先想象一下。

> 实际的结果就是直接通过 `python multipy.py` 的方式可以得到正确的结果，确实按照多进程的方式并发执行，但是到第二个场景时却无法运行，通过 
`ps -ef` 查看进程，确实创建了多个进程，但这些进程都被阻塞，没有执行 `runner 函数里面的内容`，程序会被卡死。当时百思不解其中的原因，尝试过很多方法，包括使用原生的 `multiprocessing`
自己实现进程管理也是同样的效果，最后是同样的代码，换到python3.8，两种方法都可以得到正确结果。python2.7 为啥会卡死，多个进程创建出来没有执行 runner 任务至今还没有找到原因，后续有进展再更新，
欢迎知道原因的小伙伴留言告知！！！
