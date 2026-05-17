async function recognizeEnglish(imageDataUrl) {
  const Tesseract = require('tesseract.js');

  let worker;
  try {
    worker = await Tesseract.createWorker('eng', 1, {
      logger: () => {
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

module.exports = { recognizeEnglish };
