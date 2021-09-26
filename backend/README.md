### 团购杀手 - 用户后端

#### 开发环境准备

1. `Python`环境
   1. 本地`Python`
      1. 安装`Python`，推荐使用`3.8`以上版本，`32/64bit`均可
      2. 配置`Python`的环境变量，把`pip`加入环境变量
      3. （可选）配置`pip`的国内源：[配置方法](https://www.jianshu.com/p/dfbb90995a2c)
      4. 在项目根目录运行`pip install -r requirements.txt`，或者临时使用国内源：`pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/`
   2. 虚拟环境(`Anacoda`)
      1. （待续……）
2. `PyCharm`
   1. 下载并安装，免费版或者专业版均可，但是专业版需认证
   2. 作为工程打开`根目录/backend`
   3. 配置`Python`运行环境，本地或者`Annaconda`等
3. 浏览器
   1. 调试中暂时使用`Chrome`浏览器，通过`chromedriver.exe`控制。请安装最新版本`Chrome`浏览器，并且将`chrome`添加到环境变量。
   2. 未来将直接使用`electron`中的`Chromium`。

#### 运行方法

1. 通常方式运行：`python server.py`即可。
2. 测试美团登录功能：`python login.py`
3. 如果环境变量中没有`PORT`值，将默认使用`8000`端口，否则使用`PORT`端口。

### 重构v0.2

- [ ] 更改工程架构
  - [x] 文件整理
  - [ ] 构建结构
    - [ ] data beans
    - [x] config
    - [ ] database
    - [x] file server
    - [ ] scheduler
    - [ ] api
      - [x] main api
      - [x] user
      - [x] session
      - [x] password
      - [ ] 
- [ ] 更换规划器为`APSchedule`
  - [x] 测试
  - [ ] 融合
- [ ] 任务触发的动作可更换
- [ ] 优化任务结构
- [ ] 增加用户系统

#### API 表

`prefix: /api/v1`

1. `/` GET：API信息以及文档链接
2. 用户部分
   1. `/user` 
      1. POST：注册
      2. DELETE：删除用户
   2. `/user/<uid>` GET：获取用户信息
   3. `/user_info` POST：更新用户信息
   4. `/session`
      1. POST：登录
      2. GET：更新`access_token`
      3. DELETE：注销登录