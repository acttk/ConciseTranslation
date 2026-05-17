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

    regionWindow.loadFile(path.join(__dirname, '..', 'renderer', 'region-select', 'index.html'));

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
