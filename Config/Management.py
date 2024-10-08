# 配置管理类函数
import json
import os

# 获取配置文件路径
def get_config_path():
    config_path = 'Config/config.json'
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('{}')
    return config_path

# 读取配置文件
def read_config():
    config_path = get_config_path()
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    config = dict(sorted(config.items()))
    return config

# 覆写配置文件
def write_config(config):
    config_path = get_config_path()
    config = dict(sorted(config.items()))
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    return config

# 新增配置
def add_config(key, value):
    config = read_config()
    config[key] = value
    write_config(config)

# 删除配置文件
def delete_config(name):
    config = read_config()
    if name in config:
        del config[name]
        write_config(config)

# 设置默认配置
def set_default_config(name):
    if os.path.exists('Config/default_config.txt') == False:
        with open('Config/default_config.txt', 'w', encoding='utf-8') as f:
            f.write(name)
    else:
        with open('Config/default_config.txt', 'w', encoding='utf-8') as f:
            f.write(name)

# 获取默认配置
def get_default_config():
    if os.path.exists('Config/default_config.txt'):
        with open('Config/default_config.txt', 'r', encoding='utf-8') as f:
            default_config = f.read()
        return default_config
    else:
        return None

# 删除默认配置
def delete_default_config():
    if os.path.exists('Config/default_config.txt'):
        os.remove('Config/default_config.txt')