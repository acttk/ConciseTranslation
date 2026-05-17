# Screenshot Translator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows Electron desktop app that captures screen regions via F1, OCRs English text with Tesseract.js, and displays Chinese translation in a floating window using DeepL/Baidu API.

**Architecture:** Electron main process manages global hotkey, screen capture, region selection overlay, system tray, and IPC. Renderer process has two windows: main settings window and floating translation result window. OCR runs locally via tesseract.js web worker. Translation calls external REST APIs.

**Tech Stack:** Electron (plain HTML/CSS/JS), tesseract.js, electron-store, electron-builder

---

### Task 1: Project scaffolding

**Files:**
- Create: `package.json`
- Create: `.gitignore`
- Create: `src/main/main.js`
- Create: `src/main/screenshot.js`
- Create: `src/main/hotkey.js`
- Create: `src/main/tray.js`
- Create: `src/renderer/main-window/index.html`
- Create: `src/renderer/main-window/style.css`
- Create: `src/renderer/main-window/renderer.js`
- Create: `src/renderer/region-select/index.html`
- Create: `src/renderer/region-select/style.css`
- Create: `src/renderer/region-select/renderer.js`
- Create: `src/renderer/floating-window/index.html`
- Create: `src/renderer/floating-window/style.css`
- Create: `src/renderer/floating-window/renderer.js`
- Create: `src/renderer/modules/ocr.js`
- Create: `src/renderer/modules/translate.js`
- Create: `src/preload.js`
- Create: `src/preload-region.js`
- Create: `src/preload-floating.js`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "screenshot-translator",
  "version": "1.0.0",
  "description": "Screenshot English-to-Chinese translator",
  "main": "src/main/main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder"
  },
  "author": "",
  "license": "MIT",
  "devDependencies": {
    "electron": "^33.0.0",
    "electron-builder": "^25.0.0"
  },
  "dependencies": {
    "electron-store": "^10.0.0",
    "tesseract.js": "^5.0.0"
  }
}
```

- [ ] **Step 2: Install dependencies**

```bash
cd /c/Users/Administrator/Desktop/AiBuilder && npm install
```

Expected: npm installs electron, electron-builder, electron-store, tesseract.js with no errors.

- [ ] **Step 3: Create .gitignore**

```
node_modules/
dist/
.env
*.log
```

- [ ] **Step 4: Create all empty placeholder files**

```bash
mkdir -p src/main && mkdir -p src/renderer/main-window && mkdir -p src/renderer/region-select && mkdir -p src/renderer/floating-window && mkdir -p src/renderer/modules
touch src/main/main.js src/main/screenshot.js src/main/hotkey.js src/main/tray.js
touch src/renderer/main-window/index.html src/renderer/main-window/style.css src/renderer/main-window/renderer.js
touch src/renderer/region-select/index.html src/renderer/region-select/style.css src/renderer/region-select/renderer.js
touch src/renderer/floating-window/index.html src/renderer/floating-window/style.css src/renderer/floating-window/renderer.js
touch src/renderer/modules/ocr.js src/renderer/modules/translate.js
touch src/preload.js src/preload-region.js src/preload-floating.js
```

- [ ] **Step 5: Verify app starts (empty window)**

```bash
cd /c/Users/Administrator/Desktop/AiBuilder && npx electron . 2>&1 &
```

Write a minimal `src/main/main.js` first:
```js
const { app, BrowserWindow } = require('electron');

app.whenReady().then(() => {
  const win = new BrowserWindow({ width: 380, height: 350 });
  win.loadFile('src/renderer/main-window/index.html');
});

app.on('window-all-closed', () => app.quit());
```

Write a minimal `src/renderer/main-window/index.html`:
```html
<!DOCTYPE html><html><body><h1>Screenshot Translator</h1></body></html>
```

Expected: Electron window appears showing "Screenshot Translator". Close window → app quits.

---

### Task 2: System tray

**Files:**
- Modify: `src/main/main.js`
- Create: `src/main/tray.js`

- [ ] **Step 1: Create tray.js**

```js
const { Tray, Menu, app } = require('electron');
const path = require('path');

