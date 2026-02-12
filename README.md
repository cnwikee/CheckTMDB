# CheckTMDB

每日自动更新TMDB，themoviedb、thetvdb 国内可正常连接IP，解决DNS污染，供tinyMediaManager(TMM削刮器)、Kodi的刮削器、群晖VideoStation的海报墙、Plex Server的元数据代理、Emby Server元数据下载器、Infuse、Nplayer等正常削刮影片信息。

## 一、前景

自从我早两年使用了黑群NAS以后，下了好多的电影电视剧，发现电视端无法生成正常的海报墙。查找资料得知应该是 themoviedb.org、tmdb.org 无法正常访问，因为DNS受到了污染无法正确解析到TMDB的IP，故依葫芦画瓢写了一个python脚本，每日定时通过[dnschecker](https://dnschecker.org/)查询出最佳IP，并自动同步到路由器外挂hosts，可正常削刮。

**本项目无需安装任何程序**

通过修改本地、路由器 hosts 文件，即可正常削刮影片信息。

## 文件地址

- TMDB IPv4 hosts：`https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv4` ，[链接](https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv4)
- TMDB IPv6 hosts：`https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv6` ，[链接](https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv6)

## 二、使用方法

### 2.1 手动方式

#### 2.1.1 IPv4地址复制下面的内容

```bash
# Tmdb Hosts Start
18.155.192.38               tmdb.org
18.155.192.88               api.tmdb.org
65.8.54.86                  files.tmdb.org
18.155.192.10               themoviedb.org
18.244.214.89               api.themoviedb.org
18.155.192.109              www.themoviedb.org
18.155.192.128              auth.themoviedb.org
108.138.246.73              image.tmdb.org
143.244.50.90               images.tmdb.org
44.215.137.99               imdb.com
18.155.187.37               www.imdb.com
98.82.155.134               secure.imdb.com
18.155.187.37               s.media-imdb.com
98.82.158.179               us.dd.imdb.com
18.155.187.37               www.imdb.to
44.215.137.99               origin-www.imdb.com
3.168.89.53                 ia.media-imdb.com
3.168.83.87                 thetvdb.com
108.139.0.92                api.thetvdb.com
3.168.89.53                 ia.media-imdb.com
151.101.193.16              f.media-amazon.com
18.238.192.108              imdb-video.media-imdb.com
148.113.196.166             webservice.fanart.tv
104.26.13.126               images.fanart.tv
158.69.210.98               assets.fanart.tv
104.26.13.126               fanart.tv
104.20.14.80                api.trakt.tv
104.20.14.80                trakt.tv
# Update time: 2026-02-12T18:56:51+08:00
# IPv4 Update url: https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv4
# IPv6 Update url: https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv6
# Star me: https://github.com/cnwikee/CheckTMDB
# Tmdb Hosts End

```

该内容会自动定时更新， 数据更新时间：2026-02-12T18:56:51+08:00

#### 2.1.2 IPv6地址复制下面的内容

```bash
# Tmdb Hosts Start
2600:9000:24bb:a00:10:db24:6940:93a1               tmdb.org
2600:9000:24bb:8000:10:fb02:4000:93a1              api.tmdb.org
2600:9000:204d:e800:5:da10:7440:93a1               files.tmdb.org
2600:9000:24bb:fa00:e:5373:440:93a1                themoviedb.org
2600:9000:25f0:fa00:c:174a:c400:93a1               api.themoviedb.org
2600:9000:24bb:2200:e:5373:440:93a1                www.themoviedb.org
2600:9000:24bb:1200:16:e4a1:eb00:93a1              auth.themoviedb.org
2400:52e0:1a01::1113:1                             image.tmdb.org
2400:52e0:1a01::997:1                              images.tmdb.org
2600:9000:2804:c000:1d:d7f6:39d5:bd01              ia.media-imdb.com
2600:9000:25f0:6a00:1d:d7f6:39d5:bd01              ia.media-imdb.com
2a04:4e42:400::272                                 f.media-amazon.com
2606:4700:20::681a:c7e                             images.fanart.tv
2606:4700:20::681a:c7e                             fanart.tv
2606:4700:10::6814:d50                             api.trakt.tv
2606:4700:10::6814:d50                             trakt.tv
# Update time: 2026-02-12T18:56:51+08:00
# IPv4 Update url: https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv4
# IPv6 Update url: https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv6
# Star me: https://github.com/cnwikee/CheckTMDB
# Tmdb Hosts End

```

该内容会自动定时更新， 数据更新时间：2026-02-12T18:56:51+08:00

> [!NOTE]
> 由于项目搭建在Github Aciton，延时数据获取于Github Action 虚拟主机网络环境，请自行测试可用性，建议使用本地网络环境自动设置。

#### 2.1.3 修改 hosts 文件

hosts 文件在每个系统的位置不一，详情如下：

- Windows 系统：`C:\Windows\System32\drivers\etc\hosts`
- Linux 系统：`/etc/hosts`
- Mac（苹果电脑）系统：`/etc/hosts`
- Android（安卓）系统：`/system/etc/hosts`
- iPhone（iOS）系统：`/etc/hosts`

修改方法，把第一步的内容复制到文本末尾：

1. Windows 使用记事本。
2. Linux、Mac 使用 Root 权限：`sudo vi /etc/hosts`。
3. iPhone、iPad 须越狱、Android 必须要 root。

#### 2.1.4 激活生效

大部分情况下是直接生效，如未生效可尝试下面的办法，刷新 DNS：

1. Windows：在 CMD 窗口输入：`ipconfig /flushdns`

2. Linux 命令：`sudo nscd restart`，如报错则须安装：`sudo apt install nscd` 或 `sudo /etc/init.d/nscd restart`

3. Mac 命令：`sudo killall -HUP mDNSResponder`

**Tips：** 上述方法无效可以尝试重启机器。

### 2.2 自动方式

#### 2.2.1 安装 SwitchHosts

GitHub 发行版：https://github.com/oldj/SwitchHosts/releases/latest

#### 2.2.2 添加 hosts

点击左上角“+”，并进行以下配置：

- Hosts 类型：`远程`
- Hosts 标题：任意
- URL
    - IPv4：`https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv4`
    - IPv6：`https://raw.githubusercontent.com/cnwikee/CheckTMDB/refs/heads/main/Tmdb_host_ipv6`
- 自动刷新：`1 小时`

#### 2.2.3 启用 hosts

在左侧边栏启用 hosts，首次使用时软件会自动获取内容。如果无法连接到 GitHub，可以尝试用同样的方法添加 [GitHub520](https://github.com/521xueweihan/GitHub520) hosts。

## 三、参数说明

1. 直接执行`check_tmdb_github.py`脚本，同时查询IPv4及IPv6地址，目录生成`Tmdb_host_ipv4`文件，及`Tmdb_host_ipv6`文件；
2. 带`-G` 参数执行：`check_tmdb_github.py -G`，会在`Tmdb_host_ipv4`文件，及`Tmdb_host_ipv6`文件中追加 Github IPv4 地址；

## 其他

- [x] 自学薄弱编程基础，大部分代码基于AI辅助生成，此项目过程中，主要人为解决的是：通过 [dnschecker](https://dnschecker.org/) 提交时，通过计算出正确的udp参数，获取正确的csrftoken，携带正确的referer提交！
- [x] README.md 及 部分代码 参考[GitHub520](https://github.com/521xueweihan/GitHub520)
- [x] * 本项目仅在本机测试通过，如有问题欢迎提 [issues](https://github.com/cnwikee/CheckTMDB/issues/new)
