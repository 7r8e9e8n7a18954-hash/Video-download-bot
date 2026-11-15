# Telegram Video Downloader Bot

Telegram bot for downloading eligible, public, non-DRM Instagram/Facebook videos when you own the content or have permission to download it.

## Features
- Accepts Instagram and Facebook HTTPS links
- Sends downloaded MP4/video back to Telegram
- No login cookies, account credentials, DRM circumvention, or access-control bypass
- Rejects unsupported domains and files over 49 MB

## 1. Create a Telegram bot
Use **@BotFather** in Telegram, create a bot with `/newbot`, and copy its token.

## 2. Add it to Render
1. Upload this project to a GitHub repository.
2. In Render, create a **New > Blueprint** and connect the repository.
3. In the service environment settings, add `BOT_TOKEN` with your BotFather token.
4. Deploy. The worker runs while the hosting service is active; free-tier availability, sleep, and usage limits can change.

GitHub Actions in this repository only performs a syntax check. GitHub itself does not keep a polling bot online 24/7.

## Run locally
```bash
pip install -r requirements.txt
# Linux/macOS:
export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
python bot.py
```

## Notes
- Download only content you created or are authorized to save, and follow the platform's terms and applicable law.
- Private links, login-required content, DRM-protected media, and restricted streams are not supported.
- Telegram upload limits may vary by Bot API/hosting setup; this version caps files at 49 MB.