let tray = null;

function createTray(mainWindow) {
  // Use a 16x16 tray icon - we create a simple one via nativeImage
  const { nativeImage } = require('electron');
  const icon = nativeImage.createEmpty();
  tray = new Tray(icon);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Settings',
      click: () => {
        mainWindow.show();
        mainWindow.focus();
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('Screenshot Translator');
  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => {
    mainWindow.show();
    mainWindow.focus();
  });

  return tray;
}

module.exports = { createTray };
```

- [ ] **Step 2: Modify main.js to integrate tray**

Modify `src/main/main.js`:
```js
const { app, BrowserWindow } = require('electron');
const { createTray } = require('./tray');

let mainWindow = null;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 380,
    height: 350,
    resizable: false,
    title: 'Screenshot Translator',
    webPreferences: {
      preload: require('path').join(__dirname, '..', 'preload.js')
    }
  });

  mainWindow.loadFile('src/renderer/main-window/index.html');

  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createMainWindow();
  createTray(mainWindow);
});

app.on('window-all-closed', (event) => {
  // Don't quit - keep running in tray
});

app.on('before-quit', () => {
  app.isQuitting = true;
});
```

- [ ] **Step 3: Test tray behavior**

```bash
cd /c/Users/Administrator/Desktop/AiBuilder && npx electron .
```

Expected: App opens main window. Close window → hides to tray (check taskbar notification area). Double-click tray icon → window shows again. Right-click tray → "Settings" and "Quit" options.

---

### Task 3: Global hotkey (F1)

**Files:**
- Create: `src/main/hotkey.js`
- Modify: `src/main/main.js`

- [ ] **Step 1: Create hotkey.js**

```js
const { globalShortcut } = require('electron');

function registerHotkey(callback) {
  const registered = globalShortcut.register('F1', () => {
    callback();
  });

  if (!registered) {
    console.error('Failed to register F1 hotkey (may be in use by another app)');
  }

  return registered;
}

function unregisterHotkeys() {
  globalShortcut.unregisterAll();
}

module.exports = { registerHotkey, unregisterHotkeys };
```

- [ ] **Step 2: Wire hotkey into main.js**

Add to `app.whenReady()` in `src/main/main.js`:
```js
const { registerHotkey, unregisterHotkeys } = require('./hotkey');
const { startScreenshot } = require('./screenshot');
// ...
app.whenReady().then(() => {
  createMainWindow();
  createTray(mainWindow);
  registerHotkey(() => {
    startScreenshot();
  });
});

app.on('will-quit', () => {
  unregisterHotkeys();
});
```

- [ ] **Step 3: Verify hotkey registration**

```bash
cd /c/Users/Administrator/Desktop/AiBuilder && npx electron .
```

Expected: App starts without error. F1 key no longer does its default Windows behavior (if any). Console should show no error about F1 registration.

---

### Task 4: Screenshot capture + region selection

**Files:**
- Create: `src/main/screenshot.js`
- Create: `src/renderer/region-select/index.html`
- Create: `src/renderer/region-select/style.css`
- Create: `src/renderer/region-select/renderer.js`
- Create: `src/preload-region.js`

- [ ] **Step 1: Create preload-region.js**

```js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  onScreenshotReady: (callback) => {
    ipcRenderer.on('screenshot-ready', (_event, dataUrl) => callback(dataUrl));
  },
  submitSelection: (bounds) => ipcRenderer.send('selection-submitted', bounds),
  cancelSelection: () => ipcRenderer.send('selection-cancelled')
});
```

- [ ] **Step 2: Create screenshot.js with capture + region overlay**

```js
const { BrowserWindow, screen, desktopCapturer } = require('electron');
const path = require('path');

