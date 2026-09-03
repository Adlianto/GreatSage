import sys
import signal
import atexit
import asyncio

from routes.audio_service import play_voice_sync
from routes.battery_handler import handle_battery_service
from routes.notif_handler import handle_notification_service
from routes.config_handler import handle_config_service

def custom_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print(f"\n[CRASH] Terjadi kegagalan sistem fatal: {exc_value}")
    play_voice_sync("shippai_shimashita.ogg")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = custom_exception_handler

def shutdown_sequence():
    print("\n[SHUTDOWN] Great Sage menonaktifkan sistem...")
    play_voice_sync("katsudou_teishi.ogg")

atexit.register(shutdown_sequence)

def handle_exit_signal(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

async def router_kernel():

    await asyncio.gather(
        handle_battery_service(),
        handle_notification_service(),
        handle_config_service()
    )

if __name__ == "__main__":
    # Booting Awal (kidou.ogg)
    play_voice_sync("kidou.ogg")

    try:
        asyncio.run(router_kernel())
    except (KeyboardInterrupt, SystemExit):
        pass