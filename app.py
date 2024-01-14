import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
from pathlib import Path
import time
import subprocess
import threading

# 创建 Dash 应用
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Input(id='folder-path', placeholder='Enter the folder path', type='text'),
    dbc.Button('检查文件夹', id='check-folder-button', color="primary", className="mr-1"),
    dbc.Button('执行目录转换xmind', id='execute-button', color="secondary", className="mr-1"),
    dbc.Button('开始合并', id='merge-button', color="success", className="mr-1"),
    html.Div(id='folder-check-result'),
    dcc.Loading(dcc.Textarea(id='log-output', style={'width': '100%', 'height': 300})),
    dcc.Interval(id='log-interval', interval=1000, n_intervals=0),  # 每秒更新日志
    dcc.Store(id='folder-path-store')  # 存储文件夹路径
], fluid=True)

# 定义检查文件夹的回调
@app.callback(
    Output('folder-check-result', 'children'),
    Output('folder-path-store', 'data'),
    Input('check-folder-button', 'n_clicks'),
    State('folder-path', 'value')
)
def check_folder(n_clicks, folder_path):
    if n_clicks:
        folder = Path(folder_path)
        if not folder.exists():
            return f'文件夹不存在: {folder}', None
        else:
            # 创建文件信息 DataFrame
            file_infos = pd.DataFrame([{
                '文件名': p.name,
                '文件大小': f"{round(p.stat().st_size / (1024 * 1024), 2)} MB",
                '修改时间': time.strftime('%Y-%m-%d', time.localtime(p.stat().st_mtime))
                } for p in folder.glob('*.pdf')])
            return dbc.Table.from_dataframe(file_infos, striped=True, bordered=True, hover=True), folder_path
    return app.no_update, app.no_update

# 定义执行脚本的回调
@app.callback(
    Output('log-output', 'value'),
    Input('execute-button', 'n_clicks'),
    State('folder-path-store', 'data')
)
def run_pdf_batch_processing(n_clicks, folder_path):
    if n_clicks and folder_path:
        # 调用您的 pdf_batch_processing 函数
        # 注意：在 Dash 中实时更新日志的逻辑可能需要另外实现
        return f"在 {folder_path} 上执行 pdf_batch_processing"
    return ""

# 定义更新日志的回调
@app.callback(
    Output('log-output', 'value'),
    Input('log-interval', 'n_intervals')
)
def update_log(n_intervals):
    # 这里是函数体，确保这部分代码有正确的缩进
    return "日志信息（更新中...）"



# 这里应实现从日志文件或其他源读取日志的逻辑
# 目前仅返回一个示例文本
# 定义更新日志的回调
@app.callback(
    Output('log-output', 'value'),
    Input('log-interval', 'n_intervals')
)
def update_log(n_intervals):
    # 这里是函数体，确保这部分代码有正确的缩进
    return "日志信息（更新中...）"

# 定义合并 PDF 的回调
@app.callback(
    Output('merge-result', 'children'),
    Input('merge-button', 'n_clicks'),
    State('folder-path-store', 'data')
)
def merge_pdfs(n_clicks, folder_path):
    if n_clicks and folder_path:
        # 在这里实现您的 PDF 合并逻辑
        return "PDF 合并已完成。"

if __name__ == '__main__':
    app.run_server(debug=True)
