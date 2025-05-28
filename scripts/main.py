import os
import time
import doctor
import cooking
import crime
import song

menu = '''
Cai-Yan 工具合计，目前已有：
1. AI 医生助手（需要大模型 API）
2. AI 厨师助手（需要大模型 API）
3. AI 猜罪助手（需要大模型 API）
4. 暴力枚举猜歌助手（速度较慢，不建议使用）
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
        if id == '2':
            time.sleep(0.5)
            os.system('cls' if os.environ.get('OS') == 'Windows_NT' else 'clear')
            cooking.main()
        if id == '3':
            time.sleep(0.5)
            os.system('cls' if os.environ.get('OS') == 'Windows_NT' else 'clear')
            crime.main()
        if id == '4':
            time.sleep(0.5)
            os.system('cls' if os.environ.get('OS') == 'Windows_NT' else 'clear')
            song.main()
