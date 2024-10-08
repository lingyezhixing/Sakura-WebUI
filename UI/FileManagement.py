# 文件管理类函数
import streamlit as st
import os
import Translators
import shutil
import time

import Translators.FilePretreatment

# 创建缓存目录
def create_cache_folder():
    if os.path.exists(".\Cache\Source"):
        pass
    else:
        os.makedirs(".\Cache\Source")
    if os.path.exists(".\Cache\Temp"):
        pass
    else:
        os.makedirs(".\Cache\Temp")

# 上传文件
def upload_file(config_use):
    create_cache_folder()
    uploaded_files = st.sidebar.file_uploader("上传文件和术语表", type=["txt", "epub", "json"], accept_multiple_files=True)
    # 判断是否上传了文件
    if uploaded_files is not None and len(uploaded_files) > 0:
        # 将上传的文件统一保存到缓存目录“Cahce\Source”，不存在则创建
        for uploaded_file in uploaded_files:
            file_path = os.path.join("Cache\Source", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        pretreatment(config_use)

# 删除文件缓存
def del_file_cache(file_name, file_type, sh256):
    if file_type == "TXT":
        pd_path = os.path.join(".\Cache\TXT", sh256)
    elif file_type == "EPUB":
        pd_path = os.path.join(".\Cache\EPUB", sh256)
    while os.path.exists(pd_path):
        time.sleep(1)
        continue
    shutil.rmtree(os.path.join(".\Cache\Temp", sh256))
    # 从“Cache\Source”中删除源文件
    os.remove(os.path.join(".\Cache\Source", file_name))
    if os.path.exists(os.path.join(".\Cache\Source", os.path.splitext(file_name)[0] + ".json")):
        os.remove(os.path.join(".\Cache\Source", os.path.splitext(file_name)[0] + ".json"))

# 文件预处理
def pretreatment(config_use):
    # 判断缓存目录“Cahce\Temp”是否存在，不存在则创建
    if os.path.exists(".\Cache\Temp"):
        pass
    else:
        os.makedirs(".\Cache\Temp")
    pretreatment_page = st.sidebar.empty()
    with pretreatment_page.container():
        markdown_text = st.sidebar.markdown("### 文件预处理")
        progress_bar = st.sidebar.progress(0)
        if os.path.exists(".\Cache\Source"):
            file_list = os.listdir(".\Cache\Source")
            for file in file_list:
                # 判断文件类型
                if file.endswith(".txt"):
                    file_path = os.path.join(".\Cache\Source", file)
                    sha256 = Translators.FilePretreatment.get_sha256(file_path)
                    # 判断文件是否已经处理过
                    if os.path.exists(os.path.join(".\Cache\Temp", sha256)):
                        progress_bar.progress((file_list.index(file) + 1) / len(file_list))
                        continue
                    data_list = Translators.FilePretreatment.TXTPretreatment(file_path, config_use['split_length'])
                    total_len = len(data_list)
                    os.mkdir(os.path.join("Cache\Temp", sha256))
                    # 将信息写入文件
                    with open(os.path.join(".\Cache\Temp", sha256, "file_info.txt"), "w", encoding="utf-8") as f:
                        f.write(f"{file}\n{file_path}\n{total_len}\nTXT")

                elif file.endswith(".epub"):
                    file_path = os.path.join(".\Cache\Source", file)
                    sha256 = Translators.FilePretreatment.get_sha256(file_path)
                    # 判断文件是否已经处理过
                    if os.path.exists(os.path.join(".\Cache\Temp", sha256)):
                        progress_bar.progress((file_list.index(file) + 1) / len(file_list))
                        continue
                    epub_texts = Translators.FilePretreatment.EPUBPretreatment(file_path, config_use['split_length'])
                    total_len = len(epub_texts)
                    os.mkdir(os.path.join("Cache\Temp", sha256))
                    # 将信息写入文件
                    with open(os.path.join(".\Cache\Temp", sha256, "file_info.txt"), "w", encoding="utf-8") as f:
                        f.write(f"{file}\n{file_path}\n{total_len}\nEPUB")
                progress_bar.progress((file_list.index(file) + 1) / len(file_list))
            pretreatment_page.empty()
            markdown_text.empty()
            progress_bar.empty()