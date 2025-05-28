import sys, os, builtins

# 切换工作目录到 PyInstaller 的临时目录，确保相对路径正常
if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)

# 避免原脚本里调用 exit() 时出现 NameError
builtins.exit = sys.exit