let regionWindow = null;

async function captureScreen() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.size;

  const sources = await desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: { width, height }
  });

  return sources[0].thumbnail.toDataURL();
}

async function startScreenshot() {
  try {
    const screenshotDataUrl = await captureScreen();

    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.bounds;

    regionWindow = new BrowserWindow({
      x: 0,
      y: 0,
      width,
      height,
      fullscreen: true,
      frame: false,
      transparent: true,
      alwaysOnTop: true,
      skipTaskbar: true,
      resizable: false,
      webPreferences: {
        preload: path.join(__dirname, '..', 'preload-region.js'),
        nodeIntegration: false,
        contextIsolation: true
      }
    });

    regionWindow.loadFile('src/renderer/region-select/index.html');

    regionWindow.webContents.once('did-finish-load', () => {
      regionWindow.webContents.send('screenshot-ready', screenshotDataUrl);
    });

    regionWindow.on('closed', () => {
      regionWindow = null;
    });

  } catch (err) {
    console.error('Screenshot failed:', err);
  }
}

function closeRegionWindow() {
  if (regionWindow) {
    regionWindow.close();
    regionWindow = null;
  }
}

module.exports = { startScreenshot, closeRegionWindow };
```

- [ ] **Step 3: Create region-select index.html**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <canvas id="bg"></canvas>
  <div id="mask"></div>
  <div id="selection"></div>
  <script src="renderer.js"></script>
</body>
</html>
```

- [ ] **Step 4: Create region-select style.css**

```css
* { margin: 0; padding: 0; cursor: crosshair; }
body { width: 100vw; height: 100vh; overflow: hidden; position: relative; }
#bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; }
#mask {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.4); z-index: 1;
}
#selection {
  position: absolute;
  border: 2px dashed #fff;
  background: transparent;
  z-index: 2;
  display: none;
  box-shadow: 0 0 0 9999px rgba(0,0,0,0.4);
}
```

- [ ] **Step 5: Create region-select renderer.js**

```js
const canvas = document.getElementById('bg');
const selection = document.getElementById('selection');
const mask = document.getElementById('mask');
const ctx = canvas.getContext('2d');

let startX = 0, startY = 0;
let isDrawing = false;
let img = new Image();

// Listen for screenshot data from main process
window.electronAPI.onScreenshotReady((dataUrl) => {
  img.onload = () => {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    mask.style.display = 'block';
  };
  img.src = dataUrl;
});

document.addEventListener('mousedown', (e) => {
  isDrawing = true;
  startX = e.clientX;
  startY = e.clientY;
  selection.style.display = 'block';
  selection.style.left = startX + 'px';
  selection.style.top = startY + 'px';
  selection.style.width = '0px';
  selection.style.height = '0px';
});

document.addEventListener('mousemove', (e) => {
  if (!isDrawing) return;
  const x = Math.min(startX, e.clientX);
  const y = Math.min(startY, e.clientY);
  const w = Math.abs(e.clientX - startX);
  const h = Math.abs(e.clientY - startY);
  selection.style.left = x + 'px';
  selection.style.top = y + 'px';
  selection.style.width = w + 'px';
  selection.style.height = h + 'px';
});

document.addEventListener('mouseup', () => {
  if (!isDrawing) return;
  isDrawing = false;

  const rect = selection.getBoundingClientRect();
  if (rect.width < 10 || rect.height < 10) {
    window.electronAPI.cancelSelection();
    return;
  }

  window.electronAPI.submitSelection({
    x: Math.round(rect.x),
    y: Math.round(rect.y),
    width: Math.round(rect.width),
    height: Math.round(rect.height)
  });
});

// ESC to cancel
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    window.electronAPI.cancelSelection();
  }
});
```

- [ ] **Step 6: Register IPC handlers in main.js for selection**

