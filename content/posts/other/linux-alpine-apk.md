+++
title = "Alpine 容器内安装命令时遇到坑"
description = "Alpine 容器内安装命令时遇到坑"
date = "2021-02-19"
aliases = ["Alpine 容器内安装命令时遇到坑"]
author = "russellgao"
draft = false
tags = [
    "linux",
    "alpine",
    "apk"
]
+++


## 导读
> 记录在 Alpine 容器内安装命令时遇到的一些问题，本篇文章会持续更新。
>
> 问题背景是在docker 容器内执行 docker 命令，执行时发现缺少某些依赖包，在安装依赖包时遇到一些难以解决的问题。

## 在容器内执行 docker 命令
在 docker 容器执行 docker 命令，如启动新的容器，需要把主机的 docker sock 套接字映射到容器内 。 具体方法为: 
```shell script
docker run -v /usr/bin/docker:/bin/docker \
  -v /var/run/docker.sock:/var/run/docker.sock \
   xxx
```

## error while loading shared libraries: libltdl.so.7
如果执行 docker 命令报错如下:
```shell script
error while loading shared libraries: libltdl.so.7: cannot open shared object file: No such file or directory
```

说明缺少对应的依赖库，安装方法为 :
```shell script
apk add --no-cache libltdl
```

如果是 Centos 容器:
```shell script
yum install libtool-ltdl -y
```

如果是 Ubantu 容器:
```shell script
sudo apt-get update
sudo apt-get install libltdl-dev
```

## 2 errors; 50 MiB in 38 packages
如果安装 `libltdl` 时报错如下：

```shell script
apk add --no-cache libltdl 
fetch http://mirrors.ustc.edu.cn/alpine/v3.4/main/x86_64/APKINDEX.tar.gz
fetch http://mirrors.ustc.edu.cn/alpine/v3.4/community/x86_64/APKINDEX.tar.gz
2 errors; 50 MiB in 38 packages
```

说明没有安装成功，需要继续定位错误方法。这时候可以执行 `apk update` 更新一下本地索引 :
```shell script
apk update
fetch http://mirrors.ustc.edu.cn/alpine/v3.4/main/x86_64/APKINDEX.tar.gz
ERROR: http://mirrors.ustc.edu.cn/alpine/v3.4/main: Bad file descriptor
WARNING: Ignoring APKINDEX.0d9a6724.tar.gz: Bad file descriptor
fetch http://mirrors.ustc.edu.cn/alpine/v3.4/community/x86_64/APKINDEX.tar.gz
ERROR: http://mirrors.ustc.edu.cn/alpine/v3.4/community: Bad file descriptor
WARNING: Ignoring APKINDEX.6a82a2a6.tar.gz: Bad file descriptor
2 errors; 38 distinct packages available
```

可以看到又报错了，这个错误说明文件描述符有问题 ，解决方法删除本地缓存目录并重新创建即可 :
```shell script
rm -fr /var/cache/apk
mkdir -p mkdir /var/cache/apk
```

这时候再执行 `apk update ` 就可以了
```shell script
apk update -v 
fetch http://mirrors.ustc.edu.cn/alpine/v3.4/main/x86_64/APKINDEX.tar.gz
fetch http://mirrors.ustc.edu.cn/alpine/v3.4/community/x86_64/APKINDEX.tar.gz
v3.4.6-316-g63ea6d0 [http://mirrors.ustc.edu.cn/alpine/v3.4/main]
v3.4.6-160-g14ad2a3 [http://mirrors.ustc.edu.cn/alpine/v3.4/community]
OK: 5984 distinct packages available
```

再次执行 `apk add --no-cache libltdl` 如果还是报错则可以执行 `apk fix` 进行修复 :
```shell script
apk fix  
(1/2) Reinstalling busybox (1.24.2-r14)
Executing busybox-1.24.2-r14.post-upgrade
(2/2) [APK unavailable, skipped] Reinstalling glibc-bin (2.25-r0)
Executing busybox-1.24.2-r14.trigger
1 errors; 164 MiB in 56 packages
bash-4.3# 
bash-4.3# apk fix  -v
(1/1) [APK unavailable, skipped] Reinstalling glibc-bin (2.25-r0)
1 errors; 56 packages, 333 dirs, 7131 files, 164 MiB
```
从上面的信息可以看出，在 `fix` 阶段 fix `glibc-bin` 失败了，那就需要手动删除再重新安装了。
```shell script
apk del  glibc-bin 
World updated, but the following packages are not removed due to:
  glibc-bin: glibc-i18n

1 errors; 164 MiB in 56 packages
```

可以如果要删除 `glibc-bin ` 需要先删除 `glibc-i18n` 

```shell script
apk del  glibc-i18n 
(1/2) Purging glibc-i18n (2.25-r0)
(2/2) Purging glibc-bin (2.25-r0)
OK: 151 MiB in 54 packages

apk del  glibc-bin 
```

这时候重新 `fix` :
```shell script
apk fix  -v
OK: 54 packages, 256 dirs, 6543 files, 151 MiB
```

再次安装 `libltdl `
```shell script
apk add -v --no-cache libltdl 
fetch http://mirrors.ustc.edu.cn/alpine/v3.4/main/x86_64/APKINDEX.tar.gz
fetch http://mirrors.ustc.edu.cn/alpine/v3.4/community/x86_64/APKINDEX.tar.gz
OK: 54 packages, 256 dirs, 6543 files, 151 MiB
```

可以看到问题完美解决 。

## 总结
记录在 alpine 容器内安装库时遇到的坑，此篇文章持续更新 。

