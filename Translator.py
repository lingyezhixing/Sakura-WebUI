# 翻译器
import Translators
import asyncio
import sys
import os
import pickle

if os.path.exists("Cache\\Translating_info.pkl"):
        with open("Cache\\Translating_info.pkl", "rb") as f:
            translating_file_sh256_info = pickle.load(f)
if os.path.exists("Cache\\translating_file_sh256.pkl"):
      with open("Cache\\translating_file_sh256.pkl", "rb") as f:
            translating_file_sh256 = pickle.load(f)
if translating_file_sh256_info != None:
    file_type = translating_file_sh256_info["file_type"]
    config = translating_file_sh256_info["config"]
    try:
        # 依据文件类型选择翻译器
        if file_type == 'TXT':
            completion_tokens = asyncio.run(Translators.TxtTranslate.translation(translating_file_sh256, config))
        elif file_type == 'EPUB':
            completion_tokens = asyncio.run(Translators.EpubTranslate.translation(translating_file_sh256, config))
    except KeyboardInterrupt:
        print("Terminating gracefully...")
        sys.exit(0)