Add to `src/main/main.js`:
```js
const { ipcMain } = require('electron');
const { startScreenshot, closeRegionWindow } = require('./screenshot');
const path = require('path');

// ... existing code ...

ipcMain.handle('get-screenshot', async () => {
  const { captureScreen } = require('./screenshot');
  return await captureScreen();
});

ipcMain.on('selection-submitted', (event, bounds) => {
  closeRegionWindow();
  // Will pass bounds to translation flow in Task 13
  handleNewScreenshot(bounds);
});

ipcMain.on('selection-cancelled', () => {
  closeRegionWindow();
});
```

Note: `handleNewScreenshot` will be defined in Task 13 once the floating window exists.

---

### Task 5: Preload scripts for main and floating windows

**Files:**
- Modify: `src/preload.js`
- Create: `src/preload-floating.js`

- [ ] **Step 1: Write preload.js (main settings window)**

```js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Config operations
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  testDeepL: (apiKey) => ipcRenderer.invoke('test-deepl', apiKey),
  testBaidu: (appId, secretKey) => ipcRenderer.invoke('test-baidu', appId, secretKey),
  minimizeToTray: () => ipcRenderer.send('minimize-to-tray')
});
```

- [ ] **Step 2: Write preload-floating.js (translation result window)**

This preload has `nodeIntegration: false, contextIsolation: true` in the floating window. It loads OCR and translate modules (which need Node.js APIs) via the preload's require access and exposes the processed results to the renderer via contextBridge.

```js
const { contextBridge, ipcRenderer } = require('electron');
const { recognizeEnglish } = require('../renderer/modules/ocr');
const { translate } = require('../renderer/modules/translate');

contextBridge.exposeInMainWorld('electronAPI', {
  // Receive image data from main process and run OCR + translation
  // Returns results via callback so the renderer can display them
  onProcessImage: (callback) => {
    ipcRenderer.on('ocr-image', async (_event, { imageDataUrl, config }) => {
      try {
        const blocks = await recognizeEnglish(imageDataUrl);

        if (blocks.length === 0) {
          callback({ error: 'No English text found in the screenshot.' });
          return;
        }

        const translations = [];
        for (const block of blocks) {
          try {
            const translation = await translate(block.text, config);
            translations.push({ original: block.text, translation });
          } catch {
            translations.push({ original: block.text, translation: '[Translation failed]' });
          }
        }

        callback({ translations });
      } catch (err) {
        callback({ error: err.message });
      }
    });
  },
  copyToClipboard: (text) => ipcRenderer.send('copy-to-clipboard', text),
  closeFloating: () => ipcRenderer.send('close-floating')
});
```

- [ ] **Step 3: Add config IPC handlers to main.js**

Add to `src/main/main.js`:
```js
const Store = require('electron-store');
const store = new Store({
  encryptionKey: 'screenshot-translator-key'
});

ipcMain.handle('get-config', () => {
  return {
    service: store.get('service', 'deepl'),
    deepLKey: store.get('deepLKey', ''),
    baiduAppId: store.get('baiduAppId', ''),
    baiduSecretKey: store.get('baiduSecretKey', '')
  };
});

ipcMain.handle('save-config', (_event, config) => {
  store.set('service', config.service);
  if (config.deepLKey !== undefined) store.set('deepLKey', config.deepLKey);
  if (config.baiduAppId !== undefined) store.set('baiduAppId', config.baiduAppId);
  if (config.baiduSecretKey !== undefined) store.set('baiduSecretKey', config.baiduSecretKey);
  return { success: true };
});

ipcMain.handle('test-deepl', async (_event, apiKey) => {
  try {
    const res = await fetch('https://api-free.deepl.com/v2/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        text: 'Hello',
        target_lang: 'ZH',
        auth_key: apiKey
      }).toString()
    });
    if (res.ok) return { success: true };
    const err = await res.json();
    return { success: false, error: err.message || 'Invalid API key' };
  } catch (e) {
    return { success: false, error: e.message };
  }
});

ipcMain.handle('test-baidu', async (_event, appId, secretKey) => {
  try {
    const salt = Date.now().toString();
    const query = 'Hello';
    const sign = require('crypto')
      .createHash('md5')
      .update(appId + query + salt + secretKey)
      .digest('hex');
    const res = await fetch(
      `https://fanyi-api.baidu.com/api/trans/vip/translate?q=${encodeURIComponent(query)}&from=en&to=zh&appid=${appId}&salt=${salt}&sign=${sign}`
    );
    if (res.ok) return { success: true };
    return { success: false, error: 'Invalid credentials' };
  } catch (e) {
    return { success: false, error: e.message };
  }
});

