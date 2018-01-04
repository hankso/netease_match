# 云村相亲大会
## 简介
<!-- - 使用[NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)(Binaryify) -->
- 爬取网易云用户公开的资料进行匹配
- 多种匹配规则可选 (喜欢歌曲重叠最多?收藏歌单相似？同城？评论？...)
- 只需提供你的`用户名`就可以找到跟你最匹配的 Ta

## 记录
##### 2018.01.04
用哪些属性来描述一个用户的口味呢,目前来看标签是最好的

因为根据网上信息显示,网易云的日推算法很有可能就是用到了标签,标签的总数量又是固定的(数据维度固定),总共就那么几十个,所以是非常理想的用户特征

一些想法:
- 一个用户的歌单包括自己创建的和收藏的,将 **用户自己创建** 的(包含`喜欢的音乐`)所有歌单中的所有音乐用于判断两人重合歌曲的数量,这个还是很简单实现的

- 网易云是否有对每首音乐的标签(或者特征描述)?
    - 这跟淘宝推荐商品的情形很相似,同样是巨大的样本空间,丰富的样本种类,想依靠用户喜欢的东西来描述用户的特征,就先要找到样本的属性
    - 根据类似的物品推荐物品需要对物品内容的了解,比如张三喜欢了SongA,而我又知道SongA和SongB在内容|风格上是类似的,我就可以给张三推荐SongB了
    - 根据类似的人推荐物品是发现UserA和UserB他们俩喜欢的东西差不多,都喜欢SongA和SongB,那么UserA很有可能喜欢UserB也喜欢的其他的东西,可以推荐
    - 在这里我们截止到发现UserA和UserB口味差不多就可以了,后面的是推荐音乐需要做的事

##### 2018.01.03
发现推荐算法真的是一个很大的范围,包括了`根据类似的人`的推荐(协同过滤 collaboration filtering)和`根据类似的物品`的推荐(item-based|content-based filtering)等不同思路

那,在云村找到与你最搭的人的依据是什么?当然是相同的音乐口味咯,此外也可以考虑位置,性别,是否单身,年龄等等,~~啊等等( ⊙ o ⊙ )...怎么查真实年龄又是个问题~~

这个项目用不到日推歌曲那种复杂程度的推荐系统,简单一点就根据用户的各种信息(能够爬取的到的)生成一个描述该用户的feature,然后分类即可

##### 2017.12.29
user_detail和simi_user接口不通根本不是加密的锅好吗！

AES加密请求信息之后各种post并没什么效果,反而从浏览器摘下来cookie放到headers里面，get一下立刻就通了，真是的/(ㄒoㄒ)/~~

添加cookie支持

##### 2017.12.25
然而用户信息/user/detail/和喜欢同一首歌的人/song/simiUser/似乎都需要加密

使用网络上大神们提供的的加密算法

##### 2017.12.20
发现用到的几个接口，除了登录功能需要加密算法外，其他的可以直接POST|GET

所以直接使用requests吧，不用那些完善的API了

