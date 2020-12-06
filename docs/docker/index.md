# docker 内部构造到底是什么样子的?


## 导读
> 提起 docker 大家应该耳熟能详，如使用 docker 所带来的持续集成、版本控制、可移植性、隔离性、安全性等诸多好处。docker
>的使用也很方便，但是其内部原理是什么样的？都有哪些组件？之间是如何相互协作的呢？这篇文章尝试揭开其内部运行原理，受限
>作者水平，如有不对之处，欢迎批评之处。

