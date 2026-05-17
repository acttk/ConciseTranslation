const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  onScreenshotReady: (callback) => {
    ipcRenderer.on('screenshot-ready', (_event, dataUrl) => callback(dataUrl));
  },
  submitSelection: (bounds) => ipcRenderer.send('selection-submitted', bounds),
  cancelSelection: () => ipcRenderer.send('selection-cancelled')
});
