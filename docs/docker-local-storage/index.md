# docker 原理之本地存储


## 导读
> 在前面的文章[docker 原理之存储驱动](../docker-storage)中简单的介绍了 Docker 的存储驱动，这篇文章接着讲存储，目前的 docker 版本中默认的是 `overlay2` ，所以这篇文章就以 `overlay2` 为例带大家看看，在我们执行 `docker build` ，`docker pull`，`docker run` 等命令时本地存储有何变化。
> 这篇文章比较长，如果看不完可以收藏起来后续需要用到的时候再查阅，称的上是干货满满，作者自己整理也花了较长的时间。

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
我自己的理解，docker inspect 执行时就是读取 `image/overlay2/imagedb/content` 中的内容加工之后输出的，这里面有些内容可以仔细理解一下(从上往下看) :

- **config:** 后续如果根据这个镜像启动容器时，config 中的内容就是容器的默认参数，
- **container:** 此处是一个容器ID，是在 `docker build` 阶段用于生成镜像的容器，此处可以简单介绍下 `docker build` 的过程：
    - 根据 Dockerfile 的指令，按理说每个指令就是一层，但实际情况并非如此哟，这里分两种情况讨论:
        - 形如 `RUN`、`ADD` 指令，会造成文件系统改变的指令，会生成新的层
        - 形如 `LABEL`、`ENV`、`CMD` 指令，这类指令不会造成文件系统的改变，只会改变镜像的配置，具体来说就是会改变 `config` 的值，会直接修改配置，不会生成新的层。
    - 如果指令需要生成新的层，则根据上一层产生的镜像启动一个新的容器运行这个指令，正常运行结束以后会 `docker commit` 成一个新的镜像
    - 所以这个 `container` 就是刚刚起的容器的ID，后面会用一个例子说明。
- **container_config:** 用来生成这层镜像的容器的配置，换言之就是上述 `container` 的配置，可以看到 `config` 和 `container_config` 配置一致。
- **created:** 镜像的生成时间
- **docker_version:** `docker build` 的执行环境
- **history:**  镜像的构建历史(包含所有的历史执行指令)。
- **rootfs:** 镜像所有包含所有层的 `diff_id` ,顺序从上往下按照 `layer` 的顺序排列。**这里需要特别注意一下，rootfs 中存的是 diff_id，后面会一步一步解释如何和真正 layer 关联起来**

### layerdb
前面我们说过，`imagedb` 存的是元数据，那么 `layerdb` 应该存的是 layer 相关信息?先看看这个目录下面有什么: 
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# ll  image/overlay2/layerdb/
总用量 12
drwxr-xr-x 3 root root 4096 12月  2 09:25 mounts
drwxr-xr-x 6 root root 4096 11月 11 13:32 sha256
drwxr-xr-x 2 root root 4096 11月 11 13:32 tmp
```

#### tmp
tmp 是一个临时目录

#### sha256

sha256: 先看看这个下面有什么 `ll  image/overlay2/layerdb/sha256/`
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# ll  image/overlay2/layerdb/sha256/
总用量 16
drwx------ 2 root root 4096 11月 11 13:32 228fb92e31891f472e9857ee11d13c404ff7c88e808b05ce4ebdc80d785d71f3
drwx------ 2 root root 4096 11月 11 13:31 50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a
drwx------ 2 root root 4096 11月 11 13:32 5f72760956a669e4c9b33aa3f2f04baa84b0f4cf1e11676049981bafcbba74da
drwx------ 2 root root 4096 11月 11 13:32 fe267088885017d5e9a4621e68617a7f35e58dc2d0d747927882da21059854e3
```
咋一看这里和 `rootfs` 中的 `diff_id` 并不相同，只有一层是一样的(只有base layer是相同)。这里的是 `chain_id` ，那么什么是 `chain_id`呢？

- diff_id: 描述的是某一层的变化
- chain_id: 描述的是一系列变化

