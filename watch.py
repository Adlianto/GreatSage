import os
import sys
import time
import subprocess

TARGET_SCRIPT = "main.py"

def kirim_notif_sistem(judul: str, pesan: str):
    """Mengirim toast notification resmi sistem Windows."""
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

def ambil_mtime():
    """Mengambil timestamp terakhir file target diubah."""
    try:
        return os.path.getmtime(TARGET_SCRIPT)
    except OSError:
        return 0

def main():
    if not os.path.exists(TARGET_SCRIPT):
        print(f"[WATCHER ERROR] File {TARGET_SCRIPT} tidak ditemukan!")
        return

    print("==================================================")
    print("      GREAT SAGE AUTO-RELOAD SUPERVISOR ACTIVE    ")
    print("==================================================")
    print(f"[*] Mengawasi perubahan file: {TARGET_SCRIPT}")
    print("[*] Simpan file (Ctrl + S) di VS Code untuk auto-restart.")

    last_mtime = ambil_mtime()
    sub_process = subprocess.Popen([sys.executable, TARGET_SCRIPT])
    notified_crash = False

    while True:
        time.sleep(1)
        current_mtime = ambil_mtime()

        if current_mtime != last_mtime:
            print("\n🔄 [HOT-RELOAD] Terdeteksi pembaruan kode! Merestart...")
            
            if sub_process.poll() is None:
                sub_process.terminate()
                try:
                    sub_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    sub_process.kill()
            sub_process = subprocess.Popen([sys.executable, TARGET_SCRIPT])
            last_mtime = current_mtime
            notified_crash = False
            
            kirim_notif_sistem(
                "Great Sage: Sistem Diperbarui"
            )
            continue

        ret = sub_process.poll()
        if ret is not None and ret != 0:
            if not notified_crash:
                print(f"\n⚠️ [SISTEM ERROR] main.py crash (Exit code: {ret})!")
                print("[*] Terminal tetap siaga. Perbaiki kode di main.py lalu tekan Ctrl + S...")
                kirim_notif_sistem(
                    "Great Sage: Sistem Diperbarui",
                    "Kode berhasil dimuat ulang."
                )
                notified_crash = True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[WATCHER] Supervisor dihentikan.")