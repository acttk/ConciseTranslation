const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config) => ipcRenderer.invoke('save-config', config),
  testDeepL: (apiKey) => ipcRenderer.invoke('test-deepl', apiKey),
  testBaidu: (appId, secretKey) => ipcRenderer.invoke('test-baidu', appId, secretKey),
  minimizeToTray: () => ipcRenderer.send('minimize-to-tray')
});