ipcMain.on('minimize-to-tray', () => {
  mainWindow.hide();
});

ipcMain.on('copy-to-clipboard', (_event, text) => {
  const { clipboard } = require('electron');
  clipboard.writeText(text);
});

ipcMain.on('close-floating', () => {
  if (floatingWindow) {
    floatingWindow.close();
    floatingWindow = null;
  }
});
```

Also add `const Store = require('electron-store');` at the top.

---

### Task 6: Main window UI (HTML + CSS)

**Files:**
- Write: `src/renderer/main-window/index.html`
- Write: `src/renderer/main-window/style.css`

- [ ] **Step 1: Write index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="style.css">
  <title>Screenshot Translator</title>
</head>
<body>
  <div class="container">
    <h1>Screenshot Translator</h1>

    <div class="section">
      <label class="section-title">Translation Service</label>
      <div class="radio-group">
        <label class="radio-label">
          <input type="radio" name="service" value="deepl" checked>
          <span>DeepL (Free API)</span>
        </label>
        <label class="radio-label">
          <input type="radio" name="service" value="baidu">
          <span>Baidu Translate</span>
        </label>
      </div>
    </div>

    <div class="section" id="deepl-section">
      <label for="deepLKey">DeepL API Key</label>
      <div class="input-row">
        <input type="password" id="deepLKey" placeholder="Enter your DeepL API key">
        <button id="toggleDeepL" type="button" class="icon-btn" title="Show/Hide">👁</button>
      </div>
      <button id="testDeepL" class="btn-secondary">Test Connection</button>
      <span id="deepLStatus" class="status"></span>
    </div>

    <div class="section hidden" id="baidu-section">
      <label for="baiduAppId">Baidu App ID</label>
      <input type="text" id="baiduAppId" placeholder="Enter Baidu App ID">
      <label for="baiduSecretKey">Baidu Secret Key</label>
      <input type="password" id="baiduSecretKey" placeholder="Enter Baidu Secret Key">
      <button id="testBaidu" class="btn-secondary">Test Connection</button>
      <span id="baiduStatus" class="status"></span>
    </div>

    <div class="section">
      <label class="shortcut-hint">Press F1 to take a screenshot and translate</label>
    </div>

    <div class="actions">
      <button id="saveBtn" class="btn-primary">Save Settings</button>
      <button id="minimizeBtn" class="btn-secondary">Minimize to Tray</button>
    </div>
  </div>
  <script src="renderer.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write style.css**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 20px;
  user-select: none;
}

.container {
  max-width: 340px;
  margin: 0 auto;
}

h1 {
  font-size: 18px;
  text-align: center;
  margin-bottom: 20px;
  color: #f5c2e7;
}

.section {
  margin-bottom: 16px;
}

.section-title {
  display: block;
  font-size: 13px;
  color: #a6adc8;
  margin-bottom: 6px;
}

label {
  display: block;
  font-size: 12px;
  margin-bottom: 4px;
  color: #bac2de;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #45475a;
  border-radius: 6px;
  background: #313244;
  color: #cdd6f4;
  font-size: 13px;
  outline: none;
}

input:focus {
  border-color: #cba6f7;
}

.radio-group {
  display: flex;
  gap: 16px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 13px;
}

.input-row {
  display: flex;
  gap: 6px;
}

.input-row input {
  flex: 1;
}

.icon-btn {
  padding: 6px 8px;
  background: #313244;
  border: 1px solid #45475a;
  border-radius: 6px;
  cursor: pointer;
  color: #cdd6f4;
}

.btn-primary {
  width: 100%;
  padding: 10px;
  background: #cba6f7;
  color: #1e1e2e;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 8px;
}

.btn-secondary {
  width: 100%;
  padding: 8px;
  background: #45475a;
  color: #cdd6f4;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  margin-top: 4px;
}

.hidden { display: none; }

.status {
  display: block;
  font-size: 12px;
  margin-top: 4px;
}

.status.success { color: #a6e3a1; }
.status.error { color: #f38ba8; }

.shortcut-hint {
  display: block;
  text-align: center;
  font-size: 15px;
  color: #f5c2e7;
  padding: 16px;
  background: #313244;
  border-radius: 8px;
  border: 1px dashed #cba6f7;
}

.actions {
  margin-top: 20px;
}
```

