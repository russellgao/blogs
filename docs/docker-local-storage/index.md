# docker 原理之本地存储


## 导读
> 在前面的文章[docker 原理之存储驱动](../docker-storage)中简单的介绍了 Docker 的存储驱动，这篇文章接着讲存储，目前的 docker 版本中默认的是 `overlay2` ，所以这篇文章就以 `overlay2` 为例带大家看看，在我们执行 `docker build` ，`docker pull`，`docker run` 等命令时本地存储有何变化。

## 背景
- 查看 docker `Storage Driver` 可以通过 `docker info | grep "Storage Driver"`命令。
- docker 的默认安装目录为： `/var/lib/docker`，如果要修改可以通过修改启动时的配置文件(默认为`/usr/lib/systemd/system/docker.service`) 中的 `ExecStart`，

查看 docker 启动时的配置文件: 

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-local-storage-1.jpg)

修改 docker 的存储目录:

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-local-storage-2.jpg)

修改(增加) `--graph` 即可。

## 本地目录
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# ll
总用量 48
drwx------ 2 root root 4096 11月 11 08:49 builder
drwx--x--x 4 root root 4096 11月 11 08:49 buildkit
drwx------ 3 root root 4096 12月  2 09:25 containers
drwx------ 3 root root 4096 11月 11 08:49 image
drwxr-x--- 3 root root 4096 11月 11 08:49 network
drwx------ 9 root root 4096 12月  2 09:25 overlay2
drwx------ 4 root root 4096 11月 11 08:49 plugins
drwx------ 2 root root 4096 11月 11 08:49 runtimes
drwx------ 2 root root 4096 11月 11 08:49 swarm
drwx------ 2 root root 4096 11月 11 13:32 tmp
drwx------ 2 root root 4096 11月 11 08:49 trust
drwx------ 2 root root 4096 11月 11 08:49 volumes
```

可以用 `tree` 进行展开
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# tree -L 2
.
├── builder
│   └── fscache.db
├── buildkit
│   ├── cache.db
│   ├── content
│   ├── executor
│   ├── metadata.db
│   └── snapshots.db
├── containers
│   └── 9bd6ac07a8c962e2403203e1c45f4fb54733f9953cf318b34fc3f155bf2c0c59
├── image
│   └── overlay2
├── network
│   └── files
├── overlay2
│   ├── 00b65b9c288df8c0ae7cdacba531a7dc5cb006e6c768e19ee36055717b782acc
│   ├── 1e53dddb1a0bb04ee4ebd24a8edb94b96e2fd471a72bf1b8608096b38cb16646
│   ├── 1e53dddb1a0bb04ee4ebd24a8edb94b96e2fd471a72bf1b8608096b38cb16646-init
│   ├── 5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4
│   ├── 8cbfb8b74c887e780747c8e6f4b3b9223a513ff6d69770bac16abb76da4e314f
│   ├── f1cf8b173467c98e08f3d276d7ccd8f9892c7c71dec2c4b335c39c6f175ae744
│   └── l
├── plugins
│   ├── storage
│   └── tmp
├── runtimes
├── swarm
├── tmp
├── trust
└── volumes
    └── metadata.db
26 directories, 5 files
```


## 参考
- https://segmentfault.com/a/1190000017579626
- https://arkingc.github.io/2017/05/05/2017-05-05-docker-filesystem-overlay/
- https://www.cnblogs.com/wdliu/p/10483252.html


