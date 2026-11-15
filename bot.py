import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
MAX_BYTES = 49 * 1024 * 1024  # Keep below Telegram Bot API upload limit.
ALLOWED_HOSTS = {
    "instagram.com", "www.instagram.com",
    "facebook.com", "www.facebook.com",
    "m.facebook.com", "fb.watch",
}

def valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
        host = (parsed.hostname or "").lower()
        return parsed.scheme == "https" and host in ALLOWED_HOSTS
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Video Downloader Bot में आपका स्वागत है!\n\n"
        "Instagram या Facebook का public video link भेजें।\n"
        "केवल वही वीडियो डाउनलोड करें जिनके लिए आपके पास अनुमति/अधिकार हैं। "
        "यह बॉट DRM या login/access restrictions को bypass नहीं करता।"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = (update.message.text or "").strip()
    if not valid_url(url):
        await update.message.reply_text(
            "कृपया Instagram या Facebook का वैध HTTPS वीडियो लिंक भेजें।"
        )
        return

    status = await update.message.reply_text("⏳ वीडियो उपलब्धता जाँच रहा हूँ…")
    try:
        with tempfile.TemporaryDirectory() as tmp:
            output = str(Path(tmp) / "video.%(ext)s")
            opts = {
                "outtmpl": output,
                "format": "best[ext=mp4][filesize<49M]/best[filesize<49M]",
                "max_filesize": MAX_BYTES,
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "retries": 2,
                "socket_timeout": 20,
                "restrictfilenames": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Downloaded video")
                requested = info.get("requested_downloads") or []
                filepath = requested[0].get("filepath") if requested else None
                if not filepath:
                    filepath = ydl.prepare_filename(info)

            path = Path(filepath)
            if not path.exists():
                candidates = list(Path(tmp).glob("video.*"))
                if not candidates:
                    raise RuntimeError("Downloaded file was not found.")
                path = candidates[0]

            if path.stat().st_size > MAX_BYTES:
                raise RuntimeError("वीडियो Telegram upload limit से बड़ा है।")

            await status.edit_text("📤 वीडियो Telegram पर भेज रहा हूँ…")
            with path.open("rb") as video:
                await update.message.reply_video(
                    video=video,
                    caption=f"✅ {title[:700]}",
                    supports_streaming=True,
                    read_timeout=120,
                    write_timeout=120,
                    connect_timeout=30,
                )
            await status.delete()

    except Exception as exc:
        message = str(exc)
        if "max-filesize" in message.lower() or "larger than" in message.lower():
            reply = "❌ वीडियो 49 MB से बड़ा है।"
        else:
            reply = (
                "❌ वीडियो डाउनलोड नहीं हो पाया। हो सकता है लिंक private हो, "
                "platform ने access रोका हो, या वीडियो उपलब्ध न हो। "
                "Login, cookies या DRM restrictions को bypass नहीं किया जाएगा।"
            )
        await status.edit_text(reply)

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
