import json
import requests
from loguru import logger as log

MODEL_API_URL = ''
MODEL_API_KEY = ''
MODEL_API_NAME = ''


def setup():
    global MODEL_API_URL, MODEL_API_KEY, MODEL_API_NAME
    try:
        with open('./model_settings.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            MODEL_API_URL = data['url']
            MODEL_API_KEY = data['key']
            MODEL_API_NAME = data['name']
    except:
        print('未找到 model_settings.json 或格式错误，重新输入大模型 API 地址。')
        MODEL_API_URL = input('大模型 API 地址，不含后缀 > ')
        MODEL_API_KEY = input('大模型 API 密钥 > ')
        MODEL_API_NAME = input('大模型 API 名称 > ')
        write = input('是否保存配置？(y/N) > ').lower()
        if write in ['y', 'yes']:
            with open('./model_settings.json', 'w', encoding='utf-8') as f:
                json.dump(
                    {
                        'url': MODEL_API_URL,
                        'key': MODEL_API_KEY,
                        'name': MODEL_API_NAME,
                    },
                    f,
                )


def chat(recent: list, systemPrompt: str = '', temperature: float = 0.7):
    if not MODEL_API_URL or not MODEL_API_KEY:
        setup()
    try:
        headers = {
            "Authorization": f"Bearer {MODEL_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": (
                recent + [{"content": systemPrompt, "role": "system"}]
                if systemPrompt
                else recent
            ),
            "temperature": temperature,
            'model': MODEL_API_NAME,
        }
        response = requests.post(
            MODEL_API_URL + '/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        log.error(e)
        return "抱歉，服务暂时不可用"
