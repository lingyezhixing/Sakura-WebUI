# 配置管理
import streamlit as st
import Config
import Clients
import time
import os

# 添加新配置
def add_config():

    # 获取servers列表
    servers = Clients.UnifiedRequest.get_available_servers()

    # 创建页面
    with st.sidebar.container():
        config_name = st.text_area('输入配置名称', help='请输入配置的名称')
        server = st.selectbox('选择服务器', servers, index=0)
        submit = st.button('添加配置')

        if submit:
            # 检查配置名称是否为空
            if config_name == '':
                st.error('配置名称不能为空')
            else:
                new_config = {
                    "split_length": 500,
                    "server": server,
                    "bat_name": "Galtransl-7B-v2.6-IQ4_XS-1024x12.bat",
                    "model": "Galtransl-7B-v2.6",
                    "system_prompt": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
                    "preset_prompt": "根据以下术语表（可以为空）：\n{DICT}\n\n将下面的日文文本根据上述术语表的对应关系和备注翻译成中文：",
                    "temperature": 0.2,
                    "top_p": 0.8,
                    "frequency_penalty": 0.0,
                    "max_retry_count": 3,
                    "Concurrent_quantity": 12
                }
                # 添加配置
                Config.Management.add_config(config_name, new_config)
                st.success('配置添加成功')
                time.sleep(1)
                st.session_state['navigation'] = '配置管理'
                st.rerun()

