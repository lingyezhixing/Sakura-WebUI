from UI import Controller
import os
import shutil
# 启动后台翻译控制器
def main():
    # 重置时间指示文件夹
    if os.path.exists(f"Cache\\Time"):
        # 删除文件夹
        shutil.rmtree(f"Cache\\Time")
    # 创建文件夹
    os.makedirs(f"Cache\\Time")
    Controller.translation_controller()

if __name__ == '__main__':
    main()