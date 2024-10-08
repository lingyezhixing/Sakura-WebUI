import streamlit as st
import Config
import UI

def web_ui():
    global T
    # 设置页面标题
    st.sidebar.title("墨泠翻译器")
    st.sidebar.markdown('---')

    # 获取配置信息
    config_dict = Config.Management.read_config()
    config_list = list(config_dict.keys())

    # 导航栏
    if len(config_list) > 0:
        navigation = st.sidebar.selectbox(
            '功能导航:',
            ('文件翻译', '配置管理'),
            index=0
        )
    else:
        navigation = '配置管理'

    # 文件翻译
    if navigation == '文件翻译':
        # 获取配置信息
        config_dict = Config.Management.read_config()
        config_list = list(config_dict.keys())
        
        # 获取默认配置
        default_config = Config.Management.get_default_config()
        if default_config == None:
            st.sidebar.warning('未设置默认配置，建议先设置默认配置')
        
        if 'config_use' not in st.session_state:
            st.session_state['config_use'] = None
        
        if st.session_state['config_use'] == None:
            if default_config == None:
                if len(config_list) > 0:
                    index = 0
            else:
                index = config_list.index(default_config)
                st.session_state['config_use'] = config_list[index]
        else:
            index = config_list.index(st.session_state['config_use'])

        # 选择配置
        st.session_state['config_use'] = st.sidebar.selectbox(
            '选择配置:',
            config_list,
            index=index
        )

        # 在st.session_state中添加翻译控制页面的状态缓存
        if 'translation_controller' not in st.session_state:
            st.session_state['translation_controller'] = False

        # 选择文件
        UI.FileManagement.upload_file(config_dict[st.session_state['config_use']])
        
        # 翻译控制页面
        UI.TranslatorManagement.translator_management(config_dict[st.session_state['config_use']])
    
    # 配置管理
    elif navigation == '配置管理':
        # 获取配置信息
        config_dict = Config.Management.read_config()
        config_list = list(config_dict.keys())

        # 添加配置
        if len(config_list) == 0:
            st.warning('请先添加至少一个可用配置')
        UI.ConfigManagement.add_config()
        UI.ConfigManagement.config_management()