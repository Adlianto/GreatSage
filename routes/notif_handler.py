import time
import asyncio
from winsdk.windows.ui.notifications.management import UserNotificationListener, UserNotificationListenerAccessStatus
from winsdk.windows.ui.notifications import NotificationKinds
from config_manager import muat_config
from .audio_service import play_voice_async, kirim_toast

async def handle_notification_service():
    try:
        listener = UserNotificationListener.current
    except AttributeError:
        listener = UserNotificationListener.get_current()

    status = await listener.request_access_async()
    if status != UserNotificationListenerAccessStatus.ALLOWED:
        return

    seen_ids = set()
    first_run = True
    last_chat_time = 0

    while True:
        try:
            cfg = muat_config()
            notif_cfg = cfg.get("notifikasi", {})
            pantau_chat = notif_cfg.get("pantau_chat", True)
            cooldown = notif_cfg.get("cooldown_detik", 4)

            notifs = await listener.get_notifications_async(NotificationKinds.TOAST)

            if first_run:
                for notif in notifs:
                    seen_ids.add(notif.id)
                first_run = False
                await asyncio.sleep(1)
                continue

            for notif in notifs:
                if notif.id not in seen_ids:
                    seen_ids.add(notif.id)

                    app_name = ""
                    try:
                        app_name = notif.app_info.display_info.display_name.lower()
                    except Exception:
                        pass

                    if "great sage" in app_name:
                        continue

                    is_wa = "whatsapp" in app_name
                    is_browser = any(b in app_name for b in ["brave", "chrome", "edge", "firefox"])

                    elements = []
                    try:
                        binding = notif.notification.visual.get_binding("ToastGeneric")
                        if binding:
                            elements = [el.text for el in binding.get_text_elements()]
                    except Exception:
                        pass

                    preview_text = " ".join(elements) if elements else "Ada notifikasi baru."

                    if any(x in preview_text.lower() for x in ["pengisian daya", "charger", "baterai"]):
                        continue

                    if (is_browser or is_wa) and pantau_chat:
                        sender = elements[0] if len(elements) > 0 else "Pengirim Tidak Dikenal"
                        message = elements[1] if len(elements) > 1 else preview_text

                        now = time.time()
                        if (now - last_chat_time) >= cooldown:
                            print(f"\n[CHAT MASUK] {sender}: {message}")
                            kirim_toast(f"Great Sage({sender})", message[:40])
                            await play_voice_async("koku.ogg")
                            last_chat_time = now

            if len(seen_ids) > 150:
                seen_ids.clear()

        except Exception:
            pass

        await asyncio.sleep(1)