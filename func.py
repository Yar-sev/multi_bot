import requests
from config import *
import math
from database_func import *
from creds import get_creds

IAM_TOKEN, FOLDER_ID = get_creds()
def count_tokens(text: str) -> int:
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json={"modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest", "text": text},
            headers=headers
        ).json()['tokens']
    )
def is_stt_block_limit(user_id, duration):
    stt_blocks_num = math.ceil(duration / 15)
    num = select_data(user_id)[0][3]
    all_blocks = num + stt_blocks_num

    if duration >= 30:
        return None, 'ошибка: аудио слишком длинное'

    if all_blocks > MAX_USER_STT_BLOCKS:
        return None, 'ошибка: лимит блоков превышен'
    else:
        return stt_blocks_num, 'все ок'
def speech_to_text(data):
    # указываем параметры запроса
    params = "&".join([
        "topic=general",
        f"folderId={FOLDER_ID}",
        "lang=ru-RU"
    ])
    url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }
    response = requests.post(url=url, headers=headers, data=data)
    decoded_data = response.json()
    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result")
    else:
        return False, "При запросе в SpeechKit возникла ошибка"
def text_to_speech(text: str):
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }
    data = {
        'text': text,  #
        'lang': 'ru-RU',
        'voice': 'filipp',
        'folderId': FOLDER_ID,
    }
    response = requests.post('https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize', headers=headers, data=data)

    if response.status_code == 200:
        return True, response.content
    else:
        return False, "При запросе в SpeechKit возникла ошибка"