diff_id 和 chain_id 的计算公式为:
```shell script
ChainID(A) = DiffID(A)
ChainID(A | B) = Digest(ChainID(A) + " " + DiffID(B))
ChainID(A | B | C) = Digest(ChainID(A | B) + " " + DiffID(C))
```
是不是有点绕，回到我们的例子看看：
rootfs 中的 diff_id 为:
```shell script
"diff_ids": [
  "sha256:50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a",
  "sha256:9c572ba82b91e3ac35c7351bdacc6876c67f5d9bc69c5e51e8b2deeafae95e4f",
  "sha256:1680a9f16b18732726d0656b6d6ff9611a3c4460ca870827b537a87bbe10cc22",
  "sha256:8521b614863046bf4bb604e3586feeca8b7ce1372f1d6664a5545e85ad9ca472"
]
```
chain_id 为:
```shell script
drwx------ 2 root root 4096 11月 11 13:32 228fb92e31891f472e9857ee11d13c404ff7c88e808b05ce4ebdc80d785d71f3
drwx------ 2 root root 4096 11月 11 13:31 50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a
drwx------ 2 root root 4096 11月 11 13:32 5f72760956a669e4c9b33aa3f2f04baa84b0f4cf1e11676049981bafcbba74da
drwx------ 2 root root 4096 11月 11 13:32 fe267088885017d5e9a4621e68617a7f35e58dc2d0d747927882da21059854e3
```
根据上面的公式 base layer 的 diff_id 和 chain_id 是相同的:
```shell script
50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a -> 50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a
```
在继续看看下面的算法
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# echo -n "sha256:50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a sha256:9c572ba82b91e3ac35c7351bdacc6876c67f5d9bc69c5e51e8b2deeafae95e4f" | sha256sum
fe267088885017d5e9a4621e68617a7f35e58dc2d0d747927882da21059854e3  -
[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# echo -n "sha256:fe267088885017d5e9a4621e68617a7f35e58dc2d0d747927882da21059854e3 sha256:1680a9f16b18732726d0656b6d6ff9611a3c4460ca870827b537a87bbe10cc22" | sha256sum
5f72760956a669e4c9b33aa3f2f04baa84b0f4cf1e11676049981bafcbba74da  -
[root@iZuf685opgs9oyozju9i2bZ docker]# echo -n "sha256:5f72760956a669e4c9b33aa3f2f04baa84b0f4cf1e11676049981bafcbba74da sha256:8521b614863046bf4bb604e3586feeca8b7ce1372f1d6664a5545e85ad9ca472" | sha256sum
228fb92e31891f472e9857ee11d13c404ff7c88e808b05ce4ebdc80d785d71f3  -
```
这么一演算就事情就变的清晰起来了:
```shell script
50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a -> 50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a
9c572ba82b91e3ac35c7351bdacc6876c67f5d9bc69c5e51e8b2deeafae95e4f -> fe267088885017d5e9a4621e68617a7f35e58dc2d0d747927882da21059854e3
1680a9f16b18732726d0656b6d6ff9611a3c4460ca870827b537a87bbe10cc22 -> 5f72760956a669e4c9b33aa3f2f04baa84b0f4cf1e11676049981bafcbba74da
8521b614863046bf4bb604e3586feeca8b7ce1372f1d6664a5545e85ad9ca472 -> 228fb92e31891f472e9857ee11d13c404ff7c88e808b05ce4ebdc80d785d71f3
```

理清它们之间的关系就比较好办了，在看看 chain_id 目录下都有什么:
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# tree image/overlay2/layerdb/sha256/
image/overlay2/layerdb/sha256/
├── 228fb92e31891f472e9857ee11d13c404ff7c88e808b05ce4ebdc80d785d71f3
│   ├── cache-id
│   ├── diff
│   ├── parent
│   ├── size
│   └── tar-split.json.gz
├── 50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a
│   ├── cache-id
│   ├── diff
│   ├── size
│   └── tar-split.json.gz
├── 5f72760956a669e4c9b33aa3f2f04baa84b0f4cf1e11676049981bafcbba74da
│   ├── cache-id
│   ├── diff
│   ├── parent
│   ├── size
│   └── tar-split.json.gz
└── fe267088885017d5e9a4621e68617a7f35e58dc2d0d747927882da21059854e3
    ├── cache-id
    ├── diff
    ├── parent
    ├── size
    └── tar-split.json.gz

4 directories, 19 files
```
- cache-id: 保存的是真正的 layer id 信息，可以看看:
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/layerdb/sha256/50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a/cache-id 
8cbfb8b74c887e780747c8e6f4b3b9223a513ff6d69770bac16abb76da4e314f[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# ll overlay2/
总用量 28
drwx------ 4 root root 4096 11月 11 13:32 00b65b9c288df8c0ae7cdacba531a7dc5cb006e6c768e19ee36055717b782acc
drwx------ 5 root root 4096 12月  2 09:25 1e53dddb1a0bb04ee4ebd24a8edb94b96e2fd471a72bf1b8608096b38cb16646
drwx------ 4 root root 4096 12月  2 09:25 1e53dddb1a0bb04ee4ebd24a8edb94b96e2fd471a72bf1b8608096b38cb16646-init
drwx------ 4 root root 4096 11月 11 13:48 5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4
drwx------ 3 root root 4096 11月 11 13:32 8cbfb8b74c887e780747c8e6f4b3b9223a513ff6d69770bac16abb76da4e314f
drwx------ 4 root root 4096 11月 11 13:32 f1cf8b173467c98e08f3d276d7ccd8f9892c7c71dec2c4b335c39c6f175ae744
drwx------ 2 root root 4096 12月  2 09:25 l
```
可以看到 cache-id 中的内容是可以和 `overlay2` 目录中的内容可以对应起来，overlay2 中的内容等会详细介绍。
- diff: 该层的 diff_id ，可以和上面的计算对应着看
- size: 该层的大小，单位为字节，看看这个镜像每层的大小信息: 
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/layerdb/sha256/50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a/size 
5574537[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/layerdb/sha256/fe267088885017d5e9a4621e68617a7f35e58dc2d0d747927882da21059854e3/size 
98318464[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/layerdb/sha256/5f72760956a669e4c9b33aa3f2f04baa84b0f4cf1e11676049981bafcbba74da/size 
1762[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/layerdb/sha256/228fb92e31891f472e9857ee11d13c404ff7c88e808b05ce4ebdc80d785d71f3/size 
1591[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# docker images 
REPOSITORY             TAG                 IMAGE ID            CREATED             SIZE
openresty/openresty    1.17.8.2-5-alpine   1ddc7a18ba0b        2 months ago        104MB
russellgao/openresty   1.17.8.2-5-alpine   1ddc7a18ba0b        2 months ago        104MB
```
total = ceil((5574537 + 98318464 + 1762 + 1591) / 1000 + 1000)

可以看到和 docker images 中的 size 是一样的
- parent: 除了 base 层之外，其余每个层都有 parent 这个文件，这个文件保存了上一层的 chain_id
- tar-split.json.gz: layer 层数据 tar 压缩包的 split 文件，该文件生成需要 [tar-split](https://github.com/vbatts/tar-split),通过它可以还原 layer 的 tar 包。

#### mounts
mounts 从名字就可以看出来挂载，没错，这里就是保存了容器的挂载信息，看看下面的命令输出: 
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# docker ps -a 
CONTAINER ID        IMAGE                                    COMMAND                  CREATED             STATUS              PORTS                                      NAMES
9bd6ac07a8c9        russellgao/openresty:1.17.8.2-5-alpine   "/usr/local/openrest…"   10 days ago         Up 2 days           0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp   openresty-app-1
[root@iZuf685opgs9oyozju9i2bZ docker]# ll containers/
总用量 4
drwx------ 4 root root 4096 12月 12 09:56 9bd6ac07a8c962e2403203e1c45f4fb54733f9953cf318b34fc3f155bf2c0c59
[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/layerdb/mounts/9bd6ac07a8c962e2403203e1c45f4fb54733f9953cf318b34fc3f155bf2c0c59/init-id 
1e53dddb1a0bb04ee4ebd24a8edb94b96e2fd471a72bf1b8608096b38cb16646-init[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/layerdb/mounts/9bd6ac07a8c962e2403203e1c45f4fb54733f9953cf318b34fc3f155bf2c0c59/mount-id 
1e53dddb1a0bb04ee4ebd24a8edb94b96e2fd471a72bf1b8608096b38cb16646[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# cat image/overlay2/layerdb/mounts/9bd6ac07a8c962e2403203e1c45f4fb54733f9953cf318b34fc3f155bf2c0c59/parent 
sha256:228fb92e31891f472e9857ee11d13c404ff7c88e808b05ce4ebdc80d785d71f3[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# ll overlay2/
总用量 28
drwx------ 4 root root 4096 11月 11 13:32 00b65b9c288df8c0ae7cdacba531a7dc5cb006e6c768e19ee36055717b782acc
drwx------ 5 root root 4096 12月  2 09:25 1e53dddb1a0bb04ee4ebd24a8edb94b96e2fd471a72bf1b8608096b38cb16646
drwx------ 4 root root 4096 12月  2 09:25 1e53dddb1a0bb04ee4ebd24a8edb94b96e2fd471a72bf1b8608096b38cb16646-init
drwx------ 4 root root 4096 11月 11 13:48 5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4
drwx------ 3 root root 4096 11月 11 13:32 8cbfb8b74c887e780747c8e6f4b3b9223a513ff6d69770bac16abb76da4e314f
drwx------ 4 root root 4096 11月 11 13:32 f1cf8b173467c98e08f3d276d7ccd8f9892c7c71dec2c4b335c39c6f175ae744
drwx------ 2 root root 4096 12月  2 09:25 l
```
可以看出来， mounts 保存了容器的镜像的挂载信息，内容是具体的 `layer id` 
>**这里需要理解一下，这里的挂载指的是挂载容器的镜像层，和 `docker run` 时 `-v` 挂载是没有关系**
> 简单理解「容器=镜像+读写层」，镜像=「layer1 + layer2 + ... + layern」的叠加，这里挂载的所有layer 叠加之后的只读层。

到这里 `image` 目录就介绍结束了，接下来再看看 `overlay2` 目录 。

### overlay2
overlay2 目录存放的每一层的具体数据，先看看目录结构:

```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# tree overlay2/ -L 2
[root@iZuf685opgs9oyozju9i2bZ docker]# tree -L 2 overlay2/
overlay2/
├── 00b65b9c288df8c0ae7cdacba531a7dc5cb006e6c768e19ee36055717b782acc
│   ├── committed
│   ├── diff
│   ├── link
│   ├── lower
│   └── work
├── 5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4
│   ├── committed
│   ├── diff
│   ├── link
│   ├── lower
│   └── work
├── 8cbfb8b74c887e780747c8e6f4b3b9223a513ff6d69770bac16abb76da4e314f
│   ├── committed
│   ├── diff
│   └── link
├── b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc
│   ├── diff
│   ├── link
│   ├── lower
│   ├── merged
│   └── work
├── b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc-init
│   ├── committed
│   ├── diff
│   ├── link
│   ├── lower
│   └── work
├── f1cf8b173467c98e08f3d276d7ccd8f9892c7c71dec2c4b335c39c6f175ae744
│   ├── committed
│   ├── diff
│   ├── link
│   ├── lower
│   └── work
└── l
    ├── 2NFRHNZBFYCUAPMTFCKUR5R4DS -> ../b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc/diff
    ├── 33RV26M4VMX3ZUISOG26USXBKR -> ../f1cf8b173467c98e08f3d276d7ccd8f9892c7c71dec2c4b335c39c6f175ae744/diff
    ├── BGEYC7V6ULKFOOIITWCEKITQEU -> ../b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc-init/diff
    ├── HG76ICE67NTXFL7AYXCMI3EK4Y -> ../00b65b9c288df8c0ae7cdacba531a7dc5cb006e6c768e19ee36055717b782acc/diff
    ├── L5XCYQVZ6DOSLJNP6HXCZQZ7A5 -> ../5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4/diff
    └── MUHXHRXFSGNCBKQ2AUXDFOUDLF -> ../8cbfb8b74c887e780747c8e6f4b3b9223a513ff6d69770bac16abb76da4e314f/diff

25 directories, 16 files
```

可以看到 overlay2 一级目录下有个特殊目录 `l` , `l` 下是各个layer 软链接，防止mount 命令太长而发生错误，所以就用短链接了。

细心的你一定发现了这么几个问题:

- 这个镜像只有 4 个层，这里为啥会有 6 个层(目录)
- 为啥具体layer 下的目录/文件结构不一样
- 有的 layer 为啥带了 `-init` 后缀，有的没有

有 6 个layer 层是因为我这里启动了一个容器，会生成两个层(读写层和这个镜像merged之后的只读层)，删除容器之后看看:
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# docker rm -f openresty-app-1 
openresty-app-1
[root@iZuf685opgs9oyozju9i2bZ docker]# ll overlay2/
总用量 20
drwx------ 4 root root 4096 11月 11 13:32 00b65b9c288df8c0ae7cdacba531a7dc5cb006e6c768e19ee36055717b782acc
drwx------ 4 root root 4096 11月 11 13:48 5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4
drwx------ 3 root root 4096 11月 11 13:32 8cbfb8b74c887e780747c8e6f4b3b9223a513ff6d69770bac16abb76da4e314f
drwx------ 4 root root 4096 11月 11 13:32 f1cf8b173467c98e08f3d276d7ccd8f9892c7c71dec2c4b335c39c6f175ae744
drwx------ 2 root root 4096 12月 12 13:29 l
```

这下和之前讨论对上了， 和 `cache-id` 中的内容一一对应
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# ll image/overlay2/layerdb/sha256/*/cache-id
-rw-r--r-- 1 root root 64 11月 11 13:32 image/overlay2/layerdb/sha256/228fb92e31891f472e9857ee11d13c404ff7c88e808b05ce4ebdc80d785d71f3/cache-id
-rw-r--r-- 1 root root 64 11月 11 13:31 image/overlay2/layerdb/sha256/50644c29ef5a27c9a40c393a73ece2479de78325cae7d762ef3cdc19bf42dd0a/cache-id
-rw-r--r-- 1 root root 64 11月 11 13:32 image/overlay2/layerdb/sha256/5f72760956a669e4c9b33aa3f2f04baa84b0f4cf1e11676049981bafcbba74da/cache-id
-rw-r--r-- 1 root root 64 11月 11 13:32 image/overlay2/layerdb/sha256/fe267088885017d5e9a4621e68617a7f35e58dc2d0d747927882da21059854e3/cache-id
```

在看看具体镜像 layer 层的内容:

- diff: 这个层所做的改动，如通过 `ADD`、`RUN` 等指令对做文件系统做出的改变都在这里了。
- link: 自己的link值，在刚刚的 `overlay2/l` 目录下可以看的到。
    ```shell script
    [root@iZuf685opgs9oyozju9i2bZ docker]# cat   overlay2/00b65b9c288df8c0ae7cdacba531a7dc5cb006e6c768e19ee36055717b782acc/link 
    HG76ICE67NTXFL7AYXCMI3EK4Y
    ```
- lower: 该层所依赖的层的所有link，base layer 不依赖任何层，所以也就不会有 `lower` 这个文件，最后一层依赖之前的所有层，如:
    ```shell script
    [root@iZuf685opgs9oyozju9i2bZ docker]# cat overlay2/5da215c4f218cbb1d9825fa111c21bf381dc35a9e6c7c6cd5c3ea952316031e4/lower 
    l/HG76ICE67NTXFL7AYXCMI3EK4Y:l/33RV26M4VMX3ZUISOG26USXBKR:l/MUHXHRXFSGNCBKQ2AUXDFOUDLF
    ```
  这个镜像的最后一层依赖前面的层
- merged:容器的最终视图，merge 了 镜像层加读写层

> 启动容器新建的两层在 `containers` 中详细说。

### containers
我们一直说 docker 镜像是分层的， 容器 = 镜像 + 读写层 ，如果还没有什么感觉的话不妨再来看一个图:

![](https://gitee.com/russellgao/blogs-image/raw/master/images/docker/docker-local-storage-container.svg)

可以看到容器是依赖于镜像，启动容器时会先把镜像的各个 layer 联合挂载成一个统一的视图(只读层)，就是我们在 `overlay2` 目录中看到的 `b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc-init` 目录，
去掉 `-init` 就是对应的读写层。

看看 `containers` 目录下都有什么: 

```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# tree -L 2 containers/
containers/
└── 4ec800c3ec10654a6ea2b2317ac198514748464a217ef63bb58ef67874a79ae0
    ├── 4ec800c3ec10654a6ea2b2317ac198514748464a217ef63bb58ef67874a79ae0-json.log
    ├── checkpoints
    ├── config.v2.json
    ├── hostconfig.json
    ├── hostname
    ├── hosts
    ├── mounts
    ├── resolv.conf
    └── resolv.conf.hash

3 directories, 7 files
[root@iZuf685opgs9oyozju9i2bZ docker]# docker ps -a
CONTAINER ID        IMAGE                                    COMMAND                  CREATED             STATUS              PORTS                                      NAMES
4ec800c3ec10        russellgao/openresty:1.17.8.2-5-alpine   "/usr/local/openrest…"   About an hour ago   Up About an hour    0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp   openresty-app-1

```

可以看到这个下面是以容器为单位进行存放的，保存了每个容器的详细配置，在容器里看到的`hostname`,`/etc/hosts`,`dns` 等各种配置在这里都可以找得到，这里就不展开看每个具体文件了，有兴趣者可以自行查看。

> 值得一提的是，通过 `docker inspect containername` 得到的内容在 `containers/xxx/config.v2.json` 都可以找的到哦，可以查看它们的输出，会发现出奇的相似哦。

**请注意好玩的事情来了**

我们说到 **容器=镜像+读写层** ，那是不是以为着我们在读写层做修改，容器中可以看到，反之在容器中做的修改，在读写层也应该能看到才对。
> 读写层时各临时的 layer 层(临时目录) ，当容器被删除时，这个 layer 也会随之被删除。

做了实验看看:
最初读写层的内容和容器的根目录如下:

```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# ll overlay2/b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc/diff/
总用量 16
drwxr-xr-x 3 root root 4096 9月  19 00:25 run
drwxr-xr-x 3 root root 4096 9月  19 00:25 usr
[root@iZuf685opgs9oyozju9i2bZ docker]# 
[root@iZuf685opgs9oyozju9i2bZ docker]# docker exec openresty-app-1 ls -l /
total 64
drwxr-xr-x    1 root     root          4096 Sep 18 16:25 bin
drwxr-xr-x    5 root     root           340 Dec 12 05:29 dev
drwxr-xr-x    1 root     root          4096 Dec 12 05:29 etc
drwxr-xr-x    2 root     root          4096 May 29  2020 home
drwxr-xr-x    1 root     root          4096 Sep 18 16:25 lib
drwxr-xr-x    5 root     root          4096 May 29  2020 media
drwxr-xr-x    2 root     root          4096 May 29  2020 mnt
drwxr-xr-x    2 root     root          4096 May 29  2020 opt
dr-xr-xr-x  114 root     root             0 Dec 12 05:29 proc
drwx------    2 root     root          4096 May 29  2020 root
drwxr-xr-x    1 root     root          4096 Sep 18 16:25 run
drwxr-xr-x    2 root     root          4096 May 29  2020 sbin
drwxr-xr-x    2 root     root          4096 May 29  2020 srv
dr-xr-xr-x   13 root     root             0 Nov 11 00:49 sys
drwxrwxrwt    1 root     root          4096 Sep 18 16:25 tmp
drwxr-xr-x    1 root     root          4096 Sep 18 16:25 usr
drwxr-xr-x    1 root     root          4096 May 29  2020 var
```

进入到容器并在根目录生成一个文件:
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# docker exec -it  openresty-app-1 sh
/ # echo "测试容器的读写层-20201209" > /test-layer.20201209.txt
```

读写层看看什么情况:
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# ll overlay2/b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc/diff/
总用量 24
drwx------ 2 root root 4096 12月 12 15:22 root
drwxr-xr-x 3 root root 4096 9月  19 00:25 run
-rw-r--r-- 1 root root   34 12月 12 15:22 test-layer.20201209.txt
drwxr-xr-x 3 root root 4096 9月  19 00:25 usr
[root@iZuf685opgs9oyozju9i2bZ docker]# cat overlay2/b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc/diff/test-layer.20201209.txt 
测试容器的读写层-20201209
```
可以看到在容器中新建的文件确实在读写层中可以看到，那么反过来再试试

在读写层新建一个文件:

```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# echo "测试容器的读写层-20201209-abcdefg" > overlay2/b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc/diff/test-layer.20201209-abcdefg.txt 
[root@iZuf685opgs9oyozju9i2bZ docker]# ll overlay2/b04b728c94b5a269e9d102329c930e3781212717e830e1941e1008088d823cdc/diff/
总用量 28
drwx------ 2 root root 4096 12月 12 15:22 root
drwxr-xr-x 3 root root 4096 9月  19 00:25 run
-rw-r--r-- 1 root root   42 12月 12 15:26 test-layer.20201209-abcdefg.txt
-rw-r--r-- 1 root root   34 12月 12 15:22 test-layer.20201209.txt
drwxr-xr-x 3 root root 4096 9月  19 00:25 usr
```

进到容器中看看:
```shell script
[root@iZuf685opgs9oyozju9i2bZ docker]# docker exec -it openresty-app-1 sh
/ # ls -l 
total 72
drwxr-xr-x    1 root     root          4096 Sep 18 16:25 bin
drwxr-xr-x    5 root     root           340 Dec 12 05:29 dev
drwxr-xr-x    1 root     root          4096 Dec 12 05:29 etc
drwxr-xr-x    2 root     root          4096 May 29  2020 home
drwxr-xr-x    1 root     root          4096 Sep 18 16:25 lib
drwxr-xr-x    5 root     root          4096 May 29  2020 media
drwxr-xr-x    2 root     root          4096 May 29  2020 mnt
drwxr-xr-x    2 root     root          4096 May 29  2020 opt
dr-xr-xr-x  114 root     root             0 Dec 12 05:29 proc
drwx------    1 root     root          4096 Dec 12 07:22 root
drwxr-xr-x    1 root     root          4096 Sep 18 16:25 run
drwxr-xr-x    2 root     root          4096 May 29  2020 sbin
drwxr-xr-x    2 root     root          4096 May 29  2020 srv
dr-xr-xr-x   13 root     root             0 Nov 11 00:49 sys
-rw-r--r--    1 root     root            42 Dec 12 07:26 test-layer.20201209-abcdefg.txt
-rw-r--r--    1 root     root            34 Dec 12 07:22 test-layer.20201209.txt
drwxrwxrwt    1 root     root          4096 Sep 18 16:25 tmp
drwxr-xr-x    1 root     root          4096 Sep 18 16:25 usr
drwxr-xr-x    1 root     root          4096 May 29  2020 var
/ # cat test-layer.20201209-abcdefg.txt 
测试容器的读写层-20201209-abcdefg
```

可以看到和我们设想的一致。

## 总结
> 这篇文章很长，难免表达逻辑上出现混乱，感谢能耐心看完的小伙伴，如果有不对之处欢迎批评指正。

- image/overlay2
    - distribution: 和镜像分发相关，记录了diffid 与 digest 之间的关系。
    - imagedb: 记录了镜像的元信息，其中`content`中的内容和`docker inspect image` 结果基本一直。
    - layerdb: 记录了 layer 的元信息，如真正的 layerid， size 等信息。
    - repositories.json: 记录这个主机上所有的镜像。
- overlay2: 镜像的具体layer 层的内容，包括镜像的只读层和容器的读写层。其中读写层是临时层，当容器删除时也会随之删除，在这一层的 diff 目录下做修改，容器内也会随之看到。
- containers: 容器的配置信息，通过 `docker inspect containerid` 得到的结果和 `containers/xxx` 下的内容基本一直。

## 参考
- https://segmentfault.com/a/1190000017579626