# 配置管理页面
def config_management():
    config_management_page = st.empty()

    # 获取配置信息
    config_dict = Config.Management.read_config()
    config_list = list(config_dict.keys())

    # 获取默认配置
    default_config = Config.Management.get_default_config()

    # 获取servers列表
    servers = Clients.UnifiedRequest.get_available_servers()

    # 获取bats列表
    bat_list = os.listdir('llama-cpp')

    # 创建默认配置组件
    with config_management_page.container():
        if default_config != None:
            with st.expander(default_config + "（默认配置）", expanded=True):
                split_length = st.slider(
                    'split_length',
                    min_value=200,
                    max_value=1000,
                    step=10,
                    value=config_dict[default_config].get('split_length'),
                    help='分割后每一段的最大长度',
                    key=default_config + '_split_length'
                    )
                server = st.selectbox(
                    label='server', 
                    options=servers, 
                    index=servers.index(config_dict[default_config].get('server')),
                    help='符合OpenAI格式的模型接口',
                    key=default_config + '_server'
                    )
                bat_name = st.selectbox(
                    label='bat_name', 
                    options=bat_list, 
                    index=bat_list.index(config_dict[default_config].get('bat_name')),
                    help='bat文件名称',
                    key=default_config + '_bat_name'
                    )
                model = st.text_input(
                    'model',
                    value=config_dict[default_config].get('model'),
                    help='选择的模型名称',
                    key=default_config + '_model'
                    )
                system_prompt = st.text_area(
                    'system_prompt',
                    value=config_dict[default_config].get('system_prompt'),
                    height=5, help='系统提示语',
                    key=default_config + '_system_prompt'
                    )
                preset_prompt = st.text_area(
                    'preset_prompt',
                    value=config_dict[default_config].get('preset_prompt'),
                    height=5, help='预设提示语',
                    key=default_config + '_preset_prompt'
                    )
                temperature = st.slider(
                    'temperature',
                    min_value=0.0,
                    max_value=1.0,
                    step=0.1,
                    value=config_dict[default_config].get('temperature'),
                    help='模型参数之一，控制输出的随机性',
                    key=default_config + '_temperature'
                    )
                top_p = st.slider(
                    'top_p',
                    min_value=0.0,
                    max_value=1.0,
                    step=0.1,
                    value=config_dict[default_config].get('top_p'),
                    help='模型参数之一，控制输出的多样性',
                    key=default_config + '_top_p'
                    )
                frequency_penalty = st.slider(
                    'frequency_penalty',
                    min_value=0.0,
                    max_value=2.0,
                    step=0.1,
                    value=config_dict[default_config].get('frequency_penalty'),
                    help='模型参数之一，控制重复输出的惩罚',
                    key=default_config + '_frequency_penalty'
                    )
                max_retry_count = st.slider(
                    'max_retry_count',
                    min_value=0,
                    max_value=10,
                    step=1,
                    value=config_dict[default_config].get('max_retry_count'),
                    help='最大重试次数',
                    key=default_config + '_max_retry_count'
                    )
                Concurrent_quantity = st.slider(
                    'Concurrent_quantity',
                    min_value=1,
                    max_value=20,
                    step=1,
                    value=config_dict[default_config].get('Concurrent_quantity'),
                    help='并发数量',
                    key=default_config + '_Concurrent_quantity'
                    )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('更新配置', key='save_' + default_config):
                            config_dict[default_config] = {
                                'split_length': split_length,
                                'server': server,
                                'bat_name': bat_name,
                                'model': model,
                                'system_prompt': system_prompt,
                                'preset_prompt': preset_prompt,
                                'temperature': temperature,
                                'top_p': top_p,
                                'frequency_penalty': frequency_penalty,
                                'max_retry_count': max_retry_count,
                                'Concurrent_quantity': Concurrent_quantity
                            }
                            Config.Management.write_config(config_dict)
                            st.success('配置已保存')
                            time.sleep(0.5)
                            config_management_page.empty()
                            st.session_state['navigation'] = '配置管理'
                            st.rerun()
                with col2:
                    if st.button('删除配置', key='delete_' + default_config):
                        if len(config_dict) > 1:
                            del config_dict[default_config]
                            Config.Management.write_config(config_dict)
                            Config.Management.delete_default_config()
                            st.success('配置已删除')
                            time.sleep(0.5)
                            config_management_page.empty()
                            st.session_state['navigation'] = '配置管理'
                            st.rerun()
                        else:
                            st.error('至少保留一个配置')
        
        # 展示剩余的配置
        for config_name in config_list:
            if config_name != default_config:
                with st.expander(config_name, expanded=False):
                    split_length = st.slider(
                        'split_length',
                        min_value=200,
                        max_value=1000,
                        step=10,
                        value=config_dict[config_name].get('split_length'),
                        help='分割后每一段的最大长度',
                        key=config_name + '_split_length'
                        )
                    server = st.selectbox(
                        label='server', 
                        options=servers, 
                        index=servers.index(config_dict[config_name].get('server')),
                        help='符合OpenAI格式的模型接口',
                        key=config_name + '_server'
                        )
                    bat_name = st.selectbox(
                        label='bat_name', 
                        options=bat_list, 
                        index=bat_list.index(config_dict[config_name].get('bat_name')),
                        help='bat文件名称',
                        key=config_name + '_bat_name'
                        )
                    model = st.text_input(
                        'model',
                        value=config_dict[config_name].get('model'),
                        help='选择的模型名称',
                        key=config_name + '_model'
                        )
                    system_prompt = st.text_area(
                        'system_prompt',
                        value=config_dict[config_name].get('system_prompt'),
                        height=5, help='系统提示语',
                        key=config_name + '_system_prompt'
                        )
                    preset_prompt = st.text_area(
                        'preset_prompt',
                        value=config_dict[config_name].get('preset_prompt'),
                        height=5, help='预设提示语',
                        key=config_name + '_preset_prompt'
                        )
                    temperature = st.slider(
                        'temperature',
                        min_value=0.0,
                        max_value=1.0,
                        step=0.1,
                        value=config_dict[config_name].get('temperature'),
                        help='模型参数之一，控制输出的随机性',
                        key=config_name + '_temperature'
                        )
                    top_p = st.slider(
                        'top_p',
                        min_value=0.0,
                        max_value=1.0,
                        step=0.1,
                        value=config_dict[config_name].get('top_p'),
                        help='模型参数之一，控制输出的多样性',
                        key=config_name + '_top_p'
                        )
                    frequency_penalty = st.slider(
                        'frequency_penalty',
                        min_value=0.0,
                        max_value=2.0,
                        step=0.1,
                        value=config_dict[config_name].get('frequency_penalty'),
                        help='模型参数之一，控制重复输出的惩罚',
                        key=config_name + '_frequency_penalty'
                        )
                    max_retry_count = st.slider(
                        'max_retry_count',
                        min_value=0,
                        max_value=10,
                        step=1,
                        value=config_dict[config_name].get('max_retry_count'),
                        help='最大重试次数',
                        key=config_name + '_max_retry_count'
                        )
                    Concurrent_quantity = st.slider(
                        'Concurrent_quantity',
                        min_value=1,
                        max_value=20,
                        step=1,
                        value=config_dict[config_name].get('Concurrent_quantity'),
                        help='并发数量',
                        key=config_name + '_Concurrent_quantity'
                        )
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button('更新配置', key='save_' + config_name):
                            config_dict[config_name] = {
                                'split_length': split_length,
                                'server': server,
                                'bat_name': bat_name,
                                'model': model,
                                'system_prompt': system_prompt,
                                'preset_prompt': preset_prompt,
                                'temperature': temperature,
                                'top_p': top_p,
                                'frequency_penalty': frequency_penalty,
                                'max_retry_count': max_retry_count,
                                'Concurrent_quantity': Concurrent_quantity
                            }
                            Config.Management.write_config(config_dict)
                            st.success('配置已保存')
                            time.sleep(0.5)
                            config_management_page.empty()
                            st.session_state['navigation'] = '配置管理'
                            st.rerun()
                    with col2:
                        if st.button('删除配置', key='delete_' + config_name):
                            if len(config_list) > 1:
                                del config_dict[config_name]
                                Config.Management.write_config(config_dict)
                                st.success('配置已删除')
                                time.sleep(0.5)
                                config_management_page.empty()
                                st.session_state['navigation'] = '配置管理'
                                st.rerun()
                            else:
                                st.error('至少保留一个配置')
                    with col3:
                        if st.button('设置为默认配置', key='update_default_' + config_name):
                            Config.Management.set_default_config(config_name)
                            st.success('已设置为默认配置')
                            time.sleep(0.5)
                            config_management_page.empty()
                            st.session_state['navigation'] = '配置管理'
                            st.rerun()