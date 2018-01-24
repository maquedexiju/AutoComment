根据一些规则，自动生成评论内容。

## 基本思想
**第一步是拆分：**  
我们可以把评论拆分成一些标准的组件，每个标准组件其实也是可以再进行拆分的，最后变成非常简单的规则。
例如：

* {sentence}：完整的句子，最大的组件，可能包括以下：
    * {shortComment}：最简单的、用于表达正向情绪的语句
    * {buyIt}：从哪里获取的我们的智能硬件
    * {favoriteFunction}：对最喜爱的功能进行描述
    * {sorrow}：一些建议、遗憾（当然是很虚假的）
    * {symbol}：表达情绪的句尾标点
    * {face}：emoji 表情

其中的{shortComment}也可以继续拆分，除了一些成语，还可以是 {adv}{good}，也就是一个*副词*加上一个*表达正向的形容词*。

**第二步是扩充：**  
我们对每一个组件进行扩充，不断去完善每一个组件。  
例如：

{adv} 可以扩充为：很、非常、极其、最……  
{good} 可以扩充为：好用、极致、简单、极客、优雅……

**第三步是排列组合：**
也就是随机选取和搭配，有了前两步的铺垫，我们就能组合出非常多的评论。  
我们还是拿 {adv}{good} 举例：

如上我们扩充了两个词库，之后我们来随机选取其中的内容，就能组合成如下内容：  
很极致、最优雅、极其简单、非常好用、非常极客……

## 基础使用
确定自己需要生成多少条评论后，在 config 文件中设置 totalNumbers 即完成了基础设置。  
之后直接执行程序即可，程序执行完成后，生成的 comment 会出现在 comment.txt 的底部。

## 词库的基本扩展
词库结构其实也就是数据结构了。毕竟是小型词库，我也没有用数据库，直接用 Python 的数据格式就好了。
为了适应各种情况，具体设计如下：

### 简单数据

```
lexiconName = [
    'content1',
    'content2',
    ...
]
```

说明：  
lexiconName 是词库名称  
contentN 是词库中的内容，注意，最后一个元素后不要加逗号

举例：

```
adv = [
   '很',
   '非常',
   '最',
   '极其' 
]
```

### 引用其他词库
在某个词库中引用另一个词库的语法很简单：

```
{lexiconName}
```

即把词库名称用花括号包裹  
举例：

```
shortComment = [
    '{adv}{good}',
    '令人印象深刻',
    '强烈推荐',
    '{adv}喜欢'
]
```

### 注释
只是写给自己看，用以提示自己的部分，以 `#` 开头即可

```
# 这是一行注释
shortComment = [ # 井号之前的是词库，井号之后的这部分是注释
    'content1',
    'content2',
    ...
]
```

### 引用多个同类组件
在某个语句中出现了多个同类组件，此时分两种情况。

#### 希望后一个和前一个保持一致
有点类似“代词”的概念，只要保持前后的引用名称相同即可  
例如：

```
shortComment = [
    '{face}{face}{face}{adv}{good}'
    ...
]
```

#### 希望后一个和前一个不同
此时需要在后续的组件名称后加上数字进行区分，例如

```
shortComment = [
    '{face}{face1}{face2}{adv}{good}'
    ...
]
```

## 词库的高级扩展
### 空组件
为了自然，有些组件可能需要需要填充为**空**，此时需要使用 `'_'`，千万不要使用 `''`。  
例如：

```
symbol = [
    '_', # 这是正确的，结果不会显示"_"，而是什么有不会显示
    '', # 这是错误的，会导致生成失败
    '!',
    '!!',
    '。',
]
```

### 自定义权重
为了更加自然、达到更好的效果，组件中不同内容出现的概率可能不同，此时可以通过自定义权重的方式解决。  
语法如下：

```
lexiconName = [
    ['content1.1', chance1],
    ['content1.2', chance2],
    ...
    'content2.1',
    'content2.2',
    ...
]
```

说明：  
content1.N 是需要自定义权重的内容，chanceN 即对应内容的权重（概率）。  
content2.N 是不需要自定义权重的内容，它们会平分没有定义的那部分权重。

举例：

