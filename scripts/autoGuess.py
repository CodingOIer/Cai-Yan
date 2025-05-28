import json
import time
import keyboard
import pyperclip

INPUT_DELAY = 0.1


def loadSettings():
    global INPUT_DELAY
    try:
        with open('./settings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            INPUT_DELAY = data['auto_guess_delay']
    except:
        print("未找到 settings.json 文件，使用默认参数")


def loadChars(filepath):
    with open(filepath, encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def main():
    loadSettings()
    chars = loadChars('./charset/chinese-6750.txt')
    print(f'已加载 {len(chars)} 个字符')
    print('请注意，如果需要停止代码，请按住 Esc 键')
    input(
        '按下回车后 2s 将开始输入字符，请在此期间将点击输入框，不要做其他操作，等待程序填写'
    )
    time.sleep(2)
    for current in chars:
        if keyboard.is_pressed('esc'):
            print("检测到 Esc，退出程序")
            break
        pyperclip.copy(current)
        keyboard.send('ctrl+a')
        keyboard.send('delete')
        keyboard.send('ctrl+v')
        keyboard.send('enter')
        time.sleep(INPUT_DELAY)


if __name__ == '__main__':
    main()
