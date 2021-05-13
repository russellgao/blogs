# CUE Use Cases


## 导读
> CUE可用于与数据相关的广泛的连续应用中。本节讨论了CUE如何在各种应用领域提供优势。
>
> 本文主要内容来自于官方文档。

## 配置
> 管理基于文本的文件，以定义一个系统的期望状态。

可以说，验证应该是任何配置语言的首要任务。然而，大多数配置语言的重点是去除模板。CUE的不同之处在于，它采取了验证优先的立场。但CUE的约束条件也能有效地减少模板，尽管它采取的方法与传统的数据模板语言有很大的不同。

CUE的基本操作是合并配置，无论执行的顺序如何，结果都是一样的（它是关联的、互换的和同位的）。这个属性是许多其他有利属性的基础，如下所述。

### CUE解决的核心问题
#### 类型检查 
对于大型代码库来说，没有人会质疑对编译/类型化语言的要求。为什么不要求对数据有同样的严谨性呢？

许多配置语言，包括GCL和它的后代，都把减少模板作为配置的主要任务。然而，对类型的支持是最小的，甚至几乎不存在。

有些语言确实添加了类型支持，但通常仅限于验证基本类型，这在编程语言中很常见。然而，对于数据来说，这还不够。这方面的证据是像CDDL和OpenAPI这样超越基本类型的标准的兴起。

在CUE中，类型和值是一个统一的概念，这给了它非常有表现力，但又直观和紧凑的类型能力。

```
#Spec: {
  kind: string

  name: {
    first:   !=""  // must be specified and non-empty
    middle?: !=""  // optional, but must be non-empty when specified
    last:    !=""
  }

  // The minimum must be strictly smaller than the maximum and vice versa.
  minimum?: int & <maximum
  maximum?: int & >minimum
}

// A spec is of type #Spec
spec: #Spec
spec: {
  knid: "Homo Sapiens" // error, misspelled field

  name: first: "Jane"
  name: last:  "Doe"
}

```
#### 规模化的简单性
当使用配置语言来减少模板时，应该考虑减少的冗长性是否值得增加的复杂性。大多数配置使用覆盖模型来减少模板：一个现有的配置被用作基础，并被修改以产生一个新的配置。这通常是以继承的形式。

对于小规模的项目来说，使用继承可能太复杂了，简单地把所有东西都拼出来往往是一种优越的方法。然而，对于大规模的项目，使用继承往往会导致深层次的修改，使人很难看出数值的来源。最后，增加的复杂性是否值得也是个问题。

就像其他配置语言一样，如果数值被组织到多个地方，CUE会增加复杂性。然而，由于CUE不允许重写，所以自然而然地防止了深度分层。更重要的是，CUE还可以提高可读性。一个文件中的定义可能适用于许多其他文件中的值。人们通常需要打开所有这些文件来验证其有效性；而使用CUE，人们可以一目了然。

CUE的方法已经在计算语言学中得到了检验，在那里它已经被用来描述人类的语言；实际上是非常大的、复杂的和不规则的配置。

#### 抽象与直接访问 
配置语言的一个常见争论是，一种语言是否应该为API提供一个抽象层。一方面，抽象层可以保护用户不被滥用。另一方面，它们需要跟上API的变化，不可避免地容易发生偏移。所以，它是这样的。

CUE解决了这两个问题。一方面，它的细粒度类型允许在本地API的基础上分层设置详细的约束，而不需要抽象层。新的功能可以在不支持现有定义的情况下被使用。

