const { Tray, Menu, app, nativeImage } = require('electron');

let tray = null;

function createTray(mainWindow) {
  // 16x16 purple icon as base64 PNG
  const icon = nativeImage.createFromDataURL(
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA' +
    'O0lEQVQ4T2P8z0AeYKS0gUzsAJMLSADGgBQXFBSwMDIybmBgYNgEVMeA5AI4DwDBi0AwOzs7HRER' +
    'EWgAAL3hDqFUluSPAAAAAElFTkSuQmCC'
  );
  tray = new Tray(icon);

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show',
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
