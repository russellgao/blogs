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

样例如下 :
```
[root@russellgao ~]# yum --help
错误：rpmdb: BDB0113 Thread/process 25958/140293357061952 failed: BDB1507 Thread died in Berkeley DB library
错误：db5 错误(-30973) 来自 dbenv->failchk：BDB0087 DB_RUNRECOVERY: Fatal error, run database recovery
错误：无法使用 db5 -  (-30973) 打开 Packages 索引
错误：无法从 /var/lib/rpm 打开软件包数据库
CRITICAL:yum.main:

Error: rpmdb open failed
[root@russellgao ~]# ll /var/lib/rpm/__db.*
-rw-r--r-- 1 root root  311296 4月  14 13:50 /var/lib/rpm/__db.001
-rw-r--r-- 1 root root   90112 4月  14 13:50 /var/lib/rpm/__db.002
-rw-r--r-- 1 root root 1318912 4月  14 13:50 /var/lib/rpm/__db.003
[root@russellgao ~]# rm -fr /var/lib/rpm/__db.*
[root@russellgao ~]# rpm --rebuilddb
[root@russellgao ~]# yum clean all
已加载插件：fastestmirror
Repodata is over 2 weeks old. Install yum-cron? Or run: yum makecache fast
正在清理软件源： base epel extras updates
Cleaning up list of fastest mirrors
[root@russellgao ~]# yum makecache
已加载插件：fastestmirror
Determining fastest mirrors
base                                                                                                                                  | 3.6 kB  00:00:00     
epel                                                                                                                                  | 4.7 kB  00:00:00     
extras                                                                                                                                | 2.9 kB  00:00:00     
updates                                                                                                                               | 2.9 kB  00:00:00     
(1/16): base/7/x86_64/group_gz                                                                                                        | 153 kB  00:00:00     
(2/16): base/7/x86_64/filelists_db                                                                                                    | 7.2 MB  00:00:00     
(3/16): base/7/x86_64/other_db                                                                                                        | 2.6 MB  00:00:00     
(4/16): base/7/x86_64/primary_db                                                                                                      | 6.1 MB  00:00:00     
(5/16): epel/x86_64/group_gz                                                                                                          |  96 kB  00:00:00     
(6/16): epel/x86_64/updateinfo                                                                                                        | 1.0 MB  00:00:00     
(7/16): epel/x86_64/prestodelta                                                                                                       | 1.5 kB  00:00:00     
(8/16): epel/x86_64/primary_db                                                                                                        | 6.9 MB  00:00:00     
(9/16): epel/x86_64/filelists_db                                                                                                      |  12 MB  00:00:00     
(10/16): epel/x86_64/other_db                                                                                                         | 3.3 MB  00:00:00     
(11/16): extras/7/x86_64/filelists_db                                                                                                 | 230 kB  00:00:00     
(12/16): extras/7/x86_64/other_db                                                                                                     | 138 kB  00:00:00     
(13/16): extras/7/x86_64/primary_db                                                                                                   | 232 kB  00:00:00     
(14/16): updates/7/x86_64/filelists_db                                                                                                | 4.2 MB  00:00:00     
(15/16): updates/7/x86_64/other_db                                                                                                    | 555 kB  00:00:00     
(16/16): updates/7/x86_64/primary_db                                                                                                  | 7.1 MB  00:00:00     
元数据缓存已建立

```

