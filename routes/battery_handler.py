import asyncio
import psutil
from config_manager import muat_config
from .audio_service import play_voice_async, kirim_toast

async def handle_battery_service():
    init_bat = psutil.sensors_battery()
    last_plugged = init_bat.power_plugged if init_bat else None

    cfg = muat_config()
    ambang_penuh_init = cfg.get("baterai", {}).get("ambang_penuh", 90)
    sudah_notif_penuh_sesi_ini = (init_bat.percent >= ambang_penuh_init) if init_bat else False
    notified_critical = False

    await asyncio.sleep(1)

    while True:
        try:
            cfg = muat_config()
            bat_cfg = cfg.get("baterai", {})
            colok_cabut = bat_cfg.get("colok_cabut", True)
            persen_kritis = bat_cfg.get("persentasi_baterai", 20)
            ambang_penuh = bat_cfg.get("ambang_penuh", 90)

            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                power_plugged = battery.power_plugged

                if last_plugged is not None and power_plugged != last_plugged:
                    last_plugged = power_plugged

                    if colok_cabut:
                        if power_plugged:
                            sudah_notif_penuh_sesi_ini = False

                            print(f"\n[CHARGER DIHUBUNGKAN] Pengisian aktif ({percent}%).")
                            kirim_toast("Great Sage", f"Pengisian daya terhubung ({percent}%).")
                            await play_voice_async("kaiseki_chuudan.ogg")

                            if percent >= ambang_penuh:
                                print(f"\n[BATTERY OPTIMAL] Energi sudah mencapai {percent}%.")
                                kirim_toast("Great Sage: Status Energi", f"Pengisian optimal terpenuhi ({percent}%).")
                                await play_voice_async("taishou_kanryou.ogg")
                                sudah_notif_penuh_sesi_ini = True
                        else:
                            print(f"\n[CHARGER DILEPAS] Menggunakan baterai ({percent}%).")
                            kirim_toast("Great Sage", f"Pengisi daya dilepas ({percent}%).")
                            await play_voice_async("kaiseki_chuu.ogg")
                            sudah_notif_penuh_sesi_ini = False

                    await asyncio.sleep(2)
                    continue

                if power_plugged and percent >= ambang_penuh:
                    if not sudah_notif_penuh_sesi_ini and colok_cabut:
                        print(f"\n[BATTERY OPTIMAL] Energi mencapai {percent}%.")
                        kirim_toast("Great Sage: Status Energi", f"Pengisian optimal terpenuhi ({percent}%).")
                        await play_voice_async("taishou_kanryou.ogg")
                        sudah_notif_penuh_sesi_ini = True

                if not power_plugged and percent <= persen_kritis:
                    if not notified_critical:
                        print(f"\n[BATTERY CRITICAL] Daya baterai tinggal {percent}%.")
                        kirim_toast("Great Sage", f"Daya tersisa {percent}%, hubungkan charger.")
                        await play_voice_async("seimei_teika.ogg")
                        notified_critical = True
                else:
                    if percent > persen_kritis:
                        notified_critical = False

        except Exception as e:
            print(f"[!] Battery Service Error: {e}")

        await asyncio.sleep(3)