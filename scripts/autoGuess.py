import json
import time
import keyboard
import pyperclip

INPUT_DELAY = 0.1


def loadSettings():
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
    chars = loadChars('./charset/chinese-6750.txt')
    time.sleep(2)
    for current in chars:
        pyperclip.copy(current)
        keyboard.send('ctrl+a')
        keyboard.send('delete')
        keyboard.send('ctrl+v')
        keyboard.send('enter')
        time.sleep(INPUT_DELAY)


if __name__ == '__main__':
    main()
