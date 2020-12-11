+++
title = "docker 原理之本地存储"
description = "docker 原理之本地存储"
date = "2020-12-09"
author = "russellgao"
draft = false
tags = [
    "docker"
]
+++

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

这篇文章以分析存储为主，涉及到的目录有 `image`,`containers`,`overlay2`，其他的目录放在后续的文章讨论。

在真正开始之前，先想想几个问题(这也是我自己问我自己的问题) :

- docker build 的过程是怎样的?
- docker pull 和 docker build 产生的镜像存放在哪了？
- docker run 运行一个容器的时候过程是怎么样的?

带着这些问题我们以一个例子进行说明 `russellgao/openresty:1.17.8.2-5-alpine`

### image
image 目录主要存放的镜像相关的信息，我们执行 `docker pull russellgao/openresty:1.17.8.2-5-alpine` 看看：
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# docker pull russellgao/openresty:1.17.8.2-5-alpine
1.17.8.2-5-alpine: Pulling from russellgao/openresty
df20fa9351a1: Already exists 
5682af42731d: Pull complete 
7c6cb2b54a9d: Pull complete 
aa74dc345098: Pull complete 
Digest: sha256:224ced85b5f8b679a8664a39b69c1b8feb09f8ba4343d834bd5b69433081389e
Status: Downloaded newer image for openresty/openresty:1.17.8.2-5-alpine
```

可以看到 pull 了 4 层下来了，我们看看 `image` 目录:
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# tree image 
image
└── overlay2
    ├── distribution
    │   ├── diffid-by-digest
    │   │   └── sha256
    │   │       ├── 5682af42731d652bd98d2456ed3da4f0595ed5d9e5b13ac8bb9590bb74f72eb8
    │   │       ├── 7c6cb2b54a9d9d40c4a03dd6615b1c8e791feb5d81464a7702a9bb921f7a73e9
    │   │       ├── aa74dc3450985aee599c181d650da8f8880ca1d6e2bc01a43831ca59b6e2a7b6
    │   │       └── df20fa9351a15782c64e6dddb2d4a6f50bf6d3688060a34c4014b0d9a752eb4c
    │   └── v2metadata-by-diffid
    │       └── sha256
    │           ├── 1680a9f16b18732726d0656b6d6ff9611a3c4460ca870827b537a87bbe10cc22
    │           ├── 50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a
    │           ├── 8521b614863046bf4bb604e3586feeca8b7ce1372f1d6664a5545e85ad9ca472
    │           └── 9c572ba82b91e3ac35c7351bdacc6876c67f5d9bc69c5e51e8b2deeafae95e4f
    ├── imagedb
    │   ├── content
    │   │   └── sha256
    │   │       └── 1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed
    │   └── metadata
    │       └── sha256
    │           └── 1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed
    │               └── lastUpdated
    ├── layerdb
    │   ├── mounts
    │   │   └── 9bd6ac07a8c962e2403203e1c45f4fb54733f9953cf318b34fc3f155bf2c0c59
    │   │       ├── init-id
    │   │       ├── mount-id
    │   │       └── parent
    │   ├── sha256
    │   │   ├── 228fb92e31891f472e9857ee11d13c404ff7c88e808b05ce4ebdc80d785d71f3
    │   │   │   ├── cache-id
    │   │   │   ├── diff
    │   │   │   ├── parent
    │   │   │   ├── size
    │   │   │   └── tar-split.json.gz
    │   │   ├── 50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a
    │   │   │   ├── cache-id
    │   │   │   ├── diff
    │   │   │   ├── size
    │   │   │   └── tar-split.json.gz
    │   │   ├── 5f72760956a669e4c9b33aa3f2f04baa84b0f4cf1e11676049981bafcbba74da
    │   │   │   ├── cache-id
    │   │   │   ├── diff
    │   │   │   ├── parent
    │   │   │   ├── size
    │   │   │   └── tar-split.json.gz
    │   │   └── fe267088885017d5e9a4621e68617a7f35e58dc2d0d747927882da21059854e3
    │   │       ├── cache-id
    │   │       ├── diff
    │   │       ├── parent
    │   │       ├── size
    │   │       └── tar-split.json.gz
    │   └── tmp
    └── repositories.json

21 directories, 33 files
```

