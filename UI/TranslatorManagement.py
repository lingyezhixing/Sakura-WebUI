import streamlit as st
import os
import time
import pickle
import shutil
import UI
import time
import datetime

# 显示翻译控制页面
def translator_management(config_use):
    translator_management_page = st.empty()
    
    sh256_list = os.listdir(".\Cache\\Temp")
    file_info_dict = {}
    
    # 获取文件信息
    for sh256 in sh256_list:
        with open(".\Cache\\Temp\\" + sh256 + "\\file_info.txt", "r", encoding="utf-8") as f:
            file_info = f.read().splitlines()
            file_name = file_info[0]
            file_path = file_info[1]
            total_len = int(file_info[2])
            type = file_info[3]
        file_info_dict[sh256] = {
            "file_name": file_name,
            "file_path": file_path,
            "total_len": total_len,
            "type": type
        }
    
    # 创建翻译状态指示文件
    if not os.path.exists("Cache\\translating_file_sh256.pkl"):
        with open("Cache\\translating_file_sh256.pkl", "wb") as f:
            translating_file_sh256 = None
            pickle.dump(translating_file_sh256, f)
    with open("Cache\\translating_file_sh256.pkl", "rb") as f:
        translating_file_sh256 = pickle.load(f)
        last_translating_file_sh256 = translating_file_sh256
        if translating_file_sh256 == None:
            translation_state = False
        else:
            translation_state = True
    # 开始翻译
    start, stop = st.sidebar.columns(2)
    with start:
        start_all_button = st.sidebar.button("开始翻译", key="start_all_button")
    with stop:
        stop_all_button = st.sidebar.button("停止翻译", key="stop_all_button")
    
    if start_all_button:
        if translating_file_sh256 == None:
            if len(sh256_list) > 0:
                translating_file_sh256 = sh256_list[0]
                with open("Cache\\Translating_info.pkl", "wb") as f:
                    pickle.dump({
                        "file_path": file_info_dict[translating_file_sh256]['file_path'],
                        "file_type": file_info_dict[translating_file_sh256]['type'],
                        "config": config_use}, f)
                translation_state = True
                with open("Cache\\translating_file_sh256.pkl", "wb") as f:
                    pickle.dump(translating_file_sh256, f)
            else:
                st.warning("没有文件需要翻译")
                time.sleep(1)
                st.session_state['navigation'] = '文件翻译'
                st.rerun()

    # 在st.session_state中创建所有进度条、markdown文字
    if 'progress_bars' not in st.session_state:
        st.session_state.progress_bars = {bar: False for bar in sh256_list}
    if 'markdown_texts' not in st.session_state:
        st.session_state.markdown_texts = {markdown: False for markdown in sh256_list}
    if 'start_buttons' not in st.session_state:
        st.session_state.start_buttons = {button: False for button in sh256_list}
    if 'delete_buttons' not in st.session_state:
        st.session_state.delete_buttons = {button: False for button in sh256_list}
    
    with translator_management_page.container():
        # 展示正在翻译的文件
        if translation_state:
            with st.expander(f"**正在翻译**： {file_info_dict[translating_file_sh256]['file_name']}", expanded=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{file_info_dict[translating_file_sh256]['file_name']}**")

                    # 获取翻译进度
                    if file_info_dict[translating_file_sh256]['type'] == "TXT":
                        if os.path.exists(os.path.join(".\Cache\TXT", translating_file_sh256, "translated_texts")):
                            # 获取该文件夹中translated_texts文件夹中的文件数量
                            translated_texts_count = len(os.listdir(os.path.join(".\Cache\TXT", translating_file_sh256, "translated_texts")))
                        else:
                            translated_texts_count = 0
                    elif file_info_dict[translating_file_sh256]['type'] == "EPUB":
                        if os.path.exists(os.path.join(".\Cache\EPUB", translating_file_sh256, "translated_texts")):
                            # 获取该文件夹中translated_texts文件夹中的文件数量
                            translated_texts_count = len(os.listdir(os.path.join(".\Cache\EPUB", translating_file_sh256, "translated_texts")))
                        else:
                            translated_texts_count = 0
                    
                    if os.path.exists(f"Cache\\Time\\{translating_file_sh256}") == False:
                        with open(f"Cache\\Time\\{translating_file_sh256}", "wb") as f:
                            pickle.dump((time.time(), translated_texts_count), f)
                    
                    # 计算翻译进度
                    progress = translated_texts_count / file_info_dict[translating_file_sh256]['total_len'] * 100

                    # 显示翻译进度文字
                    st.session_state.markdown_texts[translating_file_sh256] = st.markdown(f"**翻译进度**：{progress:.2f}%       **剩余时间**：——")

                    # 显示翻译进度条
                    st.session_state.progress_bars[translating_file_sh256] = st.progress(progress / 100)
                with col2:
                    st.session_state.delete_buttons[translating_file_sh256] = st.button("删除任务", key=f"delete_{translating_file_sh256}")

        n = 1
        for sh256 in sh256_list:
            if sh256 == translating_file_sh256:
                continue
            if translation_state:
                state = '排队中'
                expanded = False
            else:
                state = '暂停中'
                if n == 1:
                    expanded = True
                    n += 1
                else:
                    expanded = False
            with st.expander(f"**{state}**： {file_info_dict[sh256]['file_name']}", expanded=expanded):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{file_info_dict[sh256]['file_name']}**")

                    # 获取翻译进度
                    if file_info_dict[sh256]['type'] == "TXT":
                        if os.path.exists(os.path.join(".\Cache\TXT", sh256, "translated_texts")):
                            # 获取该文件夹中translated_texts文件夹中的文件数量
                            translated_texts_count = len(os.listdir(os.path.join(".\Cache\TXT", sh256, "translated_texts")))
                        else:
                            translated_texts_count = 0
                    elif file_info_dict[sh256]['type'] == "EPUB":
                        if os.path.exists(os.path.join(".\Cache\EPUB", sh256, "translated_texts")):
                            # 获取该文件夹中translated_texts文件夹中的文件数量
                            translated_texts_count = len(os.listdir(os.path.join(".\Cache\EPUB", sh256, "translated_texts")))
                        else:
                            translated_texts_count = 0
                    
                    # 计算翻译进度
                    progress = translated_texts_count / file_info_dict[sh256]['total_len'] * 100

                    # 显示翻译进度文字
                    st.session_state.markdown_texts[sh256] = st.markdown(f"**翻译进度**：{progress:.2f}%")

                    # 显示翻译进度条
                    st.session_state.progress_bars[sh256] = st.progress(progress / 100)
                with col2:
                    # 开始翻译按钮
                    st.session_state.start_buttons[sh256] = st.button("开始翻译", key='start_translated_' + sh256)
                    # 删除任务按钮
                    st.session_state.delete_buttons[sh256] = st.button("删除任务", key='delete_' + sh256)
                    if st.session_state.start_buttons[sh256]:
                        translating_file_sh256 = sh256
                        with open("Cache\\Translating_info.pkl", "wb") as f:
                            pickle.dump({
                                "file_path": file_info_dict[translating_file_sh256]['file_path'],
                                "file_type": file_info_dict[translating_file_sh256]['type'],
                                "config": config_use}, f)
                        with open("Cache\\translating_file_sh256.pkl", "wb") as f:
                            pickle.dump(translating_file_sh256, f)
                        # 刷新页面
                        translator_management_page.empty()
                        st.session_state['navigation'] = '文件翻译'
                        st.rerun()
                
                    if st.session_state.delete_buttons[sh256]:
                        file_name = file_info_dict[sh256]['file_name']
                        # 从缓存目录中删除任务
                        if file_info_dict[sh256]['type'] == "TXT":
                            # 删除缓存文件夹
                            shutil.rmtree(os.path.join(".\Cache\TXT", sh256))
                        elif file_info_dict[sh256]['type'] == "EPUB":
                            # 删除缓存文件夹
                            shutil.rmtree(os.path.join(".\Cache\EPUB", sh256))
                        shutil.rmtree(os.path.join(".\Cache\Temp", sh256))
                        # 从“Cache\Source”中删除源文件
                        os.remove(os.path.join(".\Cache\Source", file_name))
                        # 从sh256_list和file_info_dict中删除任务
                        sh256_list.remove(sh256)
                        del file_info_dict[sh256]
                        # 刷新页面
                        translator_management_page.empty()
                        st.session_state['navigation'] = '文件翻译'
                        st.rerun()
        
        if translation_state:
            for i in os.listdir(".\Cache\\Time"):
                if file_name != translating_file_sh256:
                    # 删除文件
                    os.remove(f"Cache\\Time\\{i}")
                else:
                    # 获取开始时间和当时翻译的文本数量
                    with open(f"Cache\\Time\\{translating_file_sh256}", "rb") as f:
                        start_time, num = pickle.load(f)
            while translating_file_sh256 == last_translating_file_sh256 and translation_state:
                # 获取翻译进度
                if file_info_dict[translating_file_sh256]['type'] == "TXT":
                    if os.path.exists(os.path.join(".\Cache\TXT", translating_file_sh256, "translated_texts")):
                        # 获取该文件夹中translated_texts文件夹中的文件数量
                        translated_texts_count = len(os.listdir(os.path.join(".\Cache\TXT", translating_file_sh256, "translated_texts")))
                    else:
                        translated_texts_count = 0
                elif file_info_dict[translating_file_sh256]['type'] == "EPUB":
                    if os.path.exists(os.path.join(".\Cache\EPUB", translating_file_sh256, "translated_texts")):
                        # 获取该文件夹中translated_texts文件夹中的文件数量
                        translated_texts_count = len(os.listdir(os.path.join(".\Cache\EPUB", translating_file_sh256, "translated_texts")))
                    else:
                        translated_texts_count = 0
                
                if os.path.exists(f"Cache\\Time\\{translating_file_sh256}") == False:
                    with open(f"Cache\\Time\\{translating_file_sh256}", "wb") as f:
                        pickle.dump((time.time(), translated_texts_count), f)
                
                with open(f"Cache\\Time\\{translating_file_sh256}", "rb") as f:
                    start_time, num = pickle.load(f)
                
                # 计算剩余时间
                if translated_texts_count - num > 0:
                    remaining_time = (file_info_dict[translating_file_sh256]['total_len'] - translated_texts_count) * (time.time() - start_time) / (translated_texts_count - num)
                    
                    # 将剩余时间转换为时分秒格式
                    remaining_time_str = str(datetime.timedelta(seconds=remaining_time)).split('.')[0]
                else:
                    remaining_time_str = "——"
                
                # 计算翻译进度
                progress = translated_texts_count / file_info_dict[translating_file_sh256]['total_len'] * 100

                # 显示翻译进度文字
                st.session_state.markdown_texts[translating_file_sh256].markdown(f"**翻译进度**：{progress:.2f}%       **剩余时间**：{remaining_time_str}")

                # 显示翻译进度条
                st.session_state.progress_bars[translating_file_sh256].progress(progress / 100)
                if translated_texts_count >= file_info_dict[translating_file_sh256]['total_len']:
                    st.session_state.markdown_texts[translating_file_sh256].markdown("**正在整合文本并删除缓存文件**")
                    file_name = file_info_dict[translating_file_sh256]['file_name']
                    file_type = file_info_dict[translating_file_sh256]['type']

                    st.toast(f"文件 {file_name} 翻译完成！")
                    
                    UI.FileManagement.del_file_cache(file_name, file_type, translating_file_sh256)
                    # 从sh256_list和file_info_dict中删除任务
                    sh256_list.remove(translating_file_sh256)
                    del file_info_dict[translating_file_sh256]
                    
                    if translation_state:
                        # 设置translating_file_sh256
                        if len(sh256_list) > 0:
                            translating_file_sh256 = sh256_list[0]
                        else:
                            translating_file_sh256 = None
                            translation_state = False
                            with open("Cache\\Translating_info.pkl", "wb") as f:
                                pickle.dump(None, f)
                            with open("Cache\\translating_file_sh256.pkl", "wb") as f:
                                pickle.dump(None, f)
                    else:
                        translating_file_sh256 = None

                    continue
                
                # 处理其余按钮事件
                for sh256 in sh256_list:
                    if st.session_state.start_buttons[sh256]:
                        translating_file_sh256 = sh256
                        continue
                
                    if st.session_state.delete_buttons[sh256]:
                        if sh256 == translating_file_sh256:
                            translating_file_sh256 = None
                            with open("Cache\\Translating_info.pkl", "wb") as f:
                                pickle.dump(None, f)
                        file_name = file_info_dict[sh256]['file_name']
                        # 从缓存目录中删除任务
                        if file_info_dict[sh256]['type'] == "TXT":
                            # 删除缓存文件夹
                            shutil.rmtree(os.path.join(".\Cache\TXT", sh256))
                        elif file_info_dict[sh256]['type'] == "EPUB":
                            # 删除缓存文件夹
                            shutil.rmtree(os.path.join(".\Cache\EPUB", sh256))
                        shutil.rmtree(os.path.join(".\Cache\Temp", sh256))
                        # 从“Cache\Source”中删除源文件
                        os.remove(os.path.join(".\Cache\Source", file_name))
                        # 从sh256_list和file_info_dict中删除任务
                        sh256_list.remove(sh256)
                        del file_info_dict[sh256]
                        if len(sh256_list) > 0:
                            translating_file_sh256 = sh256_list[0]
                        else:
                            translating_file_sh256 = None
                            translation_state = False
                            with open("Cache\\Translating_info.pkl", "wb") as f:
                                pickle.dump(None, f)
                            with open("Cache\\translating_file_sh256.pkl", "wb") as f:
                                pickle.dump(None, f)
                        continue
                
                # 处理停止按钮事件
                if stop_all_button:
                    translation_state = False
                    translating_file_sh256 = None
                    with open("Cache\\Translating_info.pkl", "wb") as f:
                        pickle.dump(None, f)
                    with open("Cache\\translating_file_sh256.pkl", "wb") as f:
                        pickle.dump(None, f)
                    continue

                time.sleep(0.05)

            if translating_file_sh256 is not None:
                with open("Cache\\Translating_info.pkl", "wb") as f:
                    pickle.dump({
                        "file_path": file_info_dict[translating_file_sh256]['file_path'],
                        "file_type": file_info_dict[translating_file_sh256]['type'],
                        "config": config_use}, f)
                with open("Cache\\translating_file_sh256.pkl", "wb") as f:
                    pickle.dump(translating_file_sh256, f)
            
            # 刷新页面
            translator_management_page.empty()
            st.session_state['navigation'] = '文件翻译'
            st.rerun()