# Screenshot Translator Design Spec

**Date:** 2026-05-10
**Status:** Draft

## Overview

A Windows desktop application that captures a screen region via F1 hotkey, performs OCR on English text, and displays the Chinese translation in a floating window.

## Core Features

1. **Global hotkey screenshot (F1)** — press F1 to enter region selection mode
2. **OCR text recognition** — local Tesseract.js, English model, free
3. **Online translation** — DeepL Free API or Baidu Translate API (user chooses and provides API key)
4. **Floating translation result** — always-on-top window next to screenshot area, showing original text + Chinese translation, with copy and close actions

## Tech Stack

- **Framework:** Electron (plain HTML/CSS/JS, no React)
- **OCR:** tesseract.js (English model, local)
- **Translation APIs:** DeepL Free API (primary), Baidu Translate API (alternative)
- **Config storage:** electron-store (local JSON, API keys encrypted at rest)
- **Packaging:** electron-builder → Windows .exe / portable

## Architecture

```
Electron Main Process
├── Global shortcut (F1) registration
├── Screen capture via desktopCapturer
├── Region selection overlay (transparent mask + selection box)
├── System tray (minimize to tray, right-click menu: settings / quit)
└── IPC: pass captured image to renderer

Electron Renderer Process
├── Main Window: settings UI (API source selection, API key input, test button)
├── Translation Overlay: floating result display
├── OCR Module: tesseract.js worker, English recognition
└── Translation Module: HTTP client for DeepL / Baidu API
```

## User Flow

1. Launch app → main window opens
2. First use: select translation service, enter API key → save
3. Minimize to tray → app listens for F1 in background
4. Press F1 → screen freezes → user drags to select region
5. Release mouse → OCR runs (loading indicator shown)
6. Translation API called
7. Translation floating window appears next to screenshot region
8. User: view, copy translation, or close the floating window

## Main Window Design

- Size: ~380×350, fixed
- Translation service selector: DeepL / Baidu (radio buttons)
- API key input: single field for DeepL; AppID + SecretKey for Baidu (dynamic toggle)
- [Test Connection] button: sends a short text to verify API key
- [Save] button: persists config
- Shortcut hint: "F1 - Region Screenshot"
- Options: auto-start checkbox, minimize-to-tray checkbox
- [Minimize to Tray] button

## Translation Floating Window

- Always-on-top, no title bar, draggable
- Shows for each recognized text block:
  - Original text (small, gray)
  - Translation (large, bold, dark)
  - Separator between blocks
- [Copy] button: copies all translation text to clipboard
- [Close] button: dismisses the window
- Position: appears near the screenshot region

## Out of Scope

- Image editing (crop, rotate, brush, text overlay)
- Pasting/sticking screenshot to desktop
- Offline translation
- Languages other than English → Chinese
- History of previous translations
- Multi-monitor optimization (v1 limitation — primary monitor only)

## Dependencies

- `electron`, `electron-builder`
- `tesseract.js` (with English trained data)
- `electron-store`
- DeepL REST API (`https://api-free.deepl.com/v2/translate`)
- Baidu Translate REST API (`https://fanyi-api.baidu.com/api/trans/vip/translate`)
