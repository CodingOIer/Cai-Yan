import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from loguru import logger as log

game_url = ''
char_set = []
guess_delay = 0.02


def loadSettings():
    global game_url, guess_delay
    try:
        with open('settings.json', 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            game_url = cfg.get('song_url', game_url)
            guess_delay = float(cfg.get('song_guess_delay', guess_delay))
            log.info(f"设置已加载，延迟: {guess_delay}s")
    except Exception as e:
        log.warning(f"读取 settings.json 出错，使用默认参数: {e}")


def loadCharset():
    global char_set
    try:
        with open('charset/chinese-6750.txt', encoding='utf-8') as f:
            char_set = [c.strip() for c in f if c.strip()]
        log.info(f"加载字库，共 {len(char_set)} 字")
    except Exception as e:
        log.error(f"加载字库失败: {e}")
        exit(1)


def main():
    loadSettings()
    loadCharset()
    log.success("正在启动浏览器并打开歌曲游戏网站...")
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-logging")
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(0)
    driver.get(game_url)
    log.success(f"网站已打开: {game_url}")
    time.sleep(0.3)
    input_selector = "input[placeholder='只输入一个字']"
    send_button_xpath = "//button[.//span[contains(text(),'猜')]]"
    success_xpath = "//span[contains(@class,'ant-typography-success') and (contains(text(),'恭喜') or contains(text(),'猜对了'))]"
    for idx, ch in enumerate(char_set, start=1):
        try:
            inp = driver.find_element(By.CSS_SELECTOR, input_selector)
            inp.clear()
            inp.send_keys(ch)
            btn = driver.find_element(By.XPATH, send_button_xpath)
            btn.click()
            try:
                driver.find_element(By.XPATH, success_xpath)
                log.success(f"第 {idx} 次尝试，猜中: {ch}")
                break
            except NoSuchElementException:
                pass
            time.sleep(guess_delay)
        except NoSuchElementException:
            log.info("输入框消失，游戏结束")
            break
        except Exception as e:
            log.error(f"第 {idx} 次尝试出错: {e}")
            continue

    log.info("测试完毕，按 Enter 关闭浏览器...")
    input()
    try:
        driver.quit()
    except:
        pass
    log.success("脚本结束")


if __name__ == '__main__':
    main()