```
face = [
    ['_', 0.8], # 无表情的占 80%
    ['😀', 0.05], # 这个表情占 5%
    '😁', # 剩下的所有表情均分剩下的 15% 概率
    '😄',
    '😆',
    '🙂',
    '😏',
    '😉',
    '😊',
    '🙂'
]
```

### 制约关系
如果组件之间存在制约关系，例如 {device}（设备组件）和 {placeInHome} （家中位置组件）就存在着制约关系。  
{device} 中的**电饭锅**之类的设备，只能与 {placeInHome} 中的**厨房**等位置关联，因此需要单独的方式来维护这种制约关系。

这会比较麻烦，有三步：

* 为两个相关的组件中的每个内容添加一个属性
* 添加一个制约关系的描述表
* 把制约关系的描述表信息记录在组件库中

#### 为两个相关的组件中的每个内容添加一个属性

语法如下：

```
lexicon = {
    'conditions': {}, # 用来记录制约关系，这里先不填
    'v':{
        'content1':property1,
        'content2':property2,
        'content3':property3,
        ...
    }
}
```

需要说明的是，这里支持 一个属性（propertyN）对应多个内容（contentN）。
例如:

```
lexicon = {
    'conditions': {}, # 用来记录制约关系，这里先不填
    'v':{
        'content1':property1,
        'content2':property1,
        'content3':property2,
        ...
    }
}
```

#### 添加一个制约关系的描述表
假设两个组件库的名称分别为 lexicon1 和 lexicon2，创建的描述表需要命名为 lexicon1VSlexicon2。  
表的内容如下：

```
lexicon1VSlexicon2 = [
    'property1_of_lexicon1':[the_list_of_lexicon2_properties, ...],
    'property2_of_lexicon1':[the_list_of_lexicon2_properties, ...],
    'property3_of_lexicon1':[the_list_of_lexicon2_properties, ...]
]
```

#### 把制约关系的描述表信息记录在组件库中
需要在 lexicon1 中的 conditions 部分增加：`'lexicon2': 'lexicon1VSlexicon2'`  
同时在 lexicon2 中的 conditions 部分增加： `'lexicon1': 'lexicon1VSlexicon2'`

#### 举例

```
# 第一个组件库
device = {
    'conditions':{
        'placeInHome': 'deviceVSPlaceInHome'
    },
    'v':{
        '插座':'p', # plugin
        '电量统计插座':'p',
        '球泡灯':'b', # bulb
        '彩灯':'b',
        '空调':'c', # circumstance
        '空气净化器':'c',
        '电风扇':'c',
        '净水器':'k', # kitchen
        '家用摄像机':'s', # 安全
        '门磁':'s'
    }
}

# 第二个组件库
placeInHome = {
    'conditions':{
        'device': 'deviceVSPlaceInHome',
    },
    'v':{
        '客厅':'l',
        '厨房':'k',
        '卧室':'b',
        '书房':'s',
        '楼上':'u',
        '楼下':'d',
        '卫生间':'w'
    }
}

# 记录制约关系的表
deviceVSPlaceInHome = {
    'p': ['l', 'k', 'b', 's', 'u', 'd', 'w'],
    'b': ['l', 'k', 'b', 's', 'u', 'd', 'w'],
    'c': ['l', 'k', 'b', 's', 'u', 'd'],
    'k': ['k', 'u', 'd'],
    's': ['l', 'k', 'b', 's', 'u', 'd']
}

```

### 制约关系加权重
还是以 {device} 为例，把概率加到属性之后，并把属性和概率使用方括号包起来即可。   
举例：

```
device = {
    'conditions':{
        'placeInHome': 'deviceVSPlaceInHome',
        'purpose': 'deviceVSPurpose'
    },
    'v':{
        '插座':['p', 0.2], # plugin
        '电量统计插座':['p', 0.05],
        '墙面开关':['p', 0.03],
        '球泡灯':['b', 0.15], # bulb
        '彩灯':'b',
        '吸顶灯':'b',
        '灯带':'b',
        '空调':'c', # circumstance
        '空气净化器':'c',
        '电风扇':'c',
        '净水器':'k', # kitchen
        '冲奶机':'k',
        '面包机':'k',
        '家用摄像机':'s', # 安全
        '门磁':'s'
    }
}
```





