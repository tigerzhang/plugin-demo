# 从 plugin demo 录音并监听效果

## 注意

1. 先要修改 `getMacAddress` 里面的蓝牙地址。

## 1. 录音

1. 打开 App
2. 点击 `初始化` 按钮
3. 点击 `打开蓝牙` 按钮
4. 点击 `连接` 按钮
5. 点击 `开始通话录音` 或者 `开始麦克风录音` 按钮
6. 根据需要，录音若干秒后，点击 `停止录音` 按钮
7. 等待 5秒 以上，确保录音文件生成
8. 滚屏到底部，点击 `导出文件` 按钮，导出录音文件到手机 (iOS)

## 2. 导出的文件处理

导出的文件 `plugin-demo-pcm.pcm` 是字符串格式。

1. 使用 `python3 convert_comma_split_array_to_raw.py ~/Downloads/plugin-demo-pcm.pcm 2-channels.pcm` 命令，把字符串格式的 pcm 文件转换为二进制格式的 pcm 文件。
2. 使用 `python3 split-channels.py 2-channels.pcm 0.pcm 1.pcm` 命令，把双声道的 pcm 文件分离为左声道和右声道的 pcm 文件。
3. 播放 `0.pcm` 和 `1.pcm` 文件，分别听左声道和右声道的声音。播放命令 `ffplay -autoexit -f s16le -ar 8000 1.pcm`。
