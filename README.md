[![Join the chat at https://gitter.im/kyan001/Portal-Django](https://badges.gitter.im/kyan001/Portal-Django.svg)](https://gitter.im/kyan001/Portal-Django?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![stable](http://badges.github.io/stability-badges/dist/stable.svg)](http://github.com/badges/stability-badges)
[![forthebadge](http://forthebadge.com/images/badges/makes-people-smile.svg)](http://forthebadge.com)

Table of Contents
=================
* [网站地图](#网站地图)
    * [「我的进度」](#我的进度)
        * [¶ 进度属性](#-进度属性)
        * [¶ 进度状态分类](#-进度状态分类)

# 网站介绍 Intro
- 个人维护的网站，逐渐完善并增加新功能
- 以做出优质而简单的应用为目标
- 不断优化已有代码
- 实现并完善新奇想法

# 网站地图
## 「我的进度」
### ¶ 进度属性
- 进度名称：要记录的进度的名字。一般是书的名字、电影的名字或一件事情的名字。
    - 如果名字在豆瓣数据库内可查，会在新增时自动填写总数。
    - 一个进度必须要有一个进度名称。
    - 建议可以把“第一季”、“特别篇”之类的加入进度名称里。
- 进度总数：一般是书的总页数、电视剧的总集数或事情的总步数。
    - 默认是 0，代表该进度总数无穷大。
- 当前进度：代表目前完成了整个进度的多少步。一般是当前阅读到哪页书、电视剧看到第几集、或事情做到了第几步。
- 副标题：用来当作备注的地方。可以描述进度的类别，如“书”，“PDF”，“美剧”等。
    - 会被识别成书籍类的副标题有：书，书籍，book，pdf，漫画，comic，文字，doc，txt
    - 会被识别成影视类的副标题有：动画，anime，电影，movie，电视剧，tv，show，美剧，英剧，韩剧，日剧
- 链接：用来记录进度所需的链接。一般是影视剧的播放地址、书的在线观看地址、或教程的网址。
    - 链接若以 http:// 或 https:// 开头，则会自动在标题后面添加一个可点击的超链接图标。
    - 在“进度列表”或“进度详情”或“进度搜索”中点击超链接图标可以直接打开该地址。

### ¶ 进度状态分类
- 进行中：正在进行中的进度，即已经开始但尚未结束的进度。
    - 出现在“我的进度”页面的最顶部
- 追剧中：不知道总共多少集的进度
    - 总集数为 0 的进度会默认变成“追剧中”
    - 进度条永远不会到 100%，也不会自动变成已完成状态。
    - 追剧进度需要将总数改为当前进度值才可能会变成已完成状态。
- 待阅读：加入到我的进度里，但还未开始阅读。一般适用于自己将来打算看的书。
    - 当前进度值

## 「活跃度系统」

## 「用户系统」

## 「其他」
