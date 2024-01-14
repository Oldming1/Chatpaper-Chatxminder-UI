import os

def change_working_directory(directory):
    current_directory = os.getcwd()
    if directory == "pdfxmind":
        new_directory = os.path.join(current_directory, "pdfxmind")
        os.chdir(new_directory)
        print(f"已切换到目录：{new_directory}")
    elif directory == "ChatPaper":
        new_directory = os.path.join(current_directory, "ChatPaper")
        os.chdir(new_directory)
        print(f"已切换到目录：{new_directory}")
    else:
        print("无法找到目录")

user_input = input("请输入目录名称（pdfxmind 或 ChatPaper）：")
change_working_directory(user_input)
