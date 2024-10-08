# EPUB翻译组件类
import logging
import aiohttp
import asyncio
import os
import glob
import shutil
import zipfile
import pickle
import json
from Clients import UnifiedRequest
from Clients.Timeout import TIMEOUT

# 设置Logging等级和格式
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log', filemode='w')

# 获取EPUB全书文本并按结构保存
async def get_novel_text_list(sha256):
    try:
        if os.path.exists(os.path.join(".\Cache\EPUB", sha256)):
            with open(os.path.join(".\Cache\EPUB", sha256, "all_information.pkl"), 'rb') as f:
                all_information = pickle.load(f)
            with open(os.path.join(".\Cache\EPUB", sha256, "epub_texts.pkl"), 'rb') as f:
                epub_texts = pickle.load(f)
            
            # 遍历同样目录下的translated_texts文件夹
            if os.path.exists(os.path.join(".\Cache\EPUB", sha256, "translated_texts")):
                cache_data_list = []
                for file in os.listdir(os.path.join(".\Cache\EPUB", sha256, "translated_texts")):
                    # 移除已经翻译过的段落
                    file_index = int(file)
                    cache_data_list.append(epub_texts[file_index])
                for i in cache_data_list:
                    if i in epub_texts:
                        epub_texts.remove(i)
            return epub_texts
    except Exception as e:
        logging.error(f"EPUB错误：获取分段失败: {e}")
        return None

# 定义EPUB翻译逻辑控制函数
async def process_control(sha256, session, server, i, system_prompt, preset_prompt, paragraph, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens, retry_count=0):
    try:
        newline_counts = paragraph[0]
        paragraph = paragraph[1]

        # 原文行数对比前的预处理
        original_lines = paragraph
        original_lines = original_lines.split("\n")
        original_lines = [line for line in original_lines if line.strip() != '']

        while retry_count < max_retry_count:
            translated_paragraph, completion_tokens = await UnifiedRequest.translate_paragraph_request(session, server, system_prompt, preset_prompt, paragraph, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens)
            if translated_paragraph is None:
                return None
            
            total_completion_tokens += completion_tokens

            # 译文行数对比前的预处理
            translated_lines = translated_paragraph
            translated_lines = translated_lines.split("\n")
            translated_lines = [line for line in translated_lines if line.strip() != '']

            # 比较原文和译文行数
            if len(original_lines) != len(translated_lines):
                logging.error(f"原文和译文行数不一致，原文行数：{len(original_lines)}，译文行数：{len(translated_lines)}\n原文：{paragraph}\n译文：{translated_paragraph}")
                retry_count += 1
                continue
            else:
                with open(os.path.join(".\Cache\EPUB", sha256, "translated_texts", f"{i}"), 'wb') as f:
                    pickle.dump([i, [newline_counts, translated_paragraph]], f)
                return total_completion_tokens
        # 逐行翻译
        logging.error(f"尝试{retry_count+1}次后原文和译文行数仍然不一致，原文行数：{len(original_lines)}，译文行数：{len(translated_lines)}\n原文：{paragraph}\n译文：{translated_paragraph}")
        logging.error(f"尝试逐行翻译")
        translated_paragraph, completion_tokens = await UnifiedRequest.translate_line_request(session, server, system_prompt, preset_prompt, paragraph, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens)
        if translated_paragraph is None:
            return None
        # 比较原文和译文行数
        translated_lines = translated_paragraph
        translated_lines = translated_lines.split("\n")
        translated_lines = [line for line in translated_lines if line.strip() != '']

        if len(original_lines) != len(translated_lines):
            logging.error(f"逐行翻译后原文和译文行数仍然不一致，原文行数：{len(original_lines)}，译文行数：{len(translated_lines)}\n原文：{paragraph}\n译文：{translated_paragraph}")

        with open(os.path.join(".\Cache\EPUB", sha256, "translated_texts", f"{i}"), 'wb') as f:
            pickle.dump([i, [newline_counts, translated_paragraph]], f)
        total_completion_tokens += completion_tokens
        return total_completion_tokens
    except Exception as e:
        logging.error(f"EPUB错误：翻译逻辑核心出错：{e}")
        return None

