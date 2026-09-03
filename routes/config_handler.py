import os
import asyncio
from config_manager import CONFIG_FILE
from .audio_service import play_voice_async, kirim_toast

async def handle_config_service():
    last_mtime = os.path.getmtime(CONFIG_FILE) if os.path.exists(CONFIG_FILE) else None

    while True:
        try:
            if os.path.exists(CONFIG_FILE):
                current_mtime = os.path.getmtime(CONFIG_FILE)
                if last_mtime is not None and current_mtime != last_mtime:
                    last_mtime = current_mtime
                    print("\n[CONFIG UPDATED] Pengaturan berhasil diterapkan.")
                    kirim_toast("Great Sage", "Pembaruan pengaturan berhasil diterapkan.")
                    await play_voice_async("seiko_shimashita.ogg")
                else:
                    last_mtime = current_mtime
        except Exception:
            pass

        await asyncio.sleep(2)