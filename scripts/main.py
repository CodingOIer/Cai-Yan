import doctor
import os
import time

menu = '''
Cai-Yan 工具合计，目前已有：
1. AI 医生助手
对应的 AI 提示词可以在 /sciripts/prompt 中查看与修改，默认为利于游戏胜利的提示词。
部分游戏会唤起 Chrome 浏览器自动操作，请不要在唤起的 Chrome 中操作。
'''

if __name__ == '__main__':
    while True:
        os.system('cls' if os.environ.get('OS') == 'Windows_NT' else 'clear')
        print(menu)
        id = input('请输入编号 > ')
        if id == '1':
            time.sleep(0.5)
            os.system('cls' if os.environ.get('OS') == 'Windows_NT' else 'clear')
            doctor.main()
        else:
            print('请输入正确的编号！')
            input('按回车键继续...')
    pass
