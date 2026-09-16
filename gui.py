import os
import sys
import subprocess
import psutil
import customtkinter as ctk
from PIL import Image
from config_manager import muat_config, simpan_config

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def start_engine_if_not_running():
    engine_name = "GreatSageEngine.exe"
    
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == engine_name.lower():
                return  # Sudah aktif, tidak perlu jalankan dobel
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    engine_path = os.path.join(base_dir, engine_name)
    
    # 3. Jalankan GreatSageEngine di background tanpa memunculkan command prompt hitam
    if os.path.exists(engine_path):
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NO_WINDOW
        subprocess.Popen([engine_path], creationflags=creationflags)

class GreatSageDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Great Sage - Control")
        self.geometry("460x650")
        self.resizable(False, False)

        self.config_data = muat_config()

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(20, 10), padx=25, fill="x")

        img_path = os.path.join(os.path.dirname(__file__), "assets", "img", "slime.jpg")
        if os.path.exists(img_path):
            img_data = Image.open(img_path)
            self.slime_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(50, 50))
            self.avatar_label = ctk.CTkLabel(self.header_frame, text="", image=self.slime_image)
            self.avatar_label.pack(side="left", padx=(0, 15))

        self.text_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.text_container.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(
            self.text_container,
            text="Great Sage",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.text_container,
            text="System Parameters & Notification Settings",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle_label.pack(anchor="w")

        self.audio_frame = ctk.CTkFrame(self)
        self.audio_frame.pack(pady=10, padx=20, fill="x")

        self.audio_title = ctk.CTkLabel(
            self.audio_frame,
            text="AUDIO & FEEDBACK",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.audio_title.pack(anchor="w", padx=15, pady=(10, 5))

        self.switch_voice = ctk.CTkSwitch(
            self.audio_frame,
            text="Aktifkan Respons Suara",
            onvalue=True,
            offvalue=False
        )
        if self.config_data.get("suara_aktif", True):
            self.switch_voice.select()
        else:
            self.switch_voice.deselect()
        self.switch_voice.pack(anchor="w", padx=15, pady=5)

        self.volume_label = ctk.CTkLabel(self.audio_frame, text=f"Master Volume: {self.config_data.get('volume', 80)}%")
        self.volume_label.pack(anchor="w", padx=15, pady=(5, 0))

        self.slider_volume = ctk.CTkSlider(
            self.audio_frame,
            from_=0,
            to=100,
            number_of_steps=20,
            command=self.update_volume_label
        )
        self.slider_volume.set(self.config_data.get("volume", 80))
        self.slider_volume.pack(fill="x", padx=15, pady=(0, 15))

        self.battery_frame = ctk.CTkFrame(self)
        self.battery_frame.pack(pady=10, padx=20, fill="x")

        self.bat_title = ctk.CTkLabel(
            self.battery_frame,
            text="Persentasi Baterai",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.bat_title.pack(anchor="w", padx=15, pady=(10, 5))

        bat_cfg = self.config_data.get("baterai", {})
        self.switch_plug = ctk.CTkSwitch(
            self.battery_frame,
            text="Deteksi Colok / Cabut Charger",
            onvalue=True,
            offvalue=False
        )
        if bat_cfg.get("colok_cabut", True):
            self.switch_plug.select()
        else:
            self.switch_plug.deselect()
        self.switch_plug.pack(anchor="w", padx=15, pady=5)

        self.crit_label = ctk.CTkLabel(self.battery_frame, text=f"Ambang Baterai Kritis: {bat_cfg.get('persentasi_baterai', 20)}%")
        self.crit_label.pack(anchor="w", padx=15, pady=(5, 0))

        self.slider_crit = ctk.CTkSlider(
            self.battery_frame,
            from_=10,
            to=35,
            number_of_steps=25,
            command=self.update_crit_label
        )
        self.slider_crit.set(bat_cfg.get("persentasi_baterai", 20))
        self.slider_crit.pack(fill="x", padx=15, pady=(0, 15))

        self.notif_frame = ctk.CTkFrame(self)
        self.notif_frame.pack(pady=10, padx=20, fill="x")

        self.notif_title = ctk.CTkLabel(
            self.notif_frame,
            text="Notif",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.notif_title.pack(anchor="w", padx=15, pady=(10, 5))

        notif_cfg = self.config_data.get("notifikasi", {})
        self.switch_chat = ctk.CTkSwitch(
            self.notif_frame,
            text="Notif Chat",
            onvalue=True,
            offvalue=False
        )
        if notif_cfg.get("pantau_chat", True):
            self.switch_chat.select()
        else:
            self.switch_chat.deselect()
        self.switch_chat.pack(anchor="w", padx=15, pady=5)

        self.switch_call = ctk.CTkSwitch(
            self.notif_frame,
            text="Panggilan Masuk",
            onvalue=True,
            offvalue=False
        )
        if notif_cfg.get("pantau_telepon", True):
            self.switch_call.select()
        else:
            self.switch_call.deselect()
        self.switch_call.pack(anchor="w", padx=15, pady=(5, 15))

        self.btn_save = ctk.CTkButton(
            self,
            text="Simpan",
            font=ctk.CTkFont(weight="bold"),
            height=38,
            command=self.simpan_perubahan
        )
        self.btn_save.pack(pady=(15, 5), padx=20, fill="x")

        self.status_save_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11), text_color="#2ecc71")
        self.status_save_label.pack()

    def update_volume_label(self, value):
        self.volume_label.configure(text=f"Master Volume: {int(value)}%")

    def update_crit_label(self, value):
        self.crit_label.configure(text=f"Persentasi Baterai {int(value)}%")

    def simpan_perubahan(self):
        new_data = {
            "suara_aktif": bool(self.switch_voice.get()),
            "volume": int(self.slider_volume.get()),
            "baterai": {
                "colok_cabut": bool(self.switch_plug.get()),
                "persentasi_baterai": int(self.slider_crit.get()),
                "ambang_penuh": self.config_data.get("baterai", {}).get("ambang_penuh", 90)
            },
            "notifikasi": {
                "pantau_chat": bool(self.switch_chat.get()),
                "pantau_telepon": bool(self.switch_call.get()),
                "cooldown_detik": self.config_data.get("notifikasi", {}).get("cooldown_detik", 4)
            },
            "sistem": self.config_data.get("sistem", {"run_on_startup": True})
        }

        if simpan_config(new_data):
            self.config_data = new_data
            self.status_save_label.configure(text="Tersimpan")
            self.after(2500, lambda: self.status_save_label.configure(text=""))

if __name__ == "__main__":
    # Jalankan engine otomatis sebelum window dashboard tampil
    start_engine_if_not_running()
    
    app = GreatSageDashboard()
    app.mainloop()