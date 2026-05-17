const canvas = document.getElementById('bg');
const selection = document.getElementById('selection');
const ctx = canvas.getContext('2d');

let startX = 0, startY = 0;
let isDrawing = false;
let dpiScale = 1;
let img = new Image();

window.electronAPI.onScreenshotReady((dataUrl) => {
  img.onload = () => {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    dpiScale = canvas.width / window.innerWidth;
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
    x: Math.round(rect.x * dpiScale),
    y: Math.round(rect.y * dpiScale),
    width: Math.round(rect.width * dpiScale),
    height: Math.round(rect.height * dpiScale)
  });
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    window.electronAPI.cancelSelection();
  }
});