看看 **repositories.json** 中是内容 :
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/repositories.json |  jq .
{
  "Repositories": {
    "openresty/openresty": {
      "openresty/openresty:1.17.8.2-5-alpine": "sha256:1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed",
      "openresty/openresty@sha256:224ced85b5f8b679a8664a39b69c1b8feb09f8ba4343d834bd5b69433081389e": "sha256:1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed"
    },
    "russellgao/openresty": {
      "russellgao/openresty:1.17.8.2-5-alpine": "sha256:1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed",
      "russellgao/openresty@sha256:84f53dc7517e9b6695fc8fd74916a1eb5970a92fc24a984f99bfb81508f3d261": "sha256:1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed"
    }
  }
}
```
**repositories.json** 中记录了这个机器上所有的镜像，可以看到这里有两个镜像 `openresty/openresty:1.17.8.2-5-alpine` 和 `russellgao/openresty:1.17.8.2-5-alpine` ，但其实只有一个镜像，因为后面的 `imageid` 是相同的，这个可以 `docker images` 验证一下
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# docker images 
REPOSITORY             TAG                 IMAGE ID            CREATED             SIZE
openresty/openresty    1.17.8.2-5-alpine   1ddc7a18ba0b        2 months ago        104MB
russellgao/openresty   1.17.8.2-5-alpine   1ddc7a18ba0b        2 months ago        104MB
```

`openresty/openresty:1.17.8.2-5-alpine` 和 `russellgao/openresty:1.17.8.2-5-alpine` 只是镜像 `1ddc7a18ba0b` 的 tag 。

那么 `1ddc7a18ba0b` 镜像是怎么组成的呢? `image/overlay2/` 下面除了 repositories.json 还有3个目录 `distribution`,`imagedb`,`layerdb`，作用分别如下: 

- distribution: 主要和镜像仓库的交互相关
- imagedb: 保存了镜像的元数据
- layerdb: 保存了镜像layer(层) 的数据

`image/overlay2/` 保存的是数据的链接，真正的镜像数据是存放在 `overlay2` 目录下，先看看 `distribution` :

### distribution

```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# tree  image/overlay2/distribution/
image/overlay2/distribution/
├── diffid-by-digest
│   └── sha256
│       ├── 5682af42731d652bd98d2456ed3da4f0595ed5d9e5b13ac8bb9590bb74f72eb8
│       ├── 7c6cb2b54a9d9d40c4a03dd6615b1c8e791feb5d81464a7702a9bb921f7a73e9
│       ├── aa74dc3450985aee599c181d650da8f8880ca1d6e2bc01a43831ca59b6e2a7b6
│       └── df20fa9351a15782c64e6dddb2d4a6f50bf6d3688060a34c4014b0d9a752eb4c
└── v2metadata-by-diffid
    └── sha256
        ├── 1680a9f16b18732726d0656b6d6ff9611a3c4460ca870827b537a87bbe10cc22
        ├── 50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a
        ├── 8521b614863046bf4bb604e3586feeca8b7ce1372f1d6664a5545e85ad9ca472
        └── 9c572ba82b91e3ac35c7351bdacc6876c67f5d9bc69c5e51e8b2deeafae95e4f

4 directories, 8 files
```
请注意看 `image/overlay2/distribution/diffid-by-digest/sha256` 下面，回过头再看看 docker pull 的过程，这里的就是 `digestid` ，docker pull 
的时候也是通过 `digestid` 实现的，这个id对应的是 `docker repository` 中的 `blob id`，在 `docker repository` 的 `blobs` 目录下可以找到。

可以查看具体的文件，如 `cat image/overlay2/distribution/diffid-by-digest/sha256/5682af42731d652bd98d2456ed3da4f0595ed5d9e5b13ac8bb9590bb74f72eb8 `
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/distribution/diffid-by-digest/sha256/5682af42731d652bd98d2456ed3da4f0595ed5d9e5b13ac8bb9590bb74f72eb8 
sha256:9c572ba82b91e3ac35c7351bdacc6876c67f5d9bc69c5e51e8b2deeafae95e4f
```

不难发现它们之间是相互引用的，可以实现 `diffid` 和 `digest` 的相互转换。

### imagedb
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# tree  image/overlay2/imagedb/
image/overlay2/imagedb/
├── content
│   └── sha256
│       └── 1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed
└── metadata
    └── sha256
        └── 1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed
            └── lastUpdated

5 directories, 2 files
```

