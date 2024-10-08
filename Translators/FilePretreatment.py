import os
import re
import hashlib
import pickle
import logging
import fnmatch
import zipfile
import shutil

# 设置Logging等级和格式
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log', filemode='w')

# 定义一个函数用于获取文件的sha256哈希值
def get_sha256(file_path):
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"TXT错误：获取文件sha256哈希值时发生错误: {e}")
        return None

# 寻找EPUB文件中的所有html文件
def find_all_htmls(root_dir):
    try:
        html_files = []
        for foldername, subfolders, filenames in os.walk(root_dir):
            for extension in ['*.html', '*.xhtml', '*.htm']:
                for filename in fnmatch.filter(filenames, extension):
                    file_path = os.path.join(foldername, filename)
                    html_files.append(file_path)
        return html_files
    except Exception as e:
        logging.error(f"EPUB错误：寻找EPUB文件中的所有html文件时发生异常：{e}")
        return None

# 获取EPUB单文件文本
def get_html_text_list(epub_html_path, split_length):
    def clean_text(text):
        text = re.sub(r'<rt[^>]*?>.*?</rt>', '', text)
        text = re.sub(r'<[^>]*>|\n', '', text)
        return text
    try:
        data_list = []
        with open(epub_html_path, 'r', encoding='utf-8') as f:
            file_text = f.read()
            matches = re.finditer(r'<(h[1-6]|p|a|title).*?>(.+?)</\1>', file_text, flags=re.DOTALL)
            if not matches:
                logging.info("这可能是个结构文件，跳过")
                return data_list, file_text

            groups = []
            text = ''
            pre_end = 0
            for match in matches:
                match_text = clean_text(match.group(2))
                if len(text + match_text) <= split_length or text == '':
                    new_text = match_text
                    if new_text:
                        # 保存匹配的必要信息
                        groups.append({
                            'full_match': match.group(0),
                            'start': match.start(),
                            'end': match.end(),
                            'group_2': match.group(2)
                        })
                        text += '\n' + new_text
                else:
                    data_list.append((text, groups, pre_end))
                    pre_end = groups[-1]['end']
                    new_text = match_text
                    if new_text:
                        groups = [{
                            'full_match': match.group(0),
                            'start': match.start(),
                            'end': match.end(),
                            'group_2': match.group(2)
                        }]
                        text = match_text
                    else:
                        groups = []
                        text = ''

            if text:
                data_list.append((text, groups, pre_end))
        return data_list, file_text
    except Exception as e:
        logging.error(f"EPUB错误：获取EPUB单文件文本发生异常：{e}")
        return None, None

def TXTPretreatment(txt_book_path, split_length):
    # 获取TXT文本
    def get_list(txt_book_path, split_length, encoding):
        with open(txt_book_path, 'r', encoding=encoding) as f:
            data = f.read().strip()
        data_raw = re.sub('\n+', '\n', data)
        data_lines = data_raw.strip().split("\n")

        data_list = []
        i = 0
        num = 1
        while i < len(data_lines):
            text = ""
            while len(text) < split_length:
                if i >= len(data_lines):
                    break
                if len(text) > max(-len(data_lines[i]) + split_length, 0):
                    break
                text += data_lines[i] + "\n"
                i += 1
            text = text.strip()
            data_list.append([num, text])
            num += 1

        newline_counts = []
        with open(txt_book_path, 'r', encoding=encoding) as f:
            n = 0
            for line in f:
                if line.strip() == '':
                    n += 1
                else:
                    newline_counts.append(n)
                    n = 0
            newline_counts.append(n)
        return data_raw, data_list, newline_counts

    try:
        sha256 = get_sha256(txt_book_path)
        os.makedirs(os.path.join(".\Cache\TXT", sha256))
        try:
            data_raw, data_list, newline_counts = get_list(txt_book_path, split_length, 'utf-8')
        except:
            data_raw, data_list, newline_counts = get_list(txt_book_path, split_length, 'gbk')
        with open(os.path.join(".\Cache\TXT", sha256, "data_raw.pkl"), 'wb') as f:
            pickle.dump(data_raw, f)
        with open(os.path.join(".\Cache\TXT", sha256, "data_list.pkl"), 'wb') as f:
            pickle.dump(data_list, f)
        with open(os.path.join(".\Cache\TXT", sha256, "newline_counts.pkl"), 'wb') as f:
            pickle.dump(newline_counts, f)
        with open(os.path.join(".\Cache\TXT", sha256, "txt_book_path.pkl"), 'wb') as f:
            pickle.dump(txt_book_path, f)
        
        if os.path.exists(os.path.join(".\Cache\TXT", sha256, "translated_texts")) == False:
            os.makedirs(os.path.join(".\Cache\TXT", sha256, "translated_texts"), exist_ok=True)
        
        # 检查字典文件是否存在
        dict_file_path = os.path.join(os.path.dirname(txt_book_path), os.path.basename(txt_book_path)[:-4] + '.json')
        if os.path.exists(dict_file_path):
            # 移动到缓存目录
            shutil.move(dict_file_path, os.path.join(".\Cache\TXT", sha256, 'dict.json'))
        else:
            logging.info("未找到字典文件，跳过")
        
        return data_list

    except Exception as e:
        logging.error(f"TXT错误：获取分段失败: {e}")
        return None

