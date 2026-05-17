const serviceRadios = document.querySelectorAll('input[name="service"]');
const deepLSection = document.getElementById('deepl-section');
const baiduSection = document.getElementById('baidu-section');
const deepLKeyInput = document.getElementById('deepLKey');
const baiduAppIdInput = document.getElementById('baiduAppId');
const baiduSecretKeyInput = document.getElementById('baiduSecretKey');
const testDeepLBtn = document.getElementById('testDeepL');
const testBaiduBtn = document.getElementById('testBaidu');
const deepLStatus = document.getElementById('deepLStatus');
const baiduStatus = document.getElementById('baiduStatus');
const saveBtn = document.getElementById('saveBtn');
const minimizeBtn = document.getElementById('minimizeBtn');
const toggleDeepLBtn = document.getElementById('toggleDeepL');

// Toggle service sections
serviceRadios.forEach(radio => {
  radio.addEventListener('change', () => {
    if (radio.value === 'deepl') {
      deepLSection.classList.remove('hidden');
      baiduSection.classList.add('hidden');
    } else {
      deepLSection.classList.add('hidden');
      baiduSection.classList.remove('hidden');
    }
  });
});

// Toggle password visibility
toggleDeepLBtn.addEventListener('click', () => {
  deepLKeyInput.type = deepLKeyInput.type === 'password' ? 'text' : 'password';
});

// Test DeepL connection
testDeepLBtn.addEventListener('click', async () => {
  const key = deepLKeyInput.value.trim();
  if (!key) {
    deepLStatus.textContent = 'Please enter an API key';
    deepLStatus.className = 'status error';
    return;
  }
  deepLStatus.textContent = 'Testing...';
  deepLStatus.className = 'status';
  const result = await window.electronAPI.testDeepL(key);
  deepLStatus.textContent = result.success ? 'Connection successful' : result.error;
  deepLStatus.className = result.success ? 'status success' : 'status error';
});

// Test Baidu connection
testBaiduBtn.addEventListener('click', async () => {
  const appId = baiduAppIdInput.value.trim();
  const secretKey = baiduSecretKeyInput.value.trim();
  if (!appId || !secretKey) {
    baiduStatus.textContent = 'Please enter App ID and Secret Key';
    baiduStatus.className = 'status error';
    return;
  }
  baiduStatus.textContent = 'Testing...';
  baiduStatus.className = 'status';
  const result = await window.electronAPI.testBaidu(appId, secretKey);
  baiduStatus.textContent = result.success ? 'Connection successful' : result.error;
  baiduStatus.className = result.success ? 'status success' : 'status error';
});

// Save config
saveBtn.addEventListener('click', async () => {
  const config = {
    service: document.querySelector('input[name="service"]:checked').value,
    deepLKey: deepLKeyInput.value,
    baiduAppId: baiduAppIdInput.value,
    baiduSecretKey: baiduSecretKeyInput.value
  };
  await window.electronAPI.saveConfig(config);
  saveBtn.textContent = 'Saved!';
  setTimeout(() => { saveBtn.textContent = 'Save Settings'; }, 1500);
});

// Minimize to tray
minimizeBtn.addEventListener('click', () => {
  window.electronAPI.minimizeToTray();
});

// Load saved config on startup
async function loadConfig() {
  const config = await window.electronAPI.getConfig();
  if (config.service === 'baidu') {
    document.querySelector('input[value="baidu"]').checked = true;
    deepLSection.classList.add('hidden');
    baiduSection.classList.remove('hidden');
  }
  if (config.deepLKey) deepLKeyInput.value = config.deepLKey;
  if (config.baiduAppId) baiduAppIdInput.value = config.baiduAppId;
  if (config.baiduSecretKey) baiduSecretKeyInput.value = config.baiduSecretKey;
}

loadConfig();
