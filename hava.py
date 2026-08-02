import customtkinter as ctk
import requests
from PIL import Image
from io import BytesIO

# Görünüm Teması Ayarları
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WeatherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere Yapılandırması
        self.title("Hava Durumu Pro")
        self.geometry("450x600")
        self.resizable(False, False)

        # API Anahtarınız
        self.API_KEY = "947838da0a30faf08ecde71e8130f2fb"

        # Arayüz Bileşenleri
        self.setup_ui()

    def setup_ui(self):
        # 1. BAŞLIK VE ARAMA BÖLÜMÜ
        self.title_label = ctk.CTkLabel(
            self, text="Hava Durumu", font=ctk.CTkFont(size=26, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))

        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.pack(fill="x", padx=30, pady=10)

        self.city_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Şehir adı giriniz (Örn: İzmir)...",
            width=260,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.city_entry.pack(side="left", padx=(0, 10))
        self.city_entry.bind("<Return>", lambda event: self.get_weather())

        self.search_btn = ctk.CTkButton(
            self.search_frame,
            text="Ara",
            width=100,
            height=40,
            command=self.get_weather,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.search_btn.pack(side="right")

        # 2. ANA HAVA DURUMU KARTI
        self.main_card = ctk.CTkFrame(self, corner_radius=20)
        self.main_card.pack(fill="both", expand=True, padx=30, pady=(10, 20))

        self.location_label = ctk.CTkLabel(
            self.main_card, text="-", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.location_label.pack(pady=(20, 5))

        self.icon_label = ctk.CTkLabel(self.main_card, text="")
        self.icon_label.pack(pady=5)

        self.temp_label = ctk.CTkLabel(
            self.main_card, text="--°C", font=ctk.CTkFont(size=42, weight="bold")
        )
        self.temp_label.pack(pady=5)

        self.desc_label = ctk.CTkLabel(
            self.main_card, text="-", font=ctk.CTkFont(size=16)
        )
        self.desc_label.pack(pady=(0, 15))

        # 3. DETAY BİLGİLERİ KARTI
        self.details_frame = ctk.CTkFrame(self.main_card, fg_color=("gray85", "gray17"), corner_radius=15)
        self.details_frame.pack(fill="x", padx=20, pady=10)
        self.details_frame.columnconfigure((0, 1, 2), weight=1)

        self.feels_val = ctk.CTkLabel(self.details_frame, text="--°C", font=ctk.CTkFont(size=14, weight="bold"))
        self.feels_val.grid(row=0, column=0, pady=(10, 0))
        ctk.CTkLabel(self.details_frame, text="Hissedilen", font=ctk.CTkFont(size=11), text_color="gray").grid(row=1, column=0, pady=(0, 10))

        self.humidity_val = ctk.CTkLabel(self.details_frame, text="--%", font=ctk.CTkFont(size=14, weight="bold"))
        self.humidity_val.grid(row=0, column=1, pady=(10, 0))
        ctk.CTkLabel(self.details_frame, text="Nem", font=ctk.CTkFont(size=11), text_color="gray").grid(row=1, column=1, pady=(0, 10))

        self.wind_val = ctk.CTkLabel(self.details_frame, text="-- km/s", font=ctk.CTkFont(size=14, weight="bold"))
        self.wind_val.grid(row=0, column=2, pady=(10, 0))
        ctk.CTkLabel(self.details_frame, text="Rüzgar", font=ctk.CTkFont(size=11), text_color="gray").grid(row=1, column=2, pady=(0, 10))

        # 4. TEMA DEĞİŞTİRME SWITCH
        self.theme_switch = ctk.CTkSwitch(
            self.main_card, text="Koyu Tema", command=self.toggle_theme
        )
        self.theme_switch.pack(pady=15)
        self.theme_switch.select()

    def toggle_theme(self):
        if self.theme_switch.get():
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            return

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.API_KEY}&units=metric&lang=tr"

        try:
            response = requests.get(url, timeout=5)
            data = response.json()

            if response.status_code == 200:
                temp = round(data["main"]["temp"])
                feels_like = round(data["main"]["feels_like"])
                humidity = data["main"]["humidity"]
                wind_speed = round(data["wind"]["speed"] * 3.6, 1)
                desc = data["weather"][0]["description"].capitalize()
                city_name = data["name"]
                country = data["sys"]["country"]
                icon_code = data["weather"][0]["icon"]

                self.location_label.configure(text=f"{city_name}, {country}")
                self.temp_label.configure(text=f"{temp}°C")
                self.desc_label.configure(text=desc, text_color=("black", "white"))
                self.feels_val.configure(text=f"{feels_like}°C")
                self.humidity_val.configure(text=f"%{humidity}")
                self.wind_val.configure(text=f"{wind_speed} km/s")

                self.update_icon(icon_code)
            elif response.status_code == 401:
                self.desc_label.configure(text="API Anahtarı Geçersiz veya Henüz Aktif Değil!", text_color="red")
            else:
                self.desc_label.configure(text="Şehir bulunamadı!", text_color="orange")

        except requests.exceptions.RequestException:
            self.desc_label.configure(text="Bağlantı hatası!", text_color="red")

    def update_icon(self, icon_code):
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        try:
            img_response = requests.get(icon_url, timeout=5)
            img_data = Image.open(BytesIO(img_response.content))
            ctk_icon = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(100, 100))
            self.icon_label.configure(image=ctk_icon)
        except Exception:
            self.icon_label.configure(image=None)


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()