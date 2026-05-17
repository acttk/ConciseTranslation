const { contextBridge, ipcRenderer } = require('electron');
const { recognizeEnglish } = require('../renderer/modules/ocr');
const { translate } = require('../renderer/modules/translate');

contextBridge.exposeInMainWorld('electronAPI', {
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