---

### Task 7: Main window renderer logic

**Files:**
- Write: `src/renderer/main-window/renderer.js`

- [ ] **Step 1: Write renderer.js**

```js
const { electronAPI } = window;

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
  const result = await electronAPI.testDeepL(key);
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
  const result = await electronAPI.testBaidu(appId, secretKey);
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
  await electronAPI.saveConfig(config);
  saveBtn.textContent = 'Saved!';
  setTimeout(() => { saveBtn.textContent = 'Save Settings'; }, 1500);
});

// Minimize to tray
minimizeBtn.addEventListener('click', () => {
  electronAPI.minimizeToTray();
});

// Load saved config on startup
async function loadConfig() {
  const config = await electronAPI.getConfig();
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
```

- [ ] **Step 2: Launch app and verify UI renders and responds to interactions**

```bash
cd /c/Users/Administrator/Desktop/AiBuilder && npx electron .
```

Expected: Main window shows with proper styling. Toggling between DeepL/Baidu switches form fields. Show/hide password works. Buttons respond.

---

### Task 8: Translation API module

**Files:**
- Write: `src/renderer/modules/translate.js`

- [ ] **Step 1: Write translate.js**

```js
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

  // Generate MD5 sign as required by Baidu API
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
```

---

### Task 9: OCR module

**Files:**
- Write: `src/renderer/modules/ocr.js`

- [ ] **Step 1: Write ocr.js**

```js
async function recognizeEnglish(imageDataUrl) {
  const Tesseract = require('tesseract.js');

  const worker = await Tesseract.createWorker('eng', 1, {
    logger: (m) => {
      if (m.status === 'recognizing text') {
        // Progress could be emitted here if needed
      }
    }
  });

  try {
    const { data } = await worker.recognize(imageDataUrl);
    await worker.terminate();

    // Extract text blocks with position info
    const blocks = [];
    if (data.blocks) {
      for (const block of data.blocks) {
        for (const paragraph of block.paragraphs) {
          const text = paragraph.text.trim();
          if (text.length > 0) {
            blocks.push({ text });
          }
        }
      }
    }

    // If no blocks found, fall back to full recognized text
    if (blocks.length === 0 && data.text.trim()) {
      blocks.push({ text: data.text.trim() });
    }

    return blocks;
  } catch (err) {
    await worker.terminate();
    throw err;
  }
}

module.exports = { recognizeEnglish };
```

---

### Task 10: Floating window UI

**Files:**
- Write: `src/renderer/floating-window/index.html`
- Write: `src/renderer/floating-window/style.css`

- [ ] **Step 1: Write floating window index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="style.css">
  <title>Translation</title>