# 定义并发量控制函数
async def bound_fetch(sha256, semaphore, session, server, i, system_prompt, preset_prompt, paragraph, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens):
    async with semaphore:
        return await process_control(sha256, session, server, i, system_prompt, preset_prompt, paragraph, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens)

# 定义EPUB翻译后文本整合函数
def integration(sha256):
    try:
        if os.path.exists("Result") == False:
            os.mkdir("Result")
        translated_texts = []
        for file in os.listdir(os.path.join(".\Cache\EPUB", sha256, "translated_texts")):
            with open(os.path.join(".\Cache\EPUB", sha256, "translated_texts", file), 'rb') as f:
                translated_texts.append(pickle.load(f))
        translated_texts.sort(key=lambda x: x[0])

        with open(os.path.join(".\Cache\EPUB", sha256, "all_information.pkl"), 'rb') as f:
            all_information = pickle.load(f)

        for html_file_index in range(1, len(all_information) + 1):
            translated = ''
            html_path, data_list, file_text, js = all_information[html_file_index]
            html_translated_texts = translated_texts[js[0]:js[1]]
            n = 0

            for html_translated_text in html_translated_texts:
                newline_counts = html_translated_text[1][0]
                translated_text = html_translated_text[1][1].strip().split('\n')
                translated_text = [line for line in translated_text if line.strip() != '']
                translated_paragraph = ''
                for i in range(len(translated_text)):
                    if i == 0:
                        translated_paragraph += "\n" * newline_counts[i]
                    else:
                        translated_paragraph += "\n" * (int(newline_counts[i]) + 1)
                    translated_paragraph += translated_text[i]
                translated_paragraph += "\n" * (int(newline_counts[-1]))
                translated_text = translated_paragraph.split('\n')

                text, groups, pre_end = data_list[n]
                if len(translated_text) < len(groups):
                    translated_text += [''] * (len(groups) - len(translated_text))
                else:
                    translated_text = translated_text[:len(groups) - 1] + ['<br/>'.join(translated_text[len(groups) - 1:])]

                for t, group in zip(translated_text, groups):
                    # 使用之前保存的字典信息替换文本
                    t = group['full_match'].replace(group['group_2'], t)
                    translated += file_text[pre_end:group['start']] + t
                    pre_end = group['end']
                n += 1

            translated += file_text[data_list[-1][1][-1]['end']:]
            with open(html_path, 'w', encoding='utf-8') as fout:
                fout.write(translated)

        # 获取翻译后的保存路径
        with open(os.path.join(".\Cache\EPUB", sha256, "translated_save_path.pkl"), 'rb') as f:
            translated_save_path = pickle.load(f)
        with zipfile.ZipFile(translated_save_path, 'w', zipfile.ZIP_DEFLATED) as f:
            for file_path in glob.glob(os.path.join(".\Cache\EPUB", sha256, "temp/**"), recursive=True):
                if not os.path.isdir(file_path):
                    relative_path = os.path.relpath(file_path, os.path.join(".\Cache\EPUB", sha256, "temp"))
                    f.write(file_path, relative_path)

        shutil.rmtree(os.path.join(".\Cache\EPUB", sha256))

    except Exception as e:
        logging.error(f"EPUB错误：翻译后整合出错: {e}")

# 获取翻译后的保存路径
async def get_translated_save_path(sha256, session, server, system_prompt, preset_prompt, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens = 0):
    try:
        with open(os.path.join(".\Cache\EPUB", sha256, "epub_book_path.pkl"), "rb") as f:
            epub_book_path = pickle.load(f)
        base_name = os.path.basename(epub_book_path)
        title = base_name[:-5]
        # 调用段落翻译用于标题翻译
        translated_title, completion_tokens = await UnifiedRequest.translate_paragraph_request(session, server, system_prompt, preset_prompt, title, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens)
        if translated_title is None:
            return None
        
        epub_book_name = translated_title + '.epub'
        translated_save_path = os.path.join("Result", epub_book_name)
        with open(os.path.join(".\Cache\EPUB", sha256, "translated_save_path.pkl"), 'wb') as f:
            pickle.dump(translated_save_path, f)
        total_completion_tokens += completion_tokens
        return total_completion_tokens
    except Exception as e:
        logging.error(f"EPUB错误：获取翻译后的保存路径出错: {e}")
        return None

