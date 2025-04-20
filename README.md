# QQ图片导出

（高强度地潜水后，手机总是被群友塞满了各种图片，删又舍不得删掉，所以写了这个）

👶 小孩子不懂事，写着玩的

## 使用adb将手机QQ聊天中的图片复制到电脑

1. 选一个文件夹（之后的步骤均在此文件夹中完成），克隆该仓库
2. 下载`adb`工具，放入该文件夹中；以windows为例，
   [下载工具包](https://dl.google.com/android/repository/platform-tools-latest-windows.zip)
   取出其中的`adb.exe`、`AdbWinApi.dll`、`AdbWinUsbApi.dll`即可
3. 将手机用数据线连接到电脑，并打开USB调试
4. 在该文件夹中打开命令行窗口（shift+右键），输入下面的命令并在手机上通过弹出的USB调试请求
   ```shell
   adb start-server
   ```
5. 输入下面的命令确定你的`chat_pic_path`是否需要修改。
   如果`need fix`，则要在`adb shell`中使用`cd`和`ls`命令自行寻找
   ```shell
   adb shell if [ ! -d "/storage/emulated/0/Android/data/com.tencent.mobileqq/Tencent/MobileQQ/chatpic/" ];then echo "need fix"; else echo "ok"; fi
   ```
6. 编辑`QQImgExporter.py`文件，按照其中的说明修改参数
7. 输入下面的命令运行脚本
   ```shell
   python QQImgExporter.py
   ```
