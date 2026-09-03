import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "suara_aktif": True,
    "volume": 80,
    "baterai": {
        "colok_cabut": True,
        "persentasi_baterai": 20,
        "ambang_penuh": 90
    },
    "notifikasi": {
        "pantau_chat": True,
        "pantau_telepon": True,
        "cooldown_detik": 4
    },
    "sistem": {
        "run_on_startup": True
    }
}

def muat_config():
    if not os.path.exists(CONFIG_FILE):
        simpan_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Gagal membaca config: {e}")
        return DEFAULT_CONFIG

def simpan_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"[!] Gagal menyimpan config: {e}")
        return False