def EPUBPretreatment(epub_book_path, split_length):
    try:
        sha256 = get_sha256(epub_book_path)
        all_information = {}
        epub_texts = []
        os.makedirs(os.path.join(".\Cache\EPUB", sha256), exist_ok=True)
        with zipfile.ZipFile(epub_book_path, "r") as f:
            f.extractall(os.path.join(".\Cache\EPUB", sha256, "temp"))
        all_htmls = find_all_htmls(os.path.join(".\Cache\EPUB", sha256, "temp"))
        n = 1 # 文件索引
        j = 0 # 分段对应的实时索引
        start_j = j # 本次分段的起始索引
        for html_path in all_htmls:
            data_list, file_text = get_html_text_list(html_path, split_length)
            if len(data_list) == 0:
                logging.info("这可能是个结构文件，跳过")
                continue
            for text, groups, pre_end in data_list:
                text = text.split("\n")
                newline_counts = []
                num = 0
                for line in text:
                    if line.strip() == '':
                        num += 1
                    else:
                        newline_counts.append(num)
                        num = 0
                newline_counts.append(num)
                text = [line for line in text if line.strip() != '']
                
                # 纠正文本重复错误
                if newline_counts[0] == 1:
                    if len(text) > 1:
                        if text[0] == text[1]:
                            text = text[1:]
                            newline_counts.pop(1)
                text = "\n".join(text)
                epub_texts.append([j, [newline_counts, text]])
                j+=1
            all_information[n] = [html_path, data_list, file_text, [start_j, j]]
            start_j = j
            n+=1

        with open(os.path.join(".\Cache\EPUB", sha256, "all_information.pkl"), "wb") as f:
            pickle.dump(all_information, f)
        with open(os.path.join(".\Cache\EPUB", sha256, "epub_texts.pkl"), "wb") as f:
            pickle.dump(epub_texts, f)
        with open(os.path.join(".\Cache\EPUB", sha256, "epub_book_path.pkl"), "wb") as f:
            pickle.dump(epub_book_path, f)
        if os.path.exists(os.path.join(".\Cache\EPUB", sha256, "translated_texts")) == False:
            os.mkdir(os.path.join(".\Cache\EPUB", sha256, "translated_texts"))
        
        # 检查字典文件是否存在
        dict_file_path = os.path.join(os.path.dirname(epub_book_path), os.path.basename(epub_book_path)[:-5] + '.json')
        if os.path.exists(dict_file_path):
            # 移动到缓存目录
            shutil.move(dict_file_path, os.path.join(".\Cache\EPUB", sha256, 'dict.json'))
        else:
            logging.info("未找到字典文件，跳过")
        
        return epub_texts
    
    except Exception as e:
        logging.error(f"EPUB错误：获取分段失败: {e}")
        return None