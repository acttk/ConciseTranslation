async function translateDeepL(text, apiKey) {
  const url = 'https://api-free.deepl.com/v2/translate';
  const params = new URLSearchParams({
    text: text,
    target_lang: 'ZH',
    auth_key: apiKey
  });

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString()
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || `DeepL API error: ${res.status}`);
  }

  const data = await res.json();
  return data.translations[0].text;
}

async function translateBaidu(text, appId, secretKey) {
  const salt = Date.now().toString();

  const { createHash } = require('crypto');
  const sign = createHash('md5')
    .update(appId + text + salt + secretKey)
    .digest('hex');

  const params = new URLSearchParams({
    q: text,
    from: 'en',
    to: 'zh',
    appid: appId,
    salt: salt,
    sign: sign
  });

  const res = await fetch(
    `https://fanyi-api.baidu.com/api/trans/vip/translate?${params.toString()}`
  );

  if (!res.ok) {
    throw new Error(`Baidu API error: ${res.status}`);
  }

  const result = await res.json();
  if (result.error_code) {
    throw new Error(`Baidu error: ${result.error_msg || result.error_code}`);
  }

  return result.trans_result.map(t => t.dst).join('\n');
}

async function translate(text, config) {
  if (config.service === 'baidu') {
    return translateBaidu(text, config.baiduAppId, config.baiduSecretKey);
  }
  return translateDeepL(text, config.deepLKey);
}

module.exports = { translate, translateDeepL, translateBaidu };
