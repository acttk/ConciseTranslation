const path = require('path');
const { app, BrowserWindow, ipcMain, screen, desktopCapturer } = require('electron');
const Store = require('electron-store');
const { createTray } = require('./tray');
const { startScreenshot, closeRegionWindow } = require('./screenshot');
const { registerHotkey, unregisterHotkeys } = require('./hotkey');

let mainWindow = null;
let floatingWindow = null;

const store = new Store({ encryptionKey: 'screenshot-translator-key' });

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 380,
    height: 350,
    resizable: false,
    title: 'Screenshot Translator',
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'main-window', 'index.html'));

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
  registerHotkey(() => {
    startScreenshot();
  });

  ipcMain.on('selection-submitted', async (event, bounds) => {
    closeRegionWindow();
    await handleNewScreenshot(bounds);
  });

  ipcMain.on('selection-cancelled', () => {
    closeRegionWindow();
  });
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

function createFloatingWindow(screenshotDataUrl, cropBounds, config) {
  if (floatingWindow) {
    floatingWindow.close();
  }

  floatingWindow = new BrowserWindow({
    x: Math.min(cropBounds.x + cropBounds.width + 20, screen.getPrimaryDisplay().bounds.width - 420),
    y: cropBounds.y,
    width: 400,
    height: 300,
    frame: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: true,
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload-floating.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  floatingWindow.loadFile(path.join(__dirname, '..', 'renderer', 'floating-window', 'index.html'));

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

async function handleNewScreenshot(bounds) {
  const sources = await desktopCapturer.getSources({
    types: ['screen'],
    thumbnailSize: screen.getPrimaryDisplay().size
  });

  const fullImage = sources[0].thumbnail;
  const cropped = fullImage.crop(bounds);
  const imageDataUrl = cropped.toDataURL();

  const config = {
    service: store.get('service', 'deepl'),
    deepLKey: store.get('deepLKey', ''),
    baiduAppId: store.get('baiduAppId', ''),
    baiduSecretKey: store.get('baiduSecretKey', '')
  };

  createFloatingWindow(imageDataUrl, bounds, config);
}

app.on('window-all-closed', () => {
  // Don't quit - keep running in tray
});

app.on('before-quit', () => {
  app.isQuitting = true;
  closeRegionWindow();
  unregisterHotkeys();
});