# 定义EPUB翻译主函数
async def translation(sha256, config):
    try:
        # 获取配置文件
        server = config['server']
        system_prompt = config['system_prompt']
        preset_prompt = config['preset_prompt']
        model = config['model']
        temperature = config['temperature']
        top_p = config['top_p']
        frequency_penalty = config['frequency_penalty']
        max_retry_count = config['max_retry_count']
        Concurrent_quantity = config['Concurrent_quantity']
        # 创建异步锁
        semaphore = asyncio.Semaphore(Concurrent_quantity)

        if os.path.exists(".\Cache\EPUB") == False:
            if not os.path.exists(".\Cache"):
                os.mkdir(".\Cache")
            os.mkdir(".\Cache\EPUB")
        
        # 检查字典文件是否存在
        dict_file_path = os.path.join(".\Cache\EPUB", sha256, 'dict.json')
        if os.path.exists(dict_file_path):
            with open(dict_file_path, 'r', encoding='utf-8') as f:
                dict_data = json.load(f)
        else:
            dict_data = []
        
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            tasks = []
            epub_texts = await get_novel_text_list(sha256)
            if epub_texts == None:
                    return None
            if os.path.exists(os.path.join(".\Cache\EPUB", sha256, "translated_save_path.pkl")):
                completion_token = 0
            else:
                completion_token = await get_translated_save_path(sha256, session, server, system_prompt, preset_prompt, model, temperature, top_p, frequency_penalty, max_retry_count)
            
            for i, paragraph in epub_texts:
                if len(dict_data) > 0:
                    dict_info_use = []
                    gpt_dict_text_list = []
                    for dict_info in dict_data:
                        if dict_info["src"] in paragraph[1]:
                            dict_info_use.append(dict_info)
                    if len(dict_info_use) > 0:
                        for dict_info in dict_info_use:
                            src = dict_info['src']
                            dst = dict_info['dst']
                            info = dict_info['info'] if "info" in dict_info.keys() else None
                            if info:
                                single = f"{src}->{dst} #{info}"
                            else:
                                single = f"{src}->{dst}"
                            gpt_dict_text_list.append(single)

                        gpt_dict_raw_text = "\n".join(gpt_dict_text_list)
                    else:
                        gpt_dict_raw_text = ""
                else:
                    gpt_dict_raw_text = ""
                
                # 将preset_prompt中的{DICT}替换为gpt_dict_raw_text
                if model == "Sakura-14b-qwen2.5-v1.0-iq4xs":
                    if gpt_dict_raw_text == "":
                        preset_prompt = "将下面的日文文本翻译成中文："
                    else:
                        preset_prompt = preset_prompt.replace("{DICT}", gpt_dict_raw_text)
                else:
                    preset_prompt = preset_prompt.replace("{DICT}", gpt_dict_raw_text)

                logging.debug(f"EPUB翻译提示词：{preset_prompt}")

                task = asyncio.ensure_future(bound_fetch(sha256, semaphore, session, server, i, system_prompt, preset_prompt, paragraph, model, temperature, top_p, frequency_penalty, max_retry_count, total_completion_tokens = 0))
                tasks.append(task)
            results = await asyncio.gather(*tasks)
            for result in results:
                if result is None:
                    return None
            completion_tokens = sum(result for result in results) + completion_token

            integration(sha256)
            
        return completion_tokens
    except Exception as e:
        logging.error(f"EPUB错误：EPUB翻译主函数发生错误: {e}")
        return None