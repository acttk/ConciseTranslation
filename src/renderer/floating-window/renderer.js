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