可以看到 `imagedb` 是以镜像为单位进行存储的，看一下 `content` 下面的具体内容 :
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/imagedb/content/sha256/1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed |  jq .
{
  "architecture": "amd64",
  "config": {
    "Hostname": "",
    "Domainname": "",
    "User": "",
    "AttachStdin": false,
    "AttachStdout": false,
    "AttachStderr": false,
    "Tty": false,
    "OpenStdin": false,
    "StdinOnce": false,
    "Env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/openresty/luajit/bin:/usr/local/openresty/nginx/sbin:/usr/local/openresty/bin"
    ],
    "Cmd": [
      "/usr/local/openresty/bin/openresty",
      "-g",
      "daemon off;"
    ],
    "ArgsEscaped": true,
    "Image": "sha256:0b827067ad09ab8a0b9a73a45f5b1c408b84db1ca6883a4c544078ed43b8b5e3",
    "Volumes": null,
    "WorkingDir": "",
    "Entrypoint": null,
    "OnBuild": null,
    "Labels": {
      "maintainer": "Evan Wies <evan@neomantra.net>",
      "resty_add_package_builddeps": "",
      "resty_add_package_rundeps": "",
      "resty_config_deps": "--with-pcre     --with-cc-opt='-DNGX_LUA_ABORT_AT_PANIC -I/usr/local/openresty/pcre/include -I/usr/local/openresty/openssl/include'     --with-ld-opt='-L/usr/local/openresty/pcre/lib -L/usr/local/openresty/openssl/lib -Wl,-rpath,/usr/local/openresty/pcre/lib:/usr/local/openresty/openssl/lib'     ",
      "resty_config_options": "    --with-compat     --with-file-aio     --with-http_addition_module     --with-http_auth_request_module     --with-http_dav_module     --with-http_flv_module     --with-http_geoip_module=dynamic     --with-http_gunzip_module     --with-http_gzip_static_module     --with-http_image_filter_module=dynamic     --with-http_mp4_module     --with-http_random_index_module     --with-http_realip_module     --with-http_secure_link_module     --with-http_slice_module     --with-http_ssl_module     --with-http_stub_status_module     --with-http_sub_module     --with-http_v2_module     --with-http_xslt_module=dynamic     --with-ipv6     --with-mail     --with-mail_ssl_module     --with-md5-asm     --with-pcre-jit     --with-sha1-asm     --with-stream     --with-stream_ssl_module     --with-threads     ",
      "resty_config_options_more": "",
      "resty_eval_post_make": "",
      "resty_eval_pre_configure": "",
      "resty_image_base": "alpine",
      "resty_image_tag": "3.12",
      "resty_openssl_patch_version": "1.1.1f",
      "resty_openssl_url_base": "https://www.openssl.org/source",
      "resty_openssl_version": "1.1.1g",
      "resty_pcre_version": "8.44",
      "resty_version": "1.17.8.2"
    },
    "StopSignal": "SIGQUIT"
  },
  "container": "0ae35046dd1afef0f1f525360939abc524dbd469a92470c5836dfbb7dc666923",
  "container_config": {
    "Hostname": "0ae35046dd1a",
    "Domainname": "",
    "User": "",
    "AttachStdin": false,
    "AttachStdout": false,
    "AttachStderr": false,
    "Tty": false,
    "OpenStdin": false,
    "StdinOnce": false,
    "Env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/openresty/luajit/bin:/usr/local/openresty/nginx/sbin:/usr/local/openresty/bin"
    ],
    "Cmd": [
      "/bin/sh",
      "-c",
      "#(nop) ",
      "STOPSIGNAL SIGQUIT"
    ],
    "ArgsEscaped": true,
    "Image": "sha256:0b827067ad09ab8a0b9a73a45f5b1c408b84db1ca6883a4c544078ed43b8b5e3",
    "Volumes": null,
    "WorkingDir": "",
    "Entrypoint": null,
    "OnBuild": null,
    "Labels": {
      "maintainer": "Evan Wies <evan@neomantra.net>",
      "resty_add_package_builddeps": "",
      "resty_add_package_rundeps": "",
      "resty_config_deps": "--with-pcre     --with-cc-opt='-DNGX_LUA_ABORT_AT_PANIC -I/usr/local/openresty/pcre/include -I/usr/local/openresty/openssl/include'     --with-ld-opt='-L/usr/local/openresty/pcre/lib -L/usr/local/openresty/openssl/lib -Wl,-rpath,/usr/local/openresty/pcre/lib:/usr/local/openresty/openssl/lib'     ",
      "resty_config_options": "    --with-compat     --with-file-aio     --with-http_addition_module     --with-http_auth_request_module     --with-http_dav_module     --with-http_flv_module     --with-http_geoip_module=dynamic     --with-http_gunzip_module     --with-http_gzip_static_module     --with-http_image_filter_module=dynamic     --with-http_mp4_module     --with-http_random_index_module     --with-http_realip_module     --with-http_secure_link_module     --with-http_slice_module     --with-http_ssl_module     --with-http_stub_status_module     --with-http_sub_module     --with-http_v2_module     --with-http_xslt_module=dynamic     --with-ipv6     --with-mail     --with-mail_ssl_module     --with-md5-asm     --with-pcre-jit     --with-sha1-asm     --with-stream     --with-stream_ssl_module     --with-threads     ",
      "resty_config_options_more": "",
      "resty_eval_post_make": "",
      "resty_eval_pre_configure": "",
      "resty_image_base": "alpine",
      "resty_image_tag": "3.12",
      "resty_openssl_patch_version": "1.1.1f",
      "resty_openssl_url_base": "https://www.openssl.org/source",
      "resty_openssl_version": "1.1.1g",
      "resty_pcre_version": "8.44",
      "resty_version": "1.17.8.2"
    },
    "StopSignal": "SIGQUIT"
  },
  "created": "2020-09-18T16:25:11.080239395Z",
  "docker_version": "18.06.0-ce",
  "history": [
    {
      "created": "2020-05-29T21:19:46.192045972Z",
      "created_by": "/bin/sh -c #(nop) ADD file:c92c248239f8c7b9b3c067650954815f391b7bcb09023f984972c082ace2a8d0 in / "
    },
    {
      "created": "2020-05-29T21:19:46.363518345Z",
      "created_by": "/bin/sh -c #(nop)  CMD [\"/bin/sh\"]",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:11.417409263Z",
      "created_by": "/bin/sh -c #(nop)  LABEL maintainer=Evan Wies <evan@neomantra.net>",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:11.510209288Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_IMAGE_BASE=alpine",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:11.601623273Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_IMAGE_TAG=3.12",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:11.688966243Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_VERSION=1.17.8.2",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:11.783539793Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_OPENSSL_VERSION=1.1.1g",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:11.885734193Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_OPENSSL_PATCH_VERSION=1.1.1f",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:11.977916317Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_OPENSSL_URL_BASE=https://www.openssl.org/source",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.075117786Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_PCRE_VERSION=8.44",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.169065223Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_J=1",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.268734856Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_CONFIG_OPTIONS=    --with-compat     --with-file-aio     --with-http_addition_module     --with-http_auth_request_module     --with-http_dav_module     --with-http_flv_module     --with-http_geoip_module=dynamic     --with-http_gunzip_module     --with-http_gzip_static_module     --with-http_image_filter_module=dynamic     --with-http_mp4_module     --with-http_random_index_module     --with-http_realip_module     --with-http_secure_link_module     --with-http_slice_module     --with-http_ssl_module     --with-http_stub_status_module     --with-http_sub_module     --with-http_v2_module     --with-http_xslt_module=dynamic     --with-ipv6     --with-mail     --with-mail_ssl_module     --with-md5-asm     --with-pcre-jit     --with-sha1-asm     --with-stream     --with-stream_ssl_module     --with-threads     ",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.363332751Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_CONFIG_OPTIONS_MORE=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.462196367Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_LUAJIT_OPTIONS=--with-luajit-xcflags='-DLUAJIT_NUMMODE=2 -DLUAJIT_ENABLE_LUA52COMPAT'",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.553726712Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_ADD_PACKAGE_BUILDDEPS=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.644512619Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_ADD_PACKAGE_RUNDEPS=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.740127392Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_EVAL_PRE_CONFIGURE=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.833898538Z",
      "created_by": "/bin/sh -c #(nop)  ARG RESTY_EVAL_POST_MAKE=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:12.93159843Z",
      "created_by": "/bin/sh -c #(nop)  ARG _RESTY_CONFIG_DEPS=--with-pcre     --with-cc-opt='-DNGX_LUA_ABORT_AT_PANIC -I/usr/local/openresty/pcre/include -I/usr/local/openresty/openssl/include'     --with-ld-opt='-L/usr/local/openresty/pcre/lib -L/usr/local/openresty/openssl/lib -Wl,-rpath,/usr/local/openresty/pcre/lib:/usr/local/openresty/openssl/lib'     ",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.022542363Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_image_base=alpine",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.120036187Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_image_tag=3.12",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.20899948Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_version=1.17.8.2",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.292383125Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_openssl_version=1.1.1g",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.385097561Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_openssl_patch_version=1.1.1f",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.476173083Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_openssl_url_base=https://www.openssl.org/source",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.564110015Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_pcre_version=8.44",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.653688493Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_config_options=    --with-compat     --with-file-aio     --with-http_addition_module     --with-http_auth_request_module     --with-http_dav_module     --with-http_flv_module     --with-http_geoip_module=dynamic     --with-http_gunzip_module     --with-http_gzip_static_module     --with-http_image_filter_module=dynamic     --with-http_mp4_module     --with-http_random_index_module     --with-http_realip_module     --with-http_secure_link_module     --with-http_slice_module     --with-http_ssl_module     --with-http_stub_status_module     --with-http_sub_module     --with-http_v2_module     --with-http_xslt_module=dynamic     --with-ipv6     --with-mail     --with-mail_ssl_module     --with-md5-asm     --with-pcre-jit     --with-sha1-asm     --with-stream     --with-stream_ssl_module     --with-threads     ",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.747250902Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_config_options_more=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.839314208Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_config_deps=--with-pcre     --with-cc-opt='-DNGX_LUA_ABORT_AT_PANIC -I/usr/local/openresty/pcre/include -I/usr/local/openresty/openssl/include'     --with-ld-opt='-L/usr/local/openresty/pcre/lib -L/usr/local/openresty/openssl/lib -Wl,-rpath,/usr/local/openresty/pcre/lib:/usr/local/openresty/openssl/lib'     ",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:13.938461929Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_add_package_builddeps=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:14.023327305Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_add_package_rundeps=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:14.111176277Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_eval_pre_configure=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:18:14.211102965Z",
      "created_by": "/bin/sh -c #(nop)  LABEL resty_eval_post_make=",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:25:10.276243663Z",
      "created_by": "|16 RESTY_ADD_PACKAGE_BUILDDEPS= RESTY_ADD_PACKAGE_RUNDEPS= RESTY_CONFIG_OPTIONS=    --with-compat     --with-file-aio     --with-http_addition_module     --with-http_auth_request_module     --with-http_dav_module     --with-http_flv_module     --with-http_geoip_module=dynamic     --with-http_gunzip_module     --with-http_gzip_static_module     --with-http_image_filter_module=dynamic     --with-http_mp4_module     --with-http_random_index_module     --with-http_realip_module     --with-http_secure_link_module     --with-http_slice_module     --with-http_ssl_module     --with-http_stub_status_module     --with-http_sub_module     --with-http_v2_module     --with-http_xslt_module=dynamic     --with-ipv6     --with-mail     --with-mail_ssl_module     --with-md5-asm     --with-pcre-jit     --with-sha1-asm     --with-stream     --with-stream_ssl_module     --with-threads      RESTY_CONFIG_OPTIONS_MORE= RESTY_EVAL_POST_MAKE= RESTY_EVAL_PRE_CONFIGURE= RESTY_IMAGE_BASE=alpine RESTY_IMAGE_TAG=3.12 RESTY_J=1 RESTY_LUAJIT_OPTIONS=--with-luajit-xcflags='-DLUAJIT_NUMMODE=2 -DLUAJIT_ENABLE_LUA52COMPAT' RESTY_OPENSSL_PATCH_VERSION=1.1.1f RESTY_OPENSSL_URL_BASE=https://www.openssl.org/source RESTY_OPENSSL_VERSION=1.1.1g RESTY_PCRE_VERSION=8.44 RESTY_VERSION=1.17.8.2 _RESTY_CONFIG_DEPS=--with-pcre     --with-cc-opt='-DNGX_LUA_ABORT_AT_PANIC -I/usr/local/openresty/pcre/include -I/usr/local/openresty/openssl/include'     --with-ld-opt='-L/usr/local/openresty/pcre/lib -L/usr/local/openresty/openssl/lib -Wl,-rpath,/usr/local/openresty/pcre/lib:/usr/local/openresty/openssl/lib'      /bin/sh -c apk add --no-cache --virtual .build-deps         build-base         coreutils         curl         gd-dev         geoip-dev         libxslt-dev         linux-headers         make         perl-dev         readline-dev         zlib-dev         ${RESTY_ADD_PACKAGE_BUILDDEPS}     && apk add --no-cache         gd         geoip         libgcc         libxslt         zlib         ${RESTY_ADD_PACKAGE_RUNDEPS}     && cd /tmp     && if [ -n \"${RESTY_EVAL_PRE_CONFIGURE}\" ]; then eval $(echo ${RESTY_EVAL_PRE_CONFIGURE}); fi     && cd /tmp     && curl -fSL \"${RESTY_OPENSSL_URL_BASE}/openssl-${RESTY_OPENSSL_VERSION}.tar.gz\" -o openssl-${RESTY_OPENSSL_VERSION}.tar.gz     && tar xzf openssl-${RESTY_OPENSSL_VERSION}.tar.gz     && cd openssl-${RESTY_OPENSSL_VERSION}     && if [ $(echo ${RESTY_OPENSSL_VERSION} | cut -c 1-5) = \"1.1.1\" ] ; then         echo 'patching OpenSSL 1.1.1 for OpenResty'         && curl -s https://raw.githubusercontent.com/openresty/openresty/master/patches/openssl-${RESTY_OPENSSL_PATCH_VERSION}-sess_set_get_cb_yield.patch | patch -p1 ;     fi     && if [ $(echo ${RESTY_OPENSSL_VERSION} | cut -c 1-5) = \"1.1.0\" ] ; then         echo 'patching OpenSSL 1.1.0 for OpenResty'         && curl -s https://raw.githubusercontent.com/openresty/openresty/ed328977028c3ec3033bc25873ee360056e247cd/patches/openssl-1.1.0j-parallel_build_fix.patch | patch -p1         && curl -s https://raw.githubusercontent.com/openresty/openresty/master/patches/openssl-${RESTY_OPENSSL_PATCH_VERSION}-sess_set_get_cb_yield.patch | patch -p1 ;     fi     && ./config       no-threads shared zlib -g       enable-ssl3 enable-ssl3-method       --prefix=/usr/local/openresty/openssl       --libdir=lib       -Wl,-rpath,/usr/local/openresty/openssl/lib     && make -j${RESTY_J}     && make -j${RESTY_J} install_sw     && cd /tmp     && curl -fSL https://ftp.pcre.org/pub/pcre/pcre-${RESTY_PCRE_VERSION}.tar.gz -o pcre-${RESTY_PCRE_VERSION}.tar.gz     && tar xzf pcre-${RESTY_PCRE_VERSION}.tar.gz     && cd /tmp/pcre-${RESTY_PCRE_VERSION}     && ./configure         --prefix=/usr/local/openresty/pcre         --disable-cpp         --enable-jit         --enable-utf         --enable-unicode-properties     && make -j${RESTY_J}     && make -j${RESTY_J} install     && cd /tmp     && curl -fSL https://openresty.org/download/openresty-${RESTY_VERSION}.tar.gz -o openresty-${RESTY_VERSION}.tar.gz     && tar xzf openresty-${RESTY_VERSION}.tar.gz     && cd /tmp/openresty-${RESTY_VERSION}     && eval ./configure -j${RESTY_J} ${_RESTY_CONFIG_DEPS} ${RESTY_CONFIG_OPTIONS} ${RESTY_CONFIG_OPTIONS_MORE} ${RESTY_LUAJIT_OPTIONS}     && make -j${RESTY_J}     && make -j${RESTY_J} install     && cd /tmp     && if [ -n \"${RESTY_EVAL_POST_MAKE}\" ]; then eval $(echo ${RESTY_EVAL_POST_MAKE}); fi     && rm -rf         openssl-${RESTY_OPENSSL_VERSION}.tar.gz openssl-${RESTY_OPENSSL_VERSION}         pcre-${RESTY_PCRE_VERSION}.tar.gz pcre-${RESTY_PCRE_VERSION}         openresty-${RESTY_VERSION}.tar.gz openresty-${RESTY_VERSION}     && apk del .build-deps     && mkdir -p /var/run/openresty     && ln -sf /dev/stdout /usr/local/openresty/nginx/logs/access.log     && ln -sf /dev/stderr /usr/local/openresty/nginx/logs/error.log"
    },
    {
      "created": "2020-09-18T16:25:10.712994475Z",
      "created_by": "/bin/sh -c #(nop)  ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/openresty/luajit/bin:/usr/local/openresty/nginx/sbin:/usr/local/openresty/bin",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:25:10.806730628Z",
      "created_by": "/bin/sh -c #(nop) COPY file:871e3c814ada8b73d3bd53e819bd122b5612587624e3eb6ef6e97d83522238fc in /usr/local/openresty/nginx/conf/nginx.conf "
    },
    {
      "created": "2020-09-18T16:25:10.8995482Z",
      "created_by": "/bin/sh -c #(nop) COPY file:1832501c6083278533ce3d09a4140cc30795ddf825ad6a0ad52ea84858291e53 in /etc/nginx/conf.d/default.conf "
    },
    {
      "created": "2020-09-18T16:25:10.984062974Z",
      "created_by": "/bin/sh -c #(nop)  CMD [\"/usr/local/openresty/bin/openresty\" \"-g\" \"daemon off;\"]",
      "empty_layer": true
    },
    {
      "created": "2020-09-18T16:25:11.080239395Z",
      "created_by": "/bin/sh -c #(nop)  STOPSIGNAL SIGQUIT",
      "empty_layer": true
    }
  ],
  "os": "linux",
  "rootfs": {
    "type": "layers",
    "diff_ids": [
      "sha256:50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a",
      "sha256:9c572ba82b91e3ac35c7351bdacc6876c67f5d9bc69c5e51e8b2deeafae95e4f",
      "sha256:1680a9f16b18732726d0656b6d6ff9611a3c4460ca870827b537a87bbe10cc22",
      "sha256:8521b614863046bf4bb604e3586feeca8b7ce1372f1d6664a5545e85ad9ca472"
    ]
  }
}
```

可以看到这个里面是保存了镜像的元信息，这是再执行一下 `docker inspect 1ddc7a18ba0b ` ,会发现它们的输出是出奇的相似 :
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# docker inspect 1ddc7a18ba0b 
[
    {
        "Id": "sha256:1ddc7a18ba0bcc20c61447f391bfff98ac559eea590e7ac59b5b5f588f1f47ed",
        "RepoTags": [
            "openresty/openresty:1.17.8.2-5-alpine",
            "russellgao/openresty:1.17.8.2-5-alpine"
        ],
        "RepoDigests": [
            "openresty/openresty@sha256:224ced85b5f8b679a8664a39b69c1b8feb09f8ba4343d834bd5b69433081389e",
            "russellgao/openresty@sha256:84f53dc7517e9b6695fc8fd74916a1eb5970a92fc24a984f99bfb81508f3d261"
        ],
        "Parent": "",
        "Comment": "",
        "Created": "2020-09-18T16:25:11.080239395Z",
        "Container": "0ae35046dd1afef0f1f525360939abc524dbd469a92470c5836dfbb7dc666923",
        "ContainerConfig": {
            "Hostname": "0ae35046dd1a",
            "Domainname": "",
            "User": "",
            "AttachStdin": false,
            "AttachStdout": false,
            "AttachStderr": false,
            "Tty": false,
            "OpenStdin": false,
            "StdinOnce": false,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/openresty/luajit/bin:/usr/local/openresty/nginx/sbin:/usr/local/openresty/bin"
            ],
            "Cmd": [
                "/bin/sh",
                "-c",
                "#(nop) ",
                "STOPSIGNAL SIGQUIT"
            ],
            "ArgsEscaped": true,
            "Image": "sha256:0b827067ad09ab8a0b9a73a45f5b1c408b84db1ca6883a4c544078ed43b8b5e3",
            "Volumes": null,
            "WorkingDir": "",
            "Entrypoint": null,
            "OnBuild": null,
            "Labels": {
                "maintainer": "Evan Wies <evan@neomantra.net>",
                "resty_add_package_builddeps": "",
                "resty_add_package_rundeps": "",
                "resty_config_deps": "--with-pcre     --with-cc-opt='-DNGX_LUA_ABORT_AT_PANIC -I/usr/local/openresty/pcre/include -I/usr/local/openresty/openssl/include'     --with-ld-opt='-L/usr/local/openresty/pcre/lib -L/usr/local/openresty/openssl/lib -Wl,-rpath,/usr/local/openresty/pcre/lib:/usr/local/openresty/openssl/lib'     ",
                "resty_config_options": "    --with-compat     --with-file-aio     --with-http_addition_module     --with-http_auth_request_module     --with-http_dav_module     --with-http_flv_module     --with-http_geoip_module=dynamic     --with-http_gunzip_module     --with-http_gzip_static_module     --with-http_image_filter_module=dynamic     --with-http_mp4_module     --with-http_random_index_module     --with-http_realip_module     --with-http_secure_link_module     --with-http_slice_module     --with-http_ssl_module     --with-http_stub_status_module     --with-http_sub_module     --with-http_v2_module     --with-http_xslt_module=dynamic     --with-ipv6     --with-mail     --with-mail_ssl_module     --with-md5-asm     --with-pcre-jit     --with-sha1-asm     --with-stream     --with-stream_ssl_module     --with-threads     ",
                "resty_config_options_more": "",
                "resty_eval_post_make": "",
                "resty_eval_pre_configure": "",
                "resty_image_base": "alpine",
                "resty_image_tag": "3.12",
                "resty_openssl_patch_version": "1.1.1f",
                "resty_openssl_url_base": "https://www.openssl.org/source",
                "resty_openssl_version": "1.1.1g",
                "resty_pcre_version": "8.44",
                "resty_version": "1.17.8.2"
            },
            "StopSignal": "SIGQUIT"
        },
        "DockerVersion": "18.06.0-ce",
        "Author": "",
        "Config": {
            "Hostname": "",
            "Domainname": "",
            "User": "",
            "AttachStdin": false,
            "AttachStdout": false,
            "AttachStderr": false,
            "Tty": false,
            "OpenStdin": false,
            "StdinOnce": false,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/openresty/luajit/bin:/usr/local/openresty/nginx/sbin:/usr/local/openresty/bin"
            ],
            "Cmd": [
                "/usr/local/openresty/bin/openresty",
                "-g",
                "daemon off;"
            ],
            "ArgsEscaped": true,
            "Image": "sha256:0b827067ad09ab8a0b9a73a45f5b1c408b84db1ca6883a4c544078ed43b8b5e3",
            "Volumes": null,
            "WorkingDir": "",
            "Entrypoint": null,
            "OnBuild": null,
            "Labels": {
                "maintainer": "Evan Wies <evan@neomantra.net>",
                "resty_add_package_builddeps": "",
                "resty_add_package_rundeps": "",
                "resty_config_deps": "--with-pcre     --with-cc-opt='-DNGX_LUA_ABORT_AT_PANIC -I/usr/local/openresty/pcre/include -I/usr/local/openresty/openssl/include'     --with-ld-opt='-L/usr/local/openresty/pcre/lib -L/usr/local/openresty/openssl/lib -Wl,-rpath,/usr/local/openresty/pcre/lib:/usr/local/openresty/openssl/lib'     ",
                "resty_config_options": "    --with-compat     --with-file-aio     --with-http_addition_module     --with-http_auth_request_module     --with-http_dav_module     --with-http_flv_module     --with-http_geoip_module=dynamic     --with-http_gunzip_module     --with-http_gzip_static_module     --with-http_image_filter_module=dynamic     --with-http_mp4_module     --with-http_random_index_module     --with-http_realip_module     --with-http_secure_link_module     --with-http_slice_module     --with-http_ssl_module     --with-http_stub_status_module     --with-http_sub_module     --with-http_v2_module     --with-http_xslt_module=dynamic     --with-ipv6     --with-mail     --with-mail_ssl_module     --with-md5-asm     --with-pcre-jit     --with-sha1-asm     --with-stream     --with-stream_ssl_module     --with-threads     ",
                "resty_config_options_more": "",
                "resty_eval_post_make": "",
                "resty_eval_pre_configure": "",
                "resty_image_base": "alpine",
                "resty_image_tag": "3.12",
                "resty_openssl_patch_version": "1.1.1f",
                "resty_openssl_url_base": "https://www.openssl.org/source",
                "resty_openssl_version": "1.1.1g",
                "resty_pcre_version": "8.44",
                "resty_version": "1.17.8.2"
            },
            "StopSignal": "SIGQUIT"
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 103896354,
        "VirtualSize": 103896354,
        "GraphDriver": {
            "Data": {
                "LowerDir": "/var/lib/docker/overlay2/00b65b9c288df8c0ae7cdacba531a7dc5cb006e6c768e19ee36055717b782acc/diff:/var/lib/docker/overlay2/f1cf8b173467c98e08f3d276d7ccd8f9892c7c71dec2c4b335c39c6f175ae744/diff:/var/lib/docker/overlay2/8cbfb8b74c887e780747c8e6f4b3b9223a513ff6d69770bac16abb76da4e314f/diff",
                "MergedDir": "/var/lib/docker/overlay2/5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4/merged",
                "UpperDir": "/var/lib/docker/overlay2/5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4/diff",
                "WorkDir": "/var/lib/docker/overlay2/5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4/work"
            },
            "Name": "overlay2"
        },
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a",
                "sha256:9c572ba82b91e3ac35c7351bdacc6876c67f5d9bc69c5e51e8b2deeafae95e4f",
                "sha256:1680a9f16b18732726d0656b6d6ff9611a3c4460ca870827b537a87bbe10cc22",
                "sha256:8521b614863046bf4bb604e3586feeca8b7ce1372f1d6664a5545e85ad9ca472"
            ]
        },
        "Metadata": {
            "LastTagTime": "2020-11-11T13:35:12.051705855+08:00"
        }
    }
]
```
我自己的理解，docker inspect 执行时就是读取 `image/overlay2/imagedb/content` 中的内容加工之后输出的，这里面有些内容可以仔细理解一下 :

- 

## 参考
- https://segmentfault.com/a/1190000017579626