</head>
<body>
  <div class="header">
    <span class="title">Translation</span>
    <div class="header-actions">
      <button id="copyBtn" title="Copy translation">📋</button>
      <button id="closeBtn" title="Close">✕</button>
    </div>
  </div>
  <div id="content">
    <div id="loading">Recognizing text...</div>
    <div id="results" class="hidden"></div>
    <div id="error" class="hidden"></div>
  </div>
  <script src="renderer.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write floating window style.css**

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #1e1e2e;
  color: #cdd6f4;
  min-width: 300px;
  max-width: 500px;
  border-radius: 8px;
  overflow: hidden;
  user-select: none;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #313244;
  -webkit-app-region: drag;
  cursor: move;
}

.title {
  font-size: 13px;
  color: #f5c2e7;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 4px;
  -webkit-app-region: no-drag;
}

.header-actions button {
  background: none;
  border: none;
  color: #cdd6f4;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 14px;
  border-radius: 4px;
}

.header-actions button:hover {
  background: #45475a;
}

#content {
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
}

#loading {
  text-align: center;
  padding: 20px;
  color: #a6adc8;
}

.block {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #313244;
}

.block:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.original {
  font-size: 12px;
  color: #6c7086;
  margin-bottom: 4px;
  word-wrap: break-word;
}

.translation {
  font-size: 16px;
  color: #cdd6f4;
  font-weight: 600;
  word-wrap: break-word;
}

#error {
  color: #f38ba8;
  text-align: center;
  padding: 20px;
}

.hidden { display: none; }
```

---

### Task 11: Floating window renderer logic

**Files:**
- Write: `src/renderer/floating-window/renderer.js`

- [ ] **Step 1: Write floating window renderer.js**

```js
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const copyBtn = document.getElementById('copyBtn');
const closeBtn = document.getElementById('closeBtn');

let allTranslations = [];

function displayResults(translations) {
  loadingDiv.classList.add('hidden');

  allTranslations = translations;
  for (const item of translations) {
    const blockDiv = document.createElement('div');
    blockDiv.className = 'block';

    const origDiv = document.createElement('div');
    origDiv.className = 'original';
    origDiv.textContent = item.original;

    const transDiv = document.createElement('div');
    transDiv.className = 'translation';
    transDiv.textContent = item.translation;

    blockDiv.appendChild(origDiv);
    blockDiv.appendChild(transDiv);
    resultsDiv.appendChild(blockDiv);
  }

  resultsDiv.classList.remove('hidden');
}

// Listen for OCR + translation results from preload
window.electronAPI.onProcessImage((result) => {
  if (result.error) {
    loadingDiv.classList.add('hidden');
    errorDiv.textContent = result.error;
    errorDiv.classList.remove('hidden');
    return;
  }
  displayResults(result.translations);
});

// Copy all translations
copyBtn.addEventListener('click', () => {
  const text = allTranslations.map(t => t.translation).join('\n');
  window.electronAPI.copyToClipboard(text);
  copyBtn.textContent = '✓';
  setTimeout(() => { copyBtn.textContent = '📋'; }, 1500);
});

// Close window
closeBtn.addEventListener('click', () => {
  window.electronAPI.closeFloating();
});
```

---

### Task 12: Wire end-to-end flow in main process

**Files:**
- Modify: `src/main/main.js`
- Modify: `src/main/screenshot.js`

- [ ] **Step 1: Add floating window creation to main.js**

Add to `src/main/main.js`:
```js
let floatingWindow = null;

