import asyncio
import subprocess
import time
import psutil
from winsdk.windows.ui.notifications.management import (
    UserNotificationListener,
    UserNotificationListenerAccessStatus
)
from winsdk.windows.ui.notifications import NotificationKinds
from config_manager import muat_config

def kirim_toast(judul: str, pesan: str):
    """Menembakkan toast notification Windows sebagai indikator sementara."""
    cfg = muat_config()
    if not cfg.get("suara_aktif", True):
        return

    pesan_sanitized = pesan.replace('"', '`"').replace("'", "’")
    cmd = (
        'powershell -Command "'
        '[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; '
        '$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); '
        '$textNodes = $template.GetElementsByTagName(\'text\'); '
        f'$textNodes.Item(0).AppendChild($template.CreateTextNode(\'{judul}\')) | Out-Null; '
        f'$textNodes.Item(1).AppendChild($template.CreateTextNode(\'{pesan_sanitized}\')) | Out-Null; '
        '$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier(\'Great Sage System\'); '
        '$notification = [Windows.UI.Notifications.ToastNotification]::new($template); '
        '$notifier.Show($notification);"'
    )
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

async def monitor_battery():
    battery = psutil.sensors_battery()
    if battery is None:
        return

    last_power_plugged = battery.power_plugged
    notified_low = False
    notified_full = False

    while True:
        try:
            cfg = muat_config()
            bat_cfg = cfg.get("baterai", {})
            pantau_daya = bat_cfg.get("colok_cabut", True)
            ambang_kritis = bat_cfg.get("ambang_kritis", 20)
            ambang_penuh = bat_cfg.get("ambang_penuh", 90)

            battery = psutil.sensors_battery()
            if battery:
                current_power = battery.power_plugged
                pct = battery.percent

                if pantau_daya:
                    if current_power and not last_power_plugged:
                        teks = f"Konfirmasi: Pasokan daya terhubung. Kapasitas: {pct}%."
                        print(f"\n[⚡ POWER] {teks}")
                        kirim_toast("Great Sage: Analisis Daya", teks)
                        last_power_plugged = True
                        notified_low = False

                    elif not current_power and last_power_plugged:
                        teks = f"Peringatan: Pasokan daya terputus. Baterai: {pct}%."
                        print(f"\n[🔋 POWER] {teks}")
                        kirim_toast("Great Sage: Analisis Daya", teks)
                        last_power_plugged = False
                        notified_full = False

                if not current_power and pct <= ambang_kritis and not notified_low:
                    teks = f"Peringatan Kritis: Cadangan energi di bawah ambang {ambang_kritis}% (Sisa: {pct}%)."
                    print(f"\n[⚠️ BATTERY CRITICAL] {teks}")
                    kirim_toast("Great Sage: Peringatan Energi Kritis", teks)
                    notified_low = True

                if current_power and pct >= ambang_penuh and not notified_full:
                    teks = f"Informasi: Energi telah mencapai {pct}%. Pengisian optimal terpenuhi."
                    print(f"\n[✅ BATTERY OPTIMAL] {teks}")
                    kirim_toast("Great Sage: Kapasitas Optimal", teks)
                    notified_full = True

        except Exception:
            pass

        await asyncio.sleep(2)

async def monitor_notifications():
    listener = UserNotificationListener.current
    status = await listener.request_access_async()
    
    if status != UserNotificationListenerAccessStatus.ALLOWED:
        return

    seen_ids = set()
    last_chat_time = 0.0

    while True:
        try:
            cfg = muat_config()
            notif_cfg = cfg.get("notifikasi", {})
            pantau_chat = notif_cfg.get("pantau_chat", True)
            pantau_call = notif_cfg.get("pantau_telepon", True)
            cooldown_detik = notif_cfg.get("cooldown_detik", 4)

            notifs = await listener.get_notifications_async(NotificationKinds.TOAST)
            for notif in notifs:
                if notif.id not in seen_ids:
                    seen_ids.add(notif.id)
                    
                    app_name = ""
                    app_id = ""
                    try:
                        app_name = notif.app_info.display_info.display_name
                    except Exception:
                        pass
                    try:
                        app_id = notif.app_info.id
                    except Exception:
                        pass

                    if not app_name and app_id:
                        app_name = app_id.split("!")[-1].split("\\")[-1]
                    elif not app_name:
                        app_name = "Unknown App"

                    elements = []
                    try:
                        binding = notif.notification.visual.get_binding("ToastGeneric")
                        if binding:
                            elements = [el.text for el in binding.get_text_elements() if el.text]
                    except Exception:
                        pass

                    preview_text = " | ".join(elements) if elements else ""
                    validasi = f"{app_name} {app_id} {preview_text}".lower()

                    if any(x in validasi for x in ["great sage", "powershell"]):
                        continue

                    is_browser = any(b in f"{app_name} {app_id}".lower() for b in ["brave", "chrome", "edge"])
                    is_wa = "whatsapp" in validasi
                    is_call = any(k in validasi for k in ["panggilan", "telepon", "incoming call", "voice call"])

                    if (is_browser or is_wa) and is_call:
                        if pantau_call:
                            print(f"\n[🚨 PANGGILAN TERDETEKSI] {preview_text}")
                            kirim_toast("Great Sage: Panggilan Masuk!", f"Transmisi: {preview_text}")
                        continue

                    if (is_browser or is_wa) and pantau_chat:
                        sender = elements[0] if len(elements) > 0 else "Pengirim Tidak Dikenal"
                        message = elements[1] if len(elements) > 1 else preview_text

                        now = time.time()
                        if (now - last_chat_time) >= cooldown_detik:
                            print(f"\n[📩 CHAT MASUK] {sender}: {message}")
                            kirim_toast(f"Great Sage: Pesan ({sender})", message[:40])
                            last_chat_time = now

            if len(seen_ids) > 150:
                seen_ids.clear()

        except Exception:
            pass

        await asyncio.sleep(0.5)

async def main():
    print("==================================================")
    print("       GREAT SAGE ENGINE (CONNECTED TO CONFIG)    ")
    print("==================================================")
    await asyncio.gather(
        monitor_battery(),
        monitor_notifications()
    )

if __name__ == "__main__":
    asyncio.run(main())