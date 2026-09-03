import os
import sys
import time
import asyncio
import pygame
from windows_toasts import Toast, WindowsToaster
from config_manager import muat_config

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    pygame.mixer.init()
except Exception as e:
    print(f"[!] Gagal inisialisasi mixer audio: {e}")

_audio_lock = asyncio.Lock()

def kirim_toast(judul: str, pesan: str):
    """Kirim Windows Toast tanpa suara bawaan OS agar OGG terdengar jernih."""
    try:
        toaster = WindowsToaster("Great Sage System")
        new_toast = Toast()
        new_toast.text_fields = [judul, pesan]
        new_toast.silent = True
        toaster.show_toast(new_toast)
    except Exception:
        try:
            toaster = WindowsToaster("Great Sage System")
            new_toast = Toast([judul, pesan])
            new_toast.silent = True
            toaster.show_toast(new_toast)
        except Exception as e:
            print(f"[!] Gagal kirim toast: {e}")

async def play_voice_async(filename: str):
    """Memutar audio asinkron dengan antrean dan jeda 0.5 detik (anti-tabrakan)."""
    cfg = muat_config()
    if not cfg.get("suara_aktif", True):
        return

    vol = min(max(cfg.get("volume", 80) / 100.0, 0.0), 1.0)
    path = os.path.join(BASE_DIR, "assets", "voice", os.path.basename(filename))
    if not os.path.exists(path):
        return

    async with _audio_lock:
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(vol)
            durasi = sound.get_length()
            sound.play()
            await asyncio.sleep(durasi + 0.5)
        except Exception as e:
            print(f"[!] Audio Async Error ({filename}): {e}")

def play_voice_sync(filename: str):
    """Khusus startup, shutdown, dan exception handler."""
    path = os.path.join(BASE_DIR, "assets", "voice", os.path.basename(filename))
    if os.path.exists(path):
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.8)
            durasi = sound.get_length()
            sound.play()
            time.sleep(durasi + 0.5)
        except Exception:
            pass