另一方面，CUE的顺序独立性允许抽象层以可控的方式注入任意的原始API，允许一个通用的逃生舱来支持新的或未覆盖的功能。请参阅 [Kubernetes](https://cuelang.org/docs/tutorials/kubernetes) 教程的手册部分，了解一个例子。

#### Tooling
配置语言通常将其配置转换为较低级别的表示，如JSON、YAML或Protobuf，以便它可以被使用这些语言的工具所消费。最初，将这样的输出管道输送到所需的工具中是可行的；但迟早人们会有将其自动化的愿望，通常是以某种工具的形式。

于是就这样了。需要高级配置的系统的兴起，与更加专业的命令行工具的兴起相匹配。所有这些工具的核心结构或多或少都是一样的。更令人恼火的是，许多工具的功能重叠，但几乎没有可扩展性或可互操作性。在后一种情况下，人们可能会看到有必要在另一套工具上分层。

拥有像kubectl或etcdctl这样直接控制核心基础设施的工具是有意义的，但在更高的抽象层次上，我们需要一个更开放的方法。

CUE试图通过在配置层之上提供一个开放的、声明式的脚本层来解决这个问题。除了上述情况外，它还被设计用来解决其他各种问题:

- 向配置中注入环境数据，这是CUE本身不允许的（它是纯粹的，或密封的，或无副作用的）
- 将计算数据注入配置中，作为管道的一部分
- 允许工具集成的可组合性

同样，确定地合并来自不同来源的数据的能力使CUE的任务变得很简单。

### 比较
#### 基于继承的配置语言 
继承，在一般情况下不是交换性和等价的。换句话说，顺序很重要。这使得我们很难追踪 value 的来源。这不仅对人类如此，对机器也是如此。这使得做任何类型的自动化都非常复杂，甚至不可能。如果数值可以从几个方向中的一个进入一个对象（超级，覆盖等），那么继承的复杂性就更大了。

CUE的基本操作是交换性、关联性和等价性的。这种顺序独立性对人类和机器都有帮助。由此产生的模型就不那么复杂了。

> **CUE中的继承性**
>
> 尽管CUE没有覆盖意义上的继承，但它确实有一个值是另一个值的实例的概念。事实上，这是一个核心原则。
>
> 让我们用一个现实世界的例子来说明这个区别：在继承的覆盖模型中，我们可以把一个现有的模板，比如说一只狗，修改成一只猫。修剪耳朵，擦干鼻子，诸如此类。
>
>在CUE中，这是一个分类的问题。猫和狗都是动物的实例，但是一旦一个实体被定义为猫，它就不可能变成狗。对于大多数人来说（也就是那些还没有习惯于继承的计算机科学家），这完全是有意义的。
>

尽管人们可以创建 values 的实例（记住，类型就是值），但人们不能改变父类的任何值。一个模板就像一个类型。就像在静态类型语言中，人们不能把一个整数分配给一个字符串一样，在CUE中人们也不能违反类型的属性。

这些限制降低了灵活性，但也提高了清晰度。要确保一个配置拥有某个属性，只需在项目中包含的任何文件中声明它，使之成为一个属性。没有必要去看其他文件。正如我们所看到的；与基于继承的语言相比，强加的限制还可以提高而不是伤害删除模板的能力。

基于继承的模型的复杂性也阻碍了自动化。GCL的引入是与先进的工具的承诺相匹配的。声明性语言的口号甚至在它的一些后代中被重复。但是，工具化从来没有实现过，因为这个模型使它难以实现。

CUE已经提供了像 `trim` 这样的强大工具，它的API为不完整的配置提供了统一和归并操作，这是强大分析的基础。

#### Jsonnet/ GCL
像Jsonnet一样，CUE是JSON的超集。它们也都受到GCL的影响。CUE反过来又受到Jsonnet的影响。这可能让人觉得这两种语言非常相似。但在核心方面，它们是非常不同的。

CUE的重点是数据验证，而Jsonnet的重点是数据模板化（去除模板）。Jsonnet在设计时没有考虑到验证问题。

Jsonnet和GCL在减少模板方面可以说是相当强大。CUE的目标并不是要比Jsonnet或GCL更好地去除模板。CUE的设计是为了解决这些方法的两个主要缺点：复杂性和缺乏类型化。Jsonnet减少了GCL的一些复杂性，但在很大程度上也属于同一类别。对于CUE来说，权衡的结果是增加打字和减少复杂性（对于人类和机器），代价是放弃了灵活性。

#### HCL
HCL与GCL有一些惊人的相似之处。但不管这是个巧合还是故意的，它去掉了GCL的核心复杂性来源：继承。

它确实引入了一个简洁版的继承：文件叠加。字段可以在多个文件中定义，按照文件名的一定顺序被覆盖。虽然没有GCL那么复杂，但它确实有一些相同的问题。

另外，不管取消继承是一个巧合还是一个伟大的洞察力，都没有给出大规模配置管理可能需要的结构作为回报。这意味着HCL的使用对于中大型设置来说可能会遇到天花板。

因此，CUE为HCL的用户提供的是：typing，更好的发展前景，更大规模的操作，以及消除文件叠加的特殊性。

CUE确实借用了CCL的一个结构：将单字段对象折叠到单行的做法直接受到了CCL非常相似的启发。

## 数据验证
验证基于文本或程序的数据。

到目前为止，指定数据的最直接的方法是在纯JSON或YAML文件中。每一个值都可以在需要定义的地方查询到。但是，即使在小规模的情况下，人们很快就不得不处理一致性问题。

数据验证工具允许根据模式来验证这些数据的一致性。

### CUE解决的核心问题 
#### 客户端验证 
没有太多方便的工具来验证纯数据文件。通常情况下，验证是依靠服务器端来完成的。如果它是在客户端完成的，它要么依赖于相当冗长的模式定义，要么使用自定义的工具来验证特定领域的模式。

cue命令行工具提供了一种相当直接的方式来定义模式，并根据数据文件的集合来验证它们。

给出这两个文件： 
```yaml
# ranges.yaml
min: 5
max: 10
---
min: 10
max: 5
```

```shell script
// check.cue
min?: *0 | number    // 0 if undefined
max?: number & >min  // must be strictly greater than min if defined.
```
cue vet命令可以验证ranges.yaml中的值是否正确 
```shell script
cue vet ranges.yaml check.cue
max: invalid value 5 (out of bound >10):
    ./check.cue:2:16
    ./ranges.yaml:5:7
```

#### 验证面向文档的数据库
像Mongo和其他许多数据库一样，面向文档的数据库的特点是拥有灵活的模式。其中一些数据库，如Mongo，可以选择允许模式定义，通常以JSON模式的形式。

CUE约束可以用来验证面向文档的数据库。它的默认机制和表达式语法允许为一个旧版本的模式填补缺失的值。更重要的是，CUE的顺序独立性允许 "补丁 "规范与主要模式定义分开。CUE可以负责合并这些，并报告定义中是否有任何不一致的地方，甚至在它们被应用到具体案例之前。

CUE可以使用其API直接应用于代码中的数据，但它也可以用来从CUE定义中计算JSON模式。(参见 cuelang.org/go/encoding/openapi)。如果一个面向文档的数据库原生支持JSON模式，那么这样做很可能有其好处。使用CUE来生成模式比直接这样做有几个好处：

- CUE 比较简洁
- CUE可以从其他来源提取基础定义，比如Go和Protobuf。
- 它允许在这些其他资源中注释验证代码（例如Go的字段标签，Protobuf的选项）。
- CUE具有合并、验证和规范化配置的能力，允许在主模式和旧版本的补丁之间进行分离
- CUE可以以多种形式变形定义，例如Kubernetes的CRD从1.15版本开始需要的结构性OpenAPI。

#### 迁移路径 
正如在   [Be useful at all scales](https://cuelang.org/docs/about#be-useful-at-all-scales) 中所讨论的，当一个人用某种方法达到极限时，改变语言的成本很高。

CUE为普通数据文件增加了类型检查的好处。一旦投入使用，当这种方法达到极限时，它允许同样的、熟悉的工具转移到更加结构化的东西。CUE提供了自动重写工具，如cue import和cue trim来帮助这种迁移。

### 比较
#### JSON Schema 
最接近用模式验证JSON和YAML的方法是使用JSON Schema 和配套的工具。

与CUE相比，JSON Schema 没有一个统一的类型和价值模型。这使得使用JSON模式来减少模板的能力降到最低。由于它是在JSON本身中指定的（它不是一个DSL），它可能是相当啰嗦的。

总的来说，CUE是一种更简明，但更强大的模式语言。例如，在CUE中，人们可以指定两个字段需要彼此相同。

```
point: {
    x: number
    y: number
}

diagonal: point & {
    x: y
    y: x
}
```

这样的事情在JSON模式（或大多数配置语言）中是不可能的。


## 模式定义
定义模式以沟通API或标准。

一种数据定义语言描述了数据的结构。这种语言所定义的结构反过来可以用来验证实现、验证输入或生成代码。

大多数现代的专用数据定义语言或标准允许的不仅仅是描述一个字段是整数还是字符串。像OpenAPI和CDDL这样的标准允许定义诸如默认值、范围和其他各种约束。OpenAPI甚至允许复杂的逻辑组合器。

然而，一个关键的区别是，这些标准没有统一模式和值，而这正是CUE的强大之处。没有价值网格。这在不同方面限制了这些标准。

### CUE解决的核心问题 
#### 验证向后的兼容性 
CUE的模型使得验证较新版本的模式与旧版本的模式向后兼容变得很容易。

考虑一下同一API的以下版本。
```
// Release notes:
// - You can now specify your age and your hobby!
#V1: {
    age:   >=0 & <=100
    hobby: string
}
// Release notes:
// - People get to be older than 100, so we relaxed it.
// - It seems not many people have a hobby, so we made it optional.
#V2: {
    age:    >=0 & <=150 // people get older now
    hobby?: string      // some people don't have a hobby
}
// Release notes:
// - Actually no one seems to have a hobby nowadays anymore, so we dropped the field.
#V3: {
    age: >=0 & <=150
}
```
名称以#开头的声明是定义。在转换为数据时，例如在导出为JSON时，定义不会被释放出来，因此在这种情况下不需要具体化。定义假定了封闭结构的定义，这意味着用户只能使用明确定义的字段。

在CUE中，如果一个API取代了旧的API，或者旧的API是新的API的一个实例，那么它就是向后兼容的。

这可以通过API来计算： 

```go
inst, err := r.Compile("apis", /* text of the above API */)
if err != nil {
    // handle error
}
v1, err1 := inst.LookupField("V1")
v2, err2 := inst.LookupField("V2")
v3, err3 := inst.LookupField("V3")
if err1 != nil || err2 != nil || err3 != nil {
	 // handle errors
}

// Check if V2 is backwards compatible with V1
fmt.Println(v2.Value.Subsumes(v1.Value))) // true

// Check if V3 is backwards compatible with V2
fmt.Println(v3.Value.Subsumes(v2.Value))) // false
```
就这么简单。这就是像CUE那样，通过在一个网格中对所有的值进行排序而实现的事情。对于CUE来说，检查一个API是否是另一个的实例就像检查3是否小于4一样。

请注意，相对于V1，V2严格放宽了API。它允许指定一个更广泛的年龄范围，并使爱好字段成为可选项。在V3中，爱好字段是明确禁止的。这不是向后兼容的，因为它破坏了以前包含爱好字段的字段。

#### 结合来自不同来源的制约因素 
大多数数据定义语言往往没有明确的换元性定义。例如，CDDL虽然比CUE的表达能力差得多，但它引入了打破换元性的操作符。

由换元性得到的加法属性对于数据定义来说是非常有价值的。约束条件往往来自很多方面。例如，我们可以有来自基础模板的约束，来自代码的约束，来自不同部门提供的政策和来自客户提供的政策。

CUE的约束条件的加法性允许以任何顺序堆积约束条件，以获得一个新的定义。这将我们引向下一个话题。

#### 数据定义的规范化 
从许多来源添加约束会导致大量的冗余。更糟糕的是，约束条件可以用不同的逻辑形式来指定，使得它们的加法形式变得冗长而不方便。如果一个系统使用这些约束条件只是验证数据的话，这还算好的。但是，如果添加的约束条件要形成人类消费的基础，这就有问题了。

CUE的逻辑推理引擎会自动减少约束。它的API使得计算和选择各种正常形式成为可能，以优化某种表述。例如，这被用于CUE的[OpenAPI生成器](https://cuelang.org/docs/integrations/openapi)中。

### 比较
#### JSON Schema / OpenAPI 
JSON Schema和OpenAPI是纯粹的数据驱动的数据定义标准。OpenAPI起源于Swagger。从第三版开始，OpenAPI或多或少是JSON Schema的一个子集。OpenAPI被用来定义Kubernetes自定义资源定义。从1.15版本开始，这需要一个OpenAPI的变体，称为结构性OpenAPI。此后，我们将把这些统称为OpenAPI。

OpenAPI没有任何表达式或引用。但它们有强大的逻辑运算符，使它们具有明显的表现力。

> **在逻辑上不**
>
>OpenAPI定义了一个not操作符。当定义在结构上时，这些就变得模糊了，OpenAPI允许这样做。CUE没有这样的结构，部分原因是为了避免其逻辑上的缺陷。然而，通过将¬P解释为P→⊥，它可以得到一个很好的近似值。

OpenAPI的一个优点是，它纯粹是以数据（JSON）来定义的。这使得它可以通过电线发送。它的定义是这样的：实现一个解释器是相当直接的。

一个缺点是，它非常啰嗦。比较以下两个等价的模式定义: 

CUE
```
// Definitions.

// Info describes...
Info: {
    // Name of the adapter.
    name: string

    // Templates.
    templates?: [...string]

    // Max is the limit.
    max?: uint & <100
}
```

Openapi 
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Definitions.",
    "version": "v1beta1"
  },
  "components": {
    "schemas": {
      "Info": {
        "description": "Info describes...",
        "type": "object",
        "required": [
            "name"
        ],
        "properties": {
          "name": {
            "description": "Name of the adapter.",
            "type": "string",
            "format": "string"
          },
          "templates": {
            "description": "Templates.",
            "type": "array",
            "items": {
              "type": "string",
              "format": "string"
            }
          },
          "max": {
            "description": "Max is the limit",
            "type": "integer",
            "minimum": 0,
            "exclusiveMaximum": 100
          }
        }
      }
    }
  }
}

```

随着更多的约束条件和逻辑组合器的使用，这种差异变得更加极端。

OpenAPI和CUE都有各自的作用。OpenAPI的JSON格式使其成为良好的交换标准。另一方面，CUE可以作为一个引擎来生成和解释OpenAPI约束。请注意，CUE通常更有表现力，许多CUE约束不能在OpenAPI中编码。

## 参考
- https://cuelang.org/docs/usecases/
- https://github.com/cuelang/cue


