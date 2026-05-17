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
