# yum 踩坑记录



## 导读
> yum 在使用过程中会遇到一些奇奇怪怪的问题，这里主要记录遇到的问题已经如何修复。这篇文档会持续更新。
>

## 踩坑1
在执行 `yum` 命令时报如下错误，不管执行任何命令都一样，如 `yum list` , `yum search` ,`yum install`

### 错误现象
```shell script
yum list
# 下面为输出
错误：rpmdb: BDB0113 Thread/process 25958/140293357061952 failed: BDB1507 Thread died in Berkeley DB library
错误：db5 错误(-30973) 来自 dbenv->failchk：BDB0087 DB_RUNRECOVERY: Fatal error, run database recovery
错误：无法使用 db5 -  (-30973) 打开 Packages 索引
错误：无法从 /var/lib/rpm 打开软件包数据库
CRITICAL:yum.main:
```

或者
```shell script
yum --help
# 下面为输出
错误：rpmdb: BDB0113 Thread/process 25958/140293357061952 failed: BDB1507 Thread died in Berkeley DB library
错误：db5 错误(-30973) 来自 dbenv->failchk：BDB0087 DB_RUNRECOVERY: Fatal error, run database recovery
错误：无法使用 db5 -  (-30973) 打开 Packages 索引
错误：无法从 /var/lib/rpm 打开软件包数据库
CRITICAL:yum.main:

Error: rpmdb open failed
```

### 错误原因
rpm数据库损坏，需要重建 rpm 数据库

### 解决方法
```shell script
# 查看下有哪些数据库
ll /var/lib/rpm/__db.*
# 删除 rpm 数据库
rm -fr /var/lib/rpm/__db.*
# 重建数据库
rpm --rebuilddb
# 清除缓存
yum clean all
# 重建缓存
yum makecache
```

至此问题即可得到解决。

