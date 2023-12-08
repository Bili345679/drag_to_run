# drag_to_run
python 拖动执行，算一个示例，也可以用作测试调用命令行的软件，如qBittorrent的“运行外部程序”
这个项目算是从 [torrent_to_json](https://github.com/Bili345679/torrent_to_json) 单独拿出来的，网上也能很容易找到相关案例，之后可能用于辅助其他软件。

### 测试时可通过命令行输入
python python_sys_argv.py param_1 param_2 param_3 ... param_n
param_*为传入参数，如果是拖动执行，param_*为路径

## 拖动执行
顾名思义，把文件拖动到封装好的软件里，根据拖动的文件进行执行
比如上文提到的 torrent_to_json项目，就是把torrent文件拖动到封装好的软件图标上，软件就会把torrent文件转换为json文件
再或者可能有些转换图片格式的软件，把png文件拖动到封装好的图片格式转换软件上，就会生成jpg文件

## 测试调用命令行的软件
比如说 [qBittorrent](https://www.qbittorrent.org/)，这个软件是用来下载文件的，在设置里面可以设置，当新建下载任务时，调用外部软件，并且可以传入如文件名，保存路径之类的参数
这时就可以用到本软件，本软件会显示出qBittorrent调用本软件时传入的参数，用于辅助开发
https://github.com/Bili345679/drag_to_run/assets/49631330/dbd15e01-b0e7-4b41-91d9-aab4c4934a9d