##### 2017.12.12
之前使用的是[node.js的网易云API](https://github.com/Binaryify/NeteaseCloudMusicApi)

后来为了不依赖js纯粹使用python实现，搜集了一些python的API，比如[这个](https://github.com/darknessomi/musicbox)

## 喜欢的歌曲重叠数
numpy集合操作               | 效果
:---------------------- | :----------------------------
unique(array)           | 返回去重之后的所有元素,相当于set()
intersect1d(arr1, arr2) | 返回交集元素
union1d(arr1, arr2)     | 返回并集元素
in1d(arr1, arr2)        | 返回bool数组表示arr1中的每个元素是否也在arr2中
setdiff1d(a, b)         | 返回差集元素 Ca(a∩b) 在a中但不在b中

## 网易云中省与市的代号对应关系存储在position.db中

## 可能需要使用的网易云API

##### 手机登录(手机号密码 -> uid) POST only

- `http://music.163.com/weapi/login/cellphone`
```
{
    'account': account info,
    'bindings': list of phone|email|wechat|weibo... binded,
    'code': 200,
    'profile': `User`
}
```

##### 搜索(用户名 -> uid) POST only

- `http://music.163.com/api/search/get?s={str}&type={}&offset={}&limit={}`

    >type: 1:单曲|10:专辑|100:歌手|1000:歌单|1002:用户|1004:MV|1006:歌词|1009:电台    搜索类型
    >
    >offset: 0(default)    用于搜索结果翻页
    >
    >limit: 50(default)    搜索结果数量限制

##### 获取用户详情
- `http://music.163.com/api/user/detail/{uid}`
```
`User`:{
    'code':200,
    'nickname':TEXT,
    'userId':TEXT|INT,
    'city':TEXT|INT,
    'gender':INT,
    'followed':INT(bool);
    'level':INT,
    'createTime':FLOAT,
    'createTime_str':TEXT,
    'description':TEXT,
    'avatarUrl':TEXT,
    'signature':TEXT
}
```

##### 获取用户关注列表
- `http://music.163.com/api/user/getfollows/{uid}` (BUG)
- `http://music.163.com/api/user/getfolloweds/{uid}`
```
{
    'code':200,
    'more':bool,
    'followeds|follow':[`Simple_User`, ]
}
```

<!-- ##### 获取用户动态
- `/user/event?uid=xxx&limit&offset`
```
{
    'more':bool,
    'size':int,
    'events':[`Event`]
}
``` -->

##### 获取用户歌单
- `http://music.163.com/api/user/playlist?uid={}&offset={}&limit={}`
```
{
    'code':200,
    'more':bool,
    'playlist':[`Simple_Playlist`]
}
```

##### 获取歌单详情
- `http://music.163.com/api/playlist/detail?id={}`
```
{
    'code':200,
    'privileges':list of songs info, it seems useless,
    'playlist':`Playlist`
}
 ```

##### 获取最近听这首歌的5个用户
- `http://music.163.com/api/discovery/simiUser?songid={}`
```
{
    'code':200,
    'userprofiles':[`User`,]
}
```

##### 获取音乐详情
- `http://music.163.com/api/song/detail?ids=[{},]`
```
{
    'code':200,
    'equalizers':{song1:'type',song2:'type'...} 均衡器,
    'songs':[`Song`,]
}
```

## 其他可能用到接口
- `/user/record?uid=xxx&type=0` 获取用户播放记录 type: 1: weekData|0: allData
```
{'code':-2,
 'msg':'无权访问'}
{'code':200,
 'allData|weekData':[`Record`]}
```
- `/event` 动态
- `/daily_signin?type=x` 签到(type: 0:android-3points|1:PC-2points)
- `/recommend/resource` 日推歌单
- `/recommend/songs` 日推歌曲
- `/personal_fm` 私人FM
- `/like?id=xxx&type=x` 喜欢歌曲(type: true:like|false:cancel)
- `/top/playlist/highquality?cat=tags&limit` 精品歌单(tags: 古风|流行|古典...)
- `/playlist/tracks?op=(add|del)&pid=(playlist)&tracks=(songid)` 歌单增删歌曲
- `/lyric?id=xxx` 歌词
- `/album?id=xxx` 专辑
- `/artists?id=xxx` 歌手
- `/artist/desc?id=xxx` 歌手描述
- `/comment/like?id=xxx&cid=commentidxxx&t=(1:like|0:cancel)&type=0` 点赞/取消点赞 type: (0:song|1:mv|2:playlist|3:album|4:dj)

- 获取相似
    - `/simi/artist?id=xxx`
    - `/simi/playlist?id=xxx`
    - `/simi/mv?mvid=xxx`
    - `/simi/song?id=xxx`

- 获取评论
    - `/comment/music?id=xxx&limit&offset`
    - `/comment/playlist?`
    - `/comment/album?`
    - `/comment/mv?`
    - `/comment/dj?`

## 数据结构
- Playlist:
![Playlist]()
- User:
![User]()


## Attribute-style access to dict keys
为什么要像调用一个对象的属性那样访问字典的值呢？看示例：
```python
t = {'a':1, 'long_name_key':2}
print(t['a']) # 似乎还好
print(t['long_name_key']) # 好长啊啊啊啊啊啊

t.a
t.long_name_key # 这样就能少写['']了
```
优雅的使用obj.attr吧！
有好多种方法可以做出这种效果，当然这么做会有一些[问题](https://stackoverflow.com/questions/4984647/accessing-dict-keys-like-an-attribute)，不过不在本部分讨论范围内

方法一： python中类的所有的属性都以`{attr:value}`的形式存储在`self.__dict__`中，所以给`self.__dict__`添加键值对就是给对象添加属性
```python
>>> class test(dict):
        def __init__(self, *args, **kwargs):
            # 现在test类返回的对象还只是一种单纯的dict

            # 所有送入的参数都传递给dict用于初始化
            super(dict, self).__init__(*args, **kwargs)

            # 现在test类返回的对象有了self.__dict__，经过改造，你可以理解成dict是本体
            self.__dict__ = self

>>> t = test(a=1, b=2)
>>> t.a = 3
>>> print(t.a)
3
>>> t.b
2
```
方法二： 覆盖类的私有函数`__getattr__`,`__setattr__`,`__delattr__`,`__getattribute__`,当使用`obj.attr`这个表达式时，解释器实际上会调用`obj.__getattr__(attr)`，
如果把这些 **访问、添加、删除属性的私有函数** 重定向到 **访问、添加、删除字典元素的方法** 上，
就可以做到操作属性等同于操作字典元素的效果了，而且可以简单的开关某种功能
```python
>>> class test(dict):
        __getattr__ = dict.__getitem__
        __setattr__ = dict.__setitem__
        __delattr__ = dict.__delitem__
>>> t = test(a=1, b=2, c=test({'d':3, 'e':4}))
>>> t
{'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}}
>>> t.c.d
3
>>> t.c.f = 5
>>> t
{'a': 1, 'b': 2, 'c': {'d': 3, 'e': 1, 'f': 2}}
```
方法三： 使用库[bunch](https://github.com/dsc/bunch)或者[munch](https://github.com/Infinidat/munch)
```python
>>> from bunch import bunchify # or munch
>>> t = bunchify(
                 {'a': 1,
                  'b': {'c': 2},
                  'd': ('test', {'e': 3})}
                )
>>> t.a
1
>>> t.b.c
2
>>> t.d[1].e
3
```
