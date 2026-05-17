import hashlib
import time
import requests


def translate_deepl(text, api_key):
    url = 'https://api-free.deepl.com/v2/translate'
    resp = requests.post(url, data={
        'text': text,
        'target_lang': 'ZH',
        'auth_key': api_key
    }, timeout=15)
    if resp.status_code != 200:
        err = resp.json() if resp.text else {}
        raise Exception(err.get('message', f'DeepL API error {resp.status_code}'))
    return resp.json()['translations'][0]['text']


def translate_baidu(text, app_id, secret_key):
    salt = str(int(time.time() * 1000))
    # Sign: md5(appid + q + salt + key), q must NOT be URL-encoded
    sign = hashlib.md5((app_id + text + salt + secret_key).encode()).hexdigest()
    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    # Use POST to avoid URL length limits
    resp = requests.post(url, data={
        'q': text, 'from': 'en', 'to': 'zh',
        'appid': app_id, 'salt': salt, 'sign': sign
    }, timeout=15)
    result = resp.json()
    if 'error_code' in result and result['error_code']:
        raise Exception(f"Baidu error: {result.get('error_msg', result['error_code'])}")
    return '\n'.join(t['dst'] for t in result.get('trans_result', []))


def translate(text, config):
    if config.get('service') == 'baidu':
        return translate_baidu(text, config['baiduAppId'], config['baiduSecretKey'])
    return translate_deepl(text, config['deepLKey'])
