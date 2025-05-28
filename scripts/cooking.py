import base
import time
import json
import traceback
import webdriver_manager.chrome
from selenium import webdriver
from selenium.webdriver.support import ui as selenium_ui
from selenium.webdriver.support import expected_conditions as selenium_ec
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
            GAME_URL = data['cooking_url']
            MAX_ATTEMPTS = data['max_attempts']
    except Exception as e:
        log.critical(f'配置文件读取错误 {e}')
        exit(0)

    try:
        with open('./prompt/cooking.md', 'r', encoding='utf-8') as f:
            SYSTEM_PROMPT = f.read()
    except Exception as e:
        log.error(f'获取系统提示词失败 {e}')


def getPatientResponses(driver):
    responses = []
    try:
        selenium_ui.WebDriverWait(driver, 5).until(
            selenium_ec.presence_of_element_located(
                (
                    by.By.XPATH,
                    "//div[contains(@class, 'ant-flex-vertical') and contains(@style, 'margin: 10px 0px')]",
                )
            )
        )
        patient_message_elements = driver.find_elements(
            by.By.XPATH,
            "//div[contains(@class, 'ant-flex-vertical') and contains(@style, 'margin: 10px 0px')]"
            "//div[contains(@style, 'align-self: start')]"
            "//div[@class='ant-alert-message']",
        )
        for elem in patient_message_elements:
            responses.append(elem.text.strip())
    except Exception as e:
        log.error(f"提取顾客回复时出错: {e}")
    return responses


def getDoctorInputs(driver):
    inputs = []
    try:
        selenium_ui.WebDriverWait(driver, 5).until(
            selenium_ec.presence_of_element_located(
                (
                    by.By.XPATH,
                    "//div[contains(@class, 'ant-flex-vertical') and contains(@style, 'margin: 10px 0px')]",
                )
            )
        )
        my_input_elements = driver.find_elements(
            by.By.XPATH,
            "//div[contains(@class, 'ant-flex-vertical') and contains(@style, 'margin: 10px 0px')]"
            "//div[contains(@style, 'align-self: end')]"
            "//div[@class='ant-alert-message']",
        )
        for elem in my_input_elements:
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
        input_field = selenium_ui.WebDriverWait(driver, 20).until(
            selenium_ec.presence_of_element_located(
                (by.By.CSS_SELECTOR, "input[placeholder^='请输入你对AI厨师的烹饪指导']")
            )
        )

        conversation_history = []
        attempts = 0

        time.sleep(0.3)
        initial_patient_responses = getPatientResponses(driver)
        if initial_patient_responses:
            last_initial_message = initial_patient_responses[-1]
            log.info(f"初始顾客消息: {last_initial_message}")
            conversation_history.append(
                {"role": "user", "content": last_initial_message}
            )
        else:
            log.error("未能捕获到初始顾客消息。")

        while attempts < MAX_ATTEMPTS:
            attempts += 1
            log.info(f"第 {attempts} 次尝试")

            if not conversation_history and not initial_patient_responses:
                log.warning("对话历史为空，让LLM决定第一个问题。")

            suggestion = base.model.chat(conversation_history, SYSTEM_PROMPT)

            if not suggestion:
                log.critical("LLM 未能提供建议，终止程序。")
                break

            log.info(f"准备输入: '{suggestion}'")
            input_field.clear()
            input_field.send_keys(suggestion)
            time.sleep(0.1)

            send_button = selenium_ui.WebDriverWait(driver, 10).until(
                selenium_ec.element_to_be_clickable(
                    (by.By.XPATH, "//button[.//span[contains(text(),'发 送')]]")
                )
            )
            send_button.click()
            log.info("已发送。等待网站响应 (等待转圈消失)...")

            spinner_xpath = "//div[contains(@class, 'ant-spin') and contains(@class, 'ant-spin-spinning')]"
            try:
                selenium_ui.WebDriverWait(driver, 3).until(
                    selenium_ec.presence_of_element_located(
                        (by.By.XPATH, spinner_xpath)
                    )
                )
                log.debug("检测到转圈动画。")
            except:
                log.warning("未立即检测到转圈动画，可能响应很快或网站结构不同。")

            try:
                selenium_ui.WebDriverWait(driver, 60).until(
                    selenium_ec.invisibility_of_element_located(
                        (by.By.XPATH, spinner_xpath)
                    )
                )
                log.info("网站已响应 (转圈已消失)。")
            except:
                log.error("等待网站响应超时 (转圈未消失)。继续尝试获取回复...")
            all_current_patient_responses = getPatientResponses(driver)
            all_my_current_inputs = getDoctorInputs(driver)
            new_patient_response = ""
            if all_current_patient_responses:
                new_patient_response = all_current_patient_responses[-1]
                log.info(f"顾客回复: {new_patient_response}")
            else:
                log.info("未能获取到新的顾客回复。")
            if all_my_current_inputs:
                my_last_input = all_my_current_inputs[-1]
                if (
                    not conversation_history
                    or conversation_history[-1]["content"] != my_last_input
                    or conversation_history[-1]["role"] != "assistant"
                ):
                    conversation_history.append(
                        {"role": "assistant", "content": my_last_input}
                    )
            else:
                conversation_history.append(
                    {"role": "assistant", "content": suggestion}
                )
            if new_patient_response:
                if (
                    not conversation_history
                    or conversation_history[-1]["content"] != new_patient_response
                    or conversation_history[-1]["role"] != "user"
                ):
                    conversation_history.append(
                        {"role": "user", "content": new_patient_response}
                    )
            else:
                log.warning("顾客没有新的回复，即使等待后也是如此。")
            try:
                score_card_elements = driver.find_elements(
                    by.By.XPATH,
                    "//div[@class='ant-card-head' and .//div[@class='ant-card-head-title' and contains(text(), '烹饪评分')]]",
                )
                if score_card_elements:
                    log.success("上菜完成！烹饪评分已出现。")
                    if (
                        len(conversation_history) >= 2
                        and conversation_history[-2]["role"] == "assistant"
                    ):
                        last_ai_action = conversation_history[-2]['content']
                        log.success(f"AI的最后动作为: {last_ai_action}")
                    elif (
                        conversation_history
                        and conversation_history[-1]["role"] == "assistant"
                    ):
                        last_ai_action = conversation_history[-1]['content']
                        log.success(f"AI的最后动作为: {last_ai_action}")
                    else:
                        log.success("上菜流程完成。")
                    break
            except Exception as e:
                log.debug(f"检查烹饪评分卡时出错 (通常表示未找到): {e}")
                pass
            if attempts >= MAX_ATTEMPTS:
                log.critical(f"达到最大尝试次数 ({MAX_ATTEMPTS})，游戏结束。")
                break

    except Exception as e:
        log.critical(f"发生错误: {e}")

        traceback.print_exc()
    finally:
        if driver:
            input("按任意键关闭浏览器...")
            driver.quit()
        log.info("程序结束。")


if __name__ == "__main__":
    base.model.setup()
    main()
