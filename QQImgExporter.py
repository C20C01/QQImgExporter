# 使用adb将手机QQ聊天中的图片复制到电脑

# 供adb访问手机QQ的图片文件夹，可能需要根据手机实际情况修改
chat_pic_path = "/storage/emulated/0/Android/data/com.tencent.mobileqq/Tencent/MobileQQ/chatpic"

# noinspection PyListCreation
tasks = []
# 确定要导出"chatpic"下面的哪些文件夹，不需要导出的文件夹可以注释掉
tasks.append("chatimg")  # 点开过的图片
tasks.append("chatraw")  # 保存过的图片
tasks.append("chatthumb")  # 没有点开看的图片

# 在电脑上保存图片的路径，留空则将保存到当前目录下的“chatpic”文件夹
save_path = ""

# 最大线程数，与CPU核心数相同即可，不是越大越好
max_workers = 16

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Semaphore


class QQImgExporter:
    def __init__(self, _root_path: str, _save_path: str, _max_workers: int):
        self.root_path = _root_path
        self.save_path = _save_path
        self.paths_path = f"{self.save_path}/path_list.tmp"
        self.tasks = Semaphore(_max_workers)
        self.executor = ThreadPoolExecutor(max_workers=_max_workers)
        self.index = 0
        self.done = 0
        self.size = 0
        self.progress_interval = 0
        self.start_time = None
        self.same_names = {}

    def start(self):
        print("生成临时文件...")
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.__save_paths()
        print(f"导出图片 (共{self.size}张)...")
        self.__export()

    def __save_paths(self):
        cmd = f"adb shell find {self.root_path} -type f ! -name '*.tmp'"
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("生成失败")
            exit(1)
        paths = result.stdout
        if not paths:
            print("没有找到图片")
            exit(1)
        with open(self.paths_path, 'w', encoding='utf-8') as f:
            f.write(paths)
        self.size = len(paths.splitlines())
        self.progress_interval = self.size // 1000

    def __export(self):
        self.start_time = datetime.now()
        with open(self.paths_path, 'r', encoding='utf-8') as f:
            for line in f:
                self.tasks.acquire()
                self.index += 1
                future = self.executor.submit(self.__pull, line.strip(), self.index)
                future.add_done_callback(lambda _: self.tasks.release())
        self.__end()

    def __end(self):
        self.executor.shutdown(wait=True)
        end_time = datetime.now()
        if os.path.exists(self.paths_path):
            os.remove(self.paths_path)
        print("\r导出完毕，"
              f"用时：{(end_time - self.start_time).total_seconds():.2f}秒，"
              f"({(self.size / (end_time - self.start_time).total_seconds()):.2f} 张/秒)\n")

    def __pull(self, path: str, index: int):
        temp_path = f"{self.save_path}/{index}"
        subprocess.run(f"adb pull -a {path} {temp_path}", capture_output=True)
        self.__rename(temp_path)
        self.__update_progress()

    def __rename(self, path: str):
        _name = datetime.fromtimestamp(os.stat(path).st_mtime).strftime("%Y%m%d_%H%M%S")
        with open(path, 'rb') as f:
            head = f.read(6)
        _type = ".gif" if head in (b'GIF87a', b'GIF89a') else ".jpg"
        try:
            os.rename(path, f"{self.save_path}/{_name}{_type}")
        except FileExistsError:
            self.__rename_exist(path, _name, _type)

    def __rename_exist(self, path: str, _name: str, _type: str):
        if _name in self.same_names:
            _index = self.same_names[_name] + 1
        else:
            _index = 1
        self.same_names[_name] = _index
        try:
            os.rename(path, f"{self.save_path}/{_name}({_index}){_type}")
        except FileExistsError:
            self.__rename_exist(path, _name, _type)

    def __update_progress(self):
        self.done += 1
        if self.done % self.progress_interval == 0:
            left = (self.size - self.done) / (self.done / (datetime.now() - self.start_time).total_seconds())
            print(f"\r{(self.done / self.size):.1%} (预计剩余时间：{left:.2f}秒)", end="")


if __name__ == "__main__":
    if chat_pic_path.endswith("/") or chat_pic_path.endswith("\\"):
        chat_pic_path = chat_pic_path[:-1]
    if not chat_pic_path.endswith("chatpic"):
        print("请检查chat_pic_path路径")
        exit(1)

    if not save_path:
        save_path = os.path.abspath(os.path.curdir) + "/chatpic"
    elif save_path.endswith("/") or save_path.endswith("\\"):
        save_path = save_path[:-1]

    max_workers = min(max(1, max_workers), 32)

    for task in tasks:
        print(f"开始导出 {task} 文件夹下的图片")
        QQImgExporter(f"{chat_pic_path}/{task}", f"{save_path}/{task}", max_workers).start()
