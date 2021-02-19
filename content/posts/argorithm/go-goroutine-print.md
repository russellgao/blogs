+++
title = "交叉打印"
description = "交叉打印"
date = "2021-02-18"
aliases = ["交叉打印"]
author = "russellgao"
draft = false
tags = [
    "多线程",
    "goroutine",
    "go"
,]
+++

# 交叉打印
数字和字母交叉打印，打印两个字母，接着打印一个数字，再接着打印两个字母，一直从 a 打印到 z，以字母结束。输出示例： 

```shell script
a b 1 c d 2 ... z
```

用 `go`语言的多线程实现

## 实现原理
用两个 `goroutine` 实现，一个打印字母，一个打印数字，通过一个 `chan` 控制打印顺序。


## 实现
```go
package main

import "fmt"

func main() {

	done := make(chan bool)
	c := make(chan bool)
	go func() {
		defer func() {
			done <- true
		}()
		letter := []string{"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}
		for i, item := range letter {
			if i%2 == 0 || i == 25 {
				c <- false
			} else {
				c <- true
			}
			fmt.Println(item)
		}
		close(c)

	}()

	go func() {
		count := 1
		for item := range c {
			if item {
				fmt.Println(count)
				count++
			}
		}
	}()
	<-done
}

```