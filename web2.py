import ctypes
from multiprocessing import Process, Value, process
import signal
import streamlit as st
from pathlib import Path
import pandas as pd
import time
import os
import sys
 ##更新模型设置
config_path = "./pdfxmind/config.py"  # 更改为您的 config.py 文件的实际路径
def update_model_in_config(new_model):
    with open(config_path, "r", encoding='utf-8') as file:
        lines = file.readlines()

    with open(config_path, "w", encoding='utf-8') as file:
        for line in lines:
            if line.strip().startswith("MODEL ="):
                file.write(f'MODEL = "{new_model}"\n')
            else:
                file.write(line)
## 更新api key
def update_apikey_in_config(new_api_key):

    with open(config_path, "r", encoding='utf-8') as file:
        lines = file.readlines()

    with open(config_path, "w", encoding='utf-8') as file:
        for line in lines:
            if line.strip().startswith("APIKEYS ="):
                file.write(f'APIKEYS = ["{new_api_key}"]\n')
            else:
                file.write(line)

apikey = st.text_input('enter api-key', 'Your OpenAi Api Key')
st.write('your API key is', apikey)


option = st.selectbox(
    '选择模型',
    ('gpt-3.5-turbo', 'gpt-3.5-turbo-1106', 'gpt-4-1106-preview', 'gpt-4', 'gpt-4-32k')
)
st.write('You selected:', option)
##写入配置文件
if st.button('加载模型'):
    update_model_in_config(option)
    update_apikey_in_config(apikey)
    st.success('模型已加载')


folder = st.text_input('输入路径')
if not folder:
    st.stop()

folder = Path(folder)
if not folder.exists():
    st.warning(f'文件夹不存在[{folder}]')
    st.stop()

# 初始化 Streamlit 状态
if 'log_messages' not in st.session_state:
    st.session_state['log_messages'] = []

## 切换工作目录程序
##xmind目录
def change_working_directory(directory, folder, stop_flag):
    current_directory = os.getcwd()
    if directory == "pdfxmind":
        new_directory = os.path.join(current_directory, "pdfxmind")
        os.chdir(new_directory)
        sys.path.insert(0, new_directory)  # 将新目录添加到模块搜索路径的开头
        print(f"已切换到目录：{new_directory}")
        from paper2xmind import pdf_batch_processing
        pdf_batch_processing(folder, stop_flag)
        # 子进程的逻辑...
        st.session_state['log_messages'].append("子进程的某个日志消息")
    elif directory == "ChatPaper":
        new_directory = os.path.join(current_directory, "ChatPaper")
        os.chdir(new_directory)
        sys.path.insert(0, new_directory)  # 同样，为 ChatPaper 添加
        print(f"已切换到目录：{new_directory}")
    else:
        print("无法找到目录")

## 切换工作目录程序
##xmind目录
def change_working_directory2(directory, filepath, stop_flag):
    current_directory = os.getcwd()
    if directory == "pdfxmind":
        new_directory = os.path.join(current_directory, "pdfxmind")
        os.chdir(new_directory)
        sys.path.insert(0, new_directory)  # 将新目录添加到模块搜索路径的开头
        print(f"已切换到目录：{new_directory}")
        from paper2xmind import pdf_batch_processing
        pdf_batch_processing(filepath, stop_flag)
    elif directory == "ChatPaper":
        new_directory = os.path.join(current_directory, "ChatPaper")
        os.chdir(new_directory)
        sys.path.insert(0, new_directory)  # 同样，为 ChatPaper 添加
        print(f"已切换到目录：{new_directory}")
    else:
        print("无法找到目录")


# 初始化 Streamlit 状态
if 'process' not in st.session_state:
    st.session_state['process'] = None
# 在 Streamlit 状态中定义 stop_flag
if 'stop_flag' not in st.session_state:
    st.session_state['stop_flag'] = Value(ctypes.c_bool, False)

# 启动进程的按钮
# 启动进程的按钮
if st.button('启动处理'):
    if st.session_state['process'] is None or not st.session_state['process'].is_alive():
        st.session_state['stop_flag'].value = False
        st.session_state['process'] = Process(target=change_working_directory, args=("pdfxmind", folder, st.session_state['stop_flag']))
        st.session_state['process'].start()
        st.success('处理已启动')
    else:
        st.warning('处理已在运行中')


# 停止进程的按钮
if st.button('停止处理'):
    if st.session_state['process'] is not None and st.session_state['process'].is_alive():
        os.kill(st.session_state['process'].pid, signal.SIGTERM)  # 请求终止进程
        st.session_state['process'].join()  # 等待进程结束
        st.success('处理已停止')
    else:
        st.warning('没有运行中的处理')
st.text('启动处理为将整个目录的pdf全部合并为一个xmind文件')
st.markdown("---")



# Get file information
file_infos = pd.DataFrame([
    {
        '文件名': p.name,
        '文件大小': f"{round(p.stat().st_size / (1024 * 1024), 2)} MB",
        '修改时间': time.strftime('%Y-%m-%d', time.localtime(p.stat().st_mtime)),
        'select': False
    }
    for p in Path(folder).glob('*.pdf')
])


editor_infos = st.data_editor(file_infos)

#if editor_infos['select'].sum() <= 0:
#    st.warning('请选择至少一个文件')
#    st.stop()

if st.button('开始转换'):
    st.write('开始转换')
    files = editor_infos[editor_infos['select'] == True]['文件名'].tolist()
    for f in files:
        f = str(f)
        filepath = os.path.join(folder, f)
        st.write(filepath)
        st.session_state['stop_flag'].value = False
        st.session_state['process'] = Process(target=change_working_directory2, args=("pdfxmind", filepath, st.session_state['stop_flag']))
        st.session_state['process'].start()
        st.success('处理已启动')
    else:
        st.warning('处理已在运行中')
    st.stop()
