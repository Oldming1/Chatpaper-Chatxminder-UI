import streamlit as st
from pathlib import Path
import pandas as pd
import time
import os
from contextlib import contextmanager
import io
import sys
import threading
import queue
from glob import glob
from queue import Queue

# 创建一个线程安全的队列
log_queue = Queue()
should_stop = False

# 在 Streamlit 应用中创建一个可更新的文本区域
log_area = st.empty()
current_log_content = ""

# 初始化captured_output
captured_output = ""
@contextmanager
def change_dir(destination):
    try:
        cwd = os.getcwd()  # 获取当前工作目录
        os.chdir(destination)  # 切换到新目录
        yield
    finally:
        os.chdir(cwd)  # 切换回原始工作目录

# 初始化状态变量
if 'run_processing' not in st.session_state:
    st.session_state['run_processing'] = False

if 'stop_processing' not in st.session_state:
    st.session_state['stop_processing'] = False


def processing_thread(folder, callback):
    try:
        relative_path_to_pdfxmind = "./pdfxmind"
        with change_dir(relative_path_to_pdfxmind):
            from paper2xmind import pdf_batch_processing
            pdf_batch_processing(folder, callback)
    finally:
        st.session_state['run_processing'] = False

def modified_pdf_batch_processing(folder):
    global should_stop
    if os.path.isdir(folder):
        xmind_path = os.path.join(folder, "summary.xmind")
        for pdf_path in glob(os.path.join(folder, '**/*.pdf'), recursive=True):
            if should_stop:
                log_queue.put("处理被中断")
                return
            # 处理 PDF 文件...
    else:
        log_queue.put("无效的路径")


folder = st.text_input('Enter the folder path')

def update_log_area():
    global current_log_content  # 引用全局变量
    while not log_queue.empty():
        message = log_queue.get()
        # 更新日志内容
        current_log_content += "\n" + message
        # 使用 markdown 更新 log_area
        log_area.markdown(current_log_content)





if not folder:
    st.stop()

folder = Path(folder)
if not folder.exists():
    st.warning(f'文件夹不存在[{folder}]')
    st.stop()
else:
    # Your code here to handle the case when the folder exists
    pass

# 调用xmind执行目录转换
# 创建线程时，不再传递 streamlit_log_callback
if st.button('执行目录转换xmind'):
    should_stop = False
    threading.Thread(target=modified_pdf_batch_processing, args=(folder,)).start()

if st.button('停止执行'):
    should_stop = True



file_infos = pd.DataFrame([{
    '文件名': [p.name],
    '文件大小': [f"{round(p.stat().st_size / (1024 * 1024), 2)} MB"],  # Convert to MB and round to 2 decimal places
    '修改时间': [time.strftime('%Y-%m-%d', time.localtime(p.stat().st_mtime))],  # Convert to YYYY-MM-DD format
    '选择': True
    } for p in Path(folder).glob('*.pdf')
])
editor_infos = st.data_editor(file_infos)

if editor_infos['选择'].sum()<=0:
    st.warning('请选择至少一个文件')
    st.stop()

if st.button('开始合并'):
    st.write('开始合并')
    files = list(editor_infos.query('选择')['文件名'])
    files = [folder/f for f in files]
    pg = st.progress(0,'合并进度')
    st.stop()

# Streamlit 应用的主循环
# 在 Streamlit 主循环中更新日志区域
while True:
    update_log_area()
    time.sleep(1)


