+++
title = "如何利用 golang 操纵 oracle"
description = "如何利用 golang 操纵 oracle"
date = "2020-11-25"
aliases = ["about-me"]
author = "russellgao"
draft = false
tags = [
    "golang",
    "oracle",
    "数据库"
,]

categories = [
    "golang"
]

+++

## 导读
这篇文章主要介绍如何利用 golang 操作 oracle 数据库，包括基本的增删改查，本地 oracle 环境搭建，以及如何在 docker 中运行。
oracle client 镜像构建并不容易，花了很长时间去踩坑，文中提供了已经构建好的基础镜像，可以直接使用，这里贡献给大家。

## 本地环境构建

### 安装客户端
oracle 客户端下载页面: https://www.oracle.com/database/technologies/instant-client/downloads.html

#### mac
- https://www.oracle.com/database/technologies/instant-client/macos-intel-x86-downloads.html

在上面的页面下载之后执行:

```shell script
# 解压
cd ~
unzip instantclient-basic-macos.x64-19.3.0.0.0dbru.zip

# 创建link
mkdir ~/lib
ln -s ~/instantclient_19_3/libclntsh.dylib ~/lib/
```

我本地环境环境是 mac ，这个亲测有用。linux 和 windows 只给出了相关参考连接，没有实际操练过。

#### linux
- https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html

#### windows
- https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html

## 用法
go 操作 oracle 可以使用 [github.com/godror/godror](github.com/godror/godror) ，如

```go
package main

import (
	"database/sql"
	"fmt"
	_ "github.com/godror/godror"
	"os"
)

func main() {
	connString := "oracle://hd40:xxx@121.196.127.xxx:1521/ylyx?charset=utf8"
	db, err := sql.Open("godror", connString)
	if err != nil {
		fmt.Println(err)
		os.Exit(10)
	}
	// 注意不要 sql 语句不要使用 ; 号结尾，否则会报错
	// dpiStmt_execute: ORA-00911: invalid character
	sql := "select * from user_tables "
	rows, err1 := db.Query(sql)
	if err1 != nil {
		fmt.Println(err1)
		os.Exit(10)
	}
	result, err2 := GetQueryResult(rows)
	if err2 != nil {
		fmt.Println(err2)
		os.Exit(10)
	}

	fmt.Println(result)
	fmt.Println("end")
}

func GetQueryResult(query *sql.Rows) ([]map[string]string, error) {
	column, _ := query.Columns()              //读出查询出的列字段名
	values := make([][]byte, len(column))     //values是每个列的值，这里获取到byte里
	scans := make([]interface{}, len(column)) //因为每次查询出来的列是不定长的，用len(column)定住当次查询的长度
	for i := range values {                   //让每一行数据都填充到[][]byte里面
		scans[i] = &values[i]
	}
	results := []map[string]string{}
	for query.Next() { //循环，让游标往下移动
		if err := query.Scan(scans...); err != nil { //query.Scan查询出来的不定长值放到scans[i] = &values[i],也就是每行都放在values里
			fmt.Println(err)
			return nil, err
		}
		row := make(map[string]string) //每行数据
		for k, v := range values {     //每行数据是放在values里面，现在把它挪到row里
			key := column[k]
			row[key] = string(v)
		}
		results = append(results, row)
	}
	query.Close()
	return results, nil
}
```
用法说明 :

- `_ "github.com/godror/godror"` 这句是说明 sql 的 driver 是 oracle ，如果要操作 mysql ，换成 mysql 的 `driver (_ "github.com/go-sql-driver/mysql")` 即可。
- crud 操作还是调用 `database/sql` 进行完成。
- 暴露出来给用户的还是 `*sql.DB` 。查询可以调用 `*sql.DB` 的 `Query` 方法，执行其他 sql 则调用 `Exec` 方法。

## 常见报错
如果报如下错误:
```
(cx_Oracle.DatabaseError) DPI-1047: Cannot locate a 64-bit Oracle Client library: "dlopen(libclntsh.dylib, 1): image not found". See https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html for help
```

说明oracle的 client 没有正确安装


如果报错如下:
```
(cx_Oracle.DatabaseError) ORA-01017: invalid username/password; logon denied
```
说明oracle 的用户密码不正确

如果报错如下:
```
dpiStmt_execute: ORA-00911: invalid character
```
说明 sql 中包含无效字符，请注意如果 sql 中包含 `;` 就会报错，需要把 sql 中的 `;` trim 掉。我写了个标准化 sql 的方法，可以参考: 

```go
// 去掉行首和行尾的空白字符
func TrimBlankSpace(s string) string {
	_s := regexp.MustCompile("^\\s+").ReplaceAll([]byte(s), []byte(""))
	_s = regexp.MustCompile("\\s+$").ReplaceAll(_s, []byte(""))
	return string(_s)
}

// 去掉 ; 并且全部转为大写字符
func FormatSql(sql string) string {
	sql = TrimBlankSpace(sql)
	sql = strings.TrimRight(sql, ";")
	return strings.ToUpper(sql)
}
```

## docker 中运行
>我尝试过用 alpine 做基础镜像，然后进行安装 oracle client，把 oracle client 安装完成之后，运行编译完的 golang 程序，
出现了各种缺少动态库的问题，查了很多资料，和 apline 的官方源都彻底没有解决，然后就准备在 dockerhub 找一个现成的拿过来参考，
很遗憾没有找到一个可以直接用的，最后放弃了 alpine 这条路，选择 alpine 是因为 alpine 镜像比较小，这样做出来的镜像比较小。

看了 oracle client 官方下载和安装说明，也都是 centos 的版本，所以就基于 centos 做了一个包含 oracle client 的基础镜像。
已经上传到 dockerhub 了，参见: [https://hub.docker.com/r/russellgao/oracle](https://hub.docker.com/r/russellgao/oracle)

如果你刚好需要，而我刚好有，那不妨试用一下（如果能帮到您可以给个 star 哟）。

dockerhub 可能访问比较慢，或者可能会出现无法访问的情况，这里贴一些关键信息。

### 镜像说明
#### 镜像名称
```
russellgao/oracle:centos7-client12.2
```

#### 操作系统
```
centos:centos7.9.2009
```

#### oracle client 版本
```
oracle-instantclient12.2-basic-12.2.0.1.0-1.x86_64
```

#### 基于基础镜像优化的部分
- 调整时区为 CST 时区 （UTC +8）

#### 镜像用法
这个一般用作基础镜像 或者:
```shell script
docker run -it --rm russellgao/oracle:centos7-client12.2 date 
```
or
```shell script
docker run -d russellgao/oracle:centos7-client12.2 tail -f /dev/null 
```
