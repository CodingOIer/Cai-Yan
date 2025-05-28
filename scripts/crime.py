import base
import time
import json
import traceback
import webdriver_manager.chrome
from selenium import webdriver
from selenium.webdriver.support import ui as seleniumUi
from selenium.webdriver.support import expected_conditions as seleniumEc
from selenium.webdriver.common import by
from loguru import logger as log

GAME_URL = ''
MAX_ATTEMPTS = 0
SYSTEM_PROMPT = ''


def setup():
    global GAME_URL, MAX_ATTEMPTS, SYSTEM_PROMPT
    try:
        with open('./settings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            GAME_URL = data['crime_url']
            MAX_ATTEMPTS = data['max_attempts']
    except Exception as e:
        log.critical(f'配置文件读取错误 {e}')
        exit(0)

    try:
        with open('./prompt/crime.md', 'r', encoding='utf-8') as f:
            SYSTEM_PROMPT = f.read()
    except Exception as e:
        log.error(f'获取系统提示词失败 {e}')


def getCrimerResponses(driver):
    responses = []
    try:
        seleniumUi.WebDriverWait(driver, 5).until(
            seleniumEc.presence_of_element_located(
                (
                    by.By.XPATH,
                    "//div[contains(@class, 'ant-flex-vertical') and contains(@style, 'margin: 10px 0px')]",
                )
            )
        )
        patientMessageElements = driver.find_elements(
            by.By.XPATH,
            "//div[contains(@class, 'ant-flex-vertical') and contains(@style, 'margin: 10px 0px')]"
            "//div[contains(@style, 'align-self: start')]"
            "//div[@class='ant-alert-message']",
        )
        for elem in patientMessageElements:
            responses.append(elem.text.strip())
    except Exception as e:
        log.error(f"提取罪犯回复时出错: {e}")
    return responses


def getLawerInputs(driver):
    inputs = []
    try:
        seleniumUi.WebDriverWait(driver, 5).until(
            seleniumEc.presence_of_element_located(
                (
                    by.By.XPATH,
                    "//div[contains(@class, 'ant-flex-vertical') and contains(@style, 'margin: 10px 0px')]",
                )
            )
        )
        myInputElements = driver.find_elements(
            by.By.XPATH,
            "//div[contains(@class, 'ant-flex-vertical') and contains(@style, 'margin: 10px 0px')]"
            "//div[contains(@style, 'align-self: end')]"
            "//div[@class='ant-alert-message']",
        )
        for elem in myInputElements:
            inputs.append(elem.text.strip())
    except Exception as e:
        log.error(f"提取我方输入时出错: {e}")
    return inputs


def main():
    setup()
    log.success("正在启动浏览器并打开游戏网站...")
    driver = None
    try:
        service = webdriver.chrome.service.Service(
            webdriver_manager.chrome.ChromeDriverManager().install()
        )
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(GAME_URL)
        log.success("网站已打开。等待页面加载...")
        inputField = seleniumUi.WebDriverWait(driver, 20).until(
            seleniumEc.presence_of_element_located(
                (
                    by.By.CSS_SELECTOR,
                    "input[placeholder^='写下你的问题或猜测']",
                )
            )
        )
        conversationHistory = []
        attempts = 0
        time.sleep(0.3)
        initialCrimerResponses = getCrimerResponses(driver)
        if initialCrimerResponses:
            lastInitialMessage = initialCrimerResponses[-1]
            log.info(f"初始罪犯消息: {lastInitialMessage}")
            conversationHistory.append(
                {"role": "assistant", "content": lastInitialMessage}
            )
        else:
            log.error("未能捕获到初始罪犯消息。")
        while attempts < MAX_ATTEMPTS:
            attempts += 1
            log.info(f"第 {attempts} 次尝试")
            if not conversationHistory and not initialCrimerResponses:
                log.warning("对话历史为空，让LLM决定第一个问题。")
            suggestion = base.model.chat(conversationHistory, SYSTEM_PROMPT)
            if not suggestion:
                log.critical("LLM 未能提供建议，终止程序。")
                break
            log.info(f"准备输入: '{suggestion}'")
            inputField.clear()
            inputField.send_keys(suggestion)
            time.sleep(0.1)
            sendButton = seleniumUi.WebDriverWait(driver, 10).until(
                seleniumEc.element_to_be_clickable(
                    (
                        by.By.XPATH,
                        "//button[.//span[contains(text(),'发 送')]]",
                    )
                )
            )
            sendButton.click()
            log.info("已发送。等待网站响应 (等待转圈消失)...")
            spinnerXpath = "//div[contains(@class, 'ant-spin') and contains(@class, 'ant-spin-spinning')]"
            try:
                seleniumUi.WebDriverWait(driver, 3).until(
                    seleniumEc.presence_of_element_located((by.By.XPATH, spinnerXpath))
                )
            except:
                pass
            try:
                seleniumUi.WebDriverWait(driver, 60).until(
                    seleniumEc.invisibility_of_element_located(
                        (by.By.XPATH, spinnerXpath)
                    )
                )
                log.info("网站已响应 (转圈已消失)。")
            except:
                log.error("等待网站响应超时 (转圈未消失)。继续尝试获取回复...")
            CrimerResponses = getCrimerResponses(driver)
            myInputs = getLawerInputs(driver)
            newCrimerResponse = ""
            if CrimerResponses:
                newCrimerResponse = CrimerResponses[-1]
                log.info(f"罪犯回复: {newCrimerResponse}")
            else:
                log.warning("未能获取到新的罪犯回复。")
            if myInputs:
                myLastInput = myInputs[-1]
                if (
                    not conversationHistory
                    or conversationHistory[-1]["content"] != myLastInput
                    or conversationHistory[-1]["role"] != "user"
                ):
                    conversationHistory.append({"role": "user", "content": myLastInput})
            else:
                conversationHistory.append({"role": "user", "content": suggestion})
            if newCrimerResponse:
                if (
                    not conversationHistory
                    or conversationHistory[-1]["content"] != newCrimerResponse
                    or conversationHistory[-1]["role"] != "assistant"
                ):
                    conversationHistory.append(
                        {"role": "assistant", "content": newCrimerResponse}
                    )
            else:
                log.warning("罪犯没有新的回复，即使等待后也是如此。")
            try:
                successMessageElements = driver.find_elements(
                    by.By.XPATH,
                    "//span[contains(@class, 'ant-typography-success') and contains(text(), '恭喜你，你猜对了！')]",
                )
                if successMessageElements:
                    log.success("恭喜！AI 成功猜对了罪名！")
                    finalGuess = "提取失败"
                    if (
                        len(conversationHistory) >= 2
                        and conversationHistory[-2]["role"] == "user"
                    ):
                        finalGuess = conversationHistory[-2]['content']
                    elif (
                        len(conversationHistory) >= 1
                        and conversationHistory[-1]["role"] == "user"
                        and "恭喜你" in newCrimerResponse
                    ):
                        finalGuess = conversationHistory[-1]['content']
                    log.success(f"最终猜测的罪名是: {finalGuess}")
                    break
            except Exception:
                pass
            if attempts >= MAX_ATTEMPTS:
                log.critical(f"达到最大尝试次数 ({MAX_ATTEMPTS})，游戏结束。")
                break
    except Exception as e:
        log.critical(f"发生错误: {e}")
        traceback.print_exc()
    finally:
        if driver:
            input("按 Enter 关闭浏览器...")
            try:
                driver.quit()
            except:
                pass
        log.info("程序结束。")


if __name__ == "__main__":
    base.model.setup()
    main()
