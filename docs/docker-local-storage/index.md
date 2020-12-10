# docker 原理之本地存储


## 导读
> 在前面的文章[docker 原理之存储驱动](../docker-storage)中简单的介绍了 Docker 的存储驱动，这篇文章接着讲存储，目前的 docker 版本中默认的是 `overlay2` ，所以这篇文章就带大家看看，在我们执行 `docker build` ，`docker pull`，`docker run` 等命令时本地存储有何变化。

## 背景
- 查看 docker `Storage Driver` 可以通过 `docker info | grep "Storage Driver"`命令。
- docker 的默认安装目录为： `/var/lib/docker`，如果要修改可以通过修改启动时的配置文件(默认为`/usr/lib/systemd/system/docker.service`) 中的 `ExecStart`，

查看 docker 启动时的配置文件: 

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-local-storage-1.jpg)

修改 docker 的存储目录:

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-local-storage-2.jpg)

修改(增加) `--graph` 即可。
