# Scripts

$$
追(tou)求(lan)效(mo)率(yu)是进步的动力💩
$$

##### Setup
- The cross-platform [rest reminder](<rest reminder/README.md>) has its own double-click launchers and isolated Python environment. Use its setup instructions instead of the legacy setup below.
- add the directory of `\libraries` to PYTHONPATH to use some utility functions in `ez.py`
- install `git` as `ez.py` uses `git` to get the name of the repository

---

### 仍有用

- backslash to slash："\\"转"/"
- batch rename：批量命名文件，例如替换字符串、插入前缀和后缀、根据歌曲名字填入metadata
- categorize videos：将游戏录像根据前缀来分类到不同文件夹里面
- convert potplayer bookmark file to youtube timestamps：将PotPlayer的Bookmark文件转成YouTube可以识别的Chapters格式
- google drive click error list：自动清除google drive for desktop一直弹出来的error list
    - 重装整个Google Drive以后就很少再弹出这个error了，不过有时候同步大量小文件的时候还是会出问题
- infowriter to pbf：将obs插件inforwriter生成的文件转换成PotPlayer可以识别的Bookmark文件，这样在播放视频就可以看到那些在录的时候标记的highlight时刻
- minecraft add textures to json：将minecraft overlay texture pack里的json model自动添加对应的texture，这样能确保用的是expected的texture，不会因为换了个base texture pack就变了样
- move repeated songs：以前下载的音乐全部放在同一层文件夹，结果导致很多文件重名，这个脚本就是结合Search Everything的功能，用来找出同样名字的歌曲，然后删掉重复的版本
    - 后来下载的音乐都按照“歌手/专辑名”的形式来分类以后就比较再遇到这个问题了，但偶尔也还有，因为可能音乐播放器没识别出来这首歌已经下载，于是又重复下载了一遍
- panopto subtitle conversion：将panopto的字幕转成段落形式方便阅读
- rest reminder：隔一段时间就提醒自己休息，顺便播放一首歌~
- schedule shutdown：非常简单的定时休眠指令，方便电脑定时执行来强逼自己晚上不要熬夜玩游戏
- winget helper：非常非常常用的一个脚本，我现在大部分软件的安装和升级都用winget，而这个脚本就是为了省去我打winget指令的麻烦，只需要打软件名的关键字就可以找到对应pacakage name，然后直接自动安装/升级

### 很少用 / 没再用

> ***All good things must come to an end.***
> 
- gen scores：HKOI砌分
    - 自从那唯一一次HKOI砌分以后就没再用过了
- j4 to j7：将j4的各种info转成j7，以及搬data
    - 搬完一次以后就没再用了（总不可能经常搬judge嘛）
- J8 transfer subtask：J2搬迁到J8时候填写subtask信息的半自动脚本
- web scraping：简单爬虫，曾经用来爬取过steam游戏价格，或者一些电脑的配置清单来方便比较哪台电脑更值得买
- mp3 metadata filler：给一些没有歌手、歌曲名、专辑名信息的mp3文件填入信息
    - 找到了更方便的软件Music Tag以后就没再用了
- fill in mp3 info from ncm：从网易云音乐获取歌曲信息并填入mp3当中
    - 同样也是找到了更方便的软件Music Tag，所以就不再用了
- netease music partner：网易云合伙人打卡脚本
    - 直接用安卓模拟器自带的macro功能感觉更加方便
- printing pages：想双面打印，但是打印机又不能自动翻面时候 的 打印页面顺序指引
    - 后来买了一部可以自动双面打印的打印机就没有再用了
- auto connect cuhk wired network：自动连接中大有线网
    - 已经转移去一个[单独的repo](https://github.com/EagleZhen/CUHK-Wired-Network-Auto-Login)开发了
- casting：旧的C++版，利用scrcpy和sndcpy的指令，方便开启Android设备无线投屏和投声音
    - 已经转移去一个[单独的repo](https://github.com/EagleZhen/android-screen-casting)开发了
- share android screen and audio to pc：新的python版，利用scrcpy和sndcpy的指令，方便开启Android设备无线投屏和投声音
    - 已经转移去一个[单独的repo](https://github.com/EagleZhen/android-screen-casting)开发了
- download baidu yun：自动批量打开百度云链接方便下载
    - 自从那次需要下载超多视频以后，就没再试过需要下载那么多百度云的文件了
- GTA 5 lucky draw：GTA 5赌场抽奖，听说有个4秒定律，等4秒再抽就一定会抽到podium car
    - 抽奖结果不是很稳定，而且也很少玩了，所以就不再用了

### 未完成

- download songs from youtube and upload it to netease cloud music：从YouTube上面下载音乐并自动上传到网易云云盘
- backup netease cloud music playlist：备份歌单……以免哪天号没了就什么都没了