function createFloatingWindow(screenshotDataUrl, cropBounds, config) {
  if (floatingWindow) {
    floatingWindow.close();
  }

  floatingWindow = new BrowserWindow({
    x: cropBounds.x + cropBounds.width + 20,
    y: cropBounds.y,
    width: 400,
    height: 300,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: true,
    transparent: true,
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload-floating.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  floatingWindow.loadFile('src/renderer/floating-window/index.html');

  floatingWindow.webContents.once('did-finish-load', () => {
    floatingWindow.webContents.send('ocr-image', {
      imageDataUrl: screenshotDataUrl,
      config: config
    });
  });

  floatingWindow.on('closed', () => {
    floatingWindow = null;
  });
}
```

- [ ] **Step 2: Add handleNewScreenshot function in main.js**

```js
const { screen } = require('electron');

async function handleNewScreenshot(bounds) {
  // Re-capture screen to get the full image, then crop
  const sources = await desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: screen.getPrimaryDisplay().size
  });

  const fullImage = sources[0].thumbnail;

  // Crop to selection bounds
  const cropped = fullImage.crop(bounds);
  const imageDataUrl = cropped.toDataURL();

  // Get current config
  const config = {
    service: store.get('service', 'deepl'),
    deepLKey: store.get('deepLKey', ''),
    baiduAppId: store.get('baiduAppId', ''),
    baiduSecretKey: store.get('baiduSecretKey', '')
  };

  createFloatingWindow(imageDataUrl, bounds, config);
}
```

- [ ] **Step 3: Add desktopCapturer require at top of main.js**

```js
const { app, BrowserWindow, ipcMain, screen, desktopCapturer } = require('electron');
```

---

### Task 13: Build and package configuration

**Files:**
- Create: `electron-builder.yml`

- [ ] **Step 1: Create electron-builder.yml**

```yaml
appId: com.screenshot-translator
productName: Screenshot Translator
directories:
  output: dist
win:
  target:
    - target: nsis
      arch: [x64]
  icon: null
nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
files:
  - src/**/*
  - node_modules/**/*
  - package.json
extraMetadata:
  main: src/main/main.js
```

- [ ] **Step 2: Build the app**

```bash
cd /c/Users/Administrator/Desktop/AiBuilder && npm run build
```

Expected: `dist/` directory created with Windows installer. Check that `dist/` contains the `.exe` installer.

- [ ] **Step 3: Test the packaged app**

Install the generated `.exe` from `dist/` and verify:
- App installs and launches
- Settings window appears
- F1 triggers screenshot region selection
- Select region → floating translation window appears
- Copy and close buttons work
- Minimize to tray works

---

### Task 14: Polish and edge cases

**Files:**
- Modify: `src/renderer/modules/ocr.js`
- Modify: `src/main/main.js`

- [ ] **Step 1: Add timeout handling for OCR**

In `src/renderer/modules/ocr.js`, modify recognize function to handle worker initialization failure:
```js
async function recognizeEnglish(imageDataUrl) {
  const Tesseract = require('tesseract.js');

  let worker;
  try {
    worker = await Tesseract.createWorker('eng', 1, {
      logger: (m) => {
        // silence logging in production
      }
    });
  } catch (err) {
    throw new Error('Failed to initialize OCR engine. Please check your internet connection for initial model download.');
  }

  try {
    const { data } = await worker.recognize(imageDataUrl);
    await worker.terminate();

    const blocks = [];
    if (data.blocks) {
      for (const block of data.blocks) {
        for (const paragraph of block.paragraphs) {
          const text = paragraph.text.trim();
          if (text.length > 0) {
            blocks.push({ text });
          }
        }
      }
    }

    if (blocks.length === 0 && data.text.trim()) {
      blocks.push({ text: data.text.trim() });
    }

    return blocks;
  } catch (err) {
    await worker.terminate();
    throw err;
  }
}
```

- [ ] **Step 2: Ensure region window closes on app quit**

In `src/main/main.js`, add to `app.on('before-quit')`:
```js
app.on('before-quit', () => {
  app.isQuitting = true;
  const { closeRegionWindow } = require('./screenshot');
  closeRegionWindow();
  unregisterHotkeys();
});
```

- [ ] **Step 3: Final end-to-end test**

```bash
cd /c/Users/Administrator/Desktop/AiBuilder && npx electron .
```

Expected: Full flow works — configure API key → minimize → press F1 → select region → see OCR + translation → copy → close.
