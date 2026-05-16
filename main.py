from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import requests
import threading

class AsistanApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # text_size ve halign ayarları gelen uzun cevapların ekrandan taşmasını engeller (Wrap text)
        self.label = Label(
            text="Poco C65 Asistan Hazır!\nSorunu sormak için butona bas.", 
            font_size='18sp', 
            halign='center', 
            valign='middle'
        )
        self.label.bind(size=lambda s, w: setattr(self.label, 'text_size', (w[0] - 20, None)))
        
        btn = Button(text="Yapay Zekaya Sor", size_hint=(1, 0.2))
        btn.bind(on_press=self.asistan_tetikle)
        
        layout.add_widget(self.label)
        layout.add_widget(btn)
        return layout

    def asistan_tetikle(self, instance):
        # Kullanıcı beklerken arayüzde geri bildirim veriyoruz
        self.label.text = "Asistan düşünüyor, lütfen bekle..."
        
        # İNTERNET İSTEĞİNİ AYRI BİR THREAD'DE BAŞLATIYORUZ (Telefon donmasın diye)
        threading.Thread(target=self.yapay_zeka_baglantisi).start()

    def yapay_zeka_baglantisi(self):
        try:
            # 1. Kendi ücretsiz Gemini API anahtarını alıp aşağıdaki tırnakların içine yapıştırabilirsin.
            # API anahtarın yoksa şimdilik bu haliyle derleyip internet testini doğrulayabilirsin.
            api_key = "YOUR_GEMINI_API_KEY" 
            
            if api_key == "YOUR_GEMINI_API_KEY":
                Clock.schedule_once(lambda dt: self.ui_guncelle("İnternet bağlantı altyapısı hazır! Ancak kodun içindeki 'YOUR_GEMINI_API_KEY' alanına gerçek bir API anahtarı girmen gerekiyor."), 0)
                return

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            
            # Yapay zekaya gönderilecek örnek soru (Bunu ileride bir girdi kutusuna bağlayabiliriz)
            data = {
                "contents": [{"parts":[{"text": "Merhaba! Ben Poco C65 telefonundan bağlanıyorum. Bana kısa, neşeli bir selam ver!"}]}]
            }

            # İstek gönderiliyor (Maksimum 10 saniye bekleme süresi)
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                res_json = response.json()
                # Gemini'den gelen metin cevabını ayıklıyoruz
                cevap = res_json['candidates'][0]['content']['parts'][0]['text']
                # Kivy'de arayüzü güncellemek için ana thread'e güvenli geçiş yapıyoruz
                Clock.schedule_once(lambda dt: self.ui_guncelle(cevap), 0)
            else:
                Clock.schedule_once(lambda dt: self.ui_guncelle(f"Yapay zeka yanıt vermedi.\nHata Kodu: {response.status_code}"), 0)

        except Exception as e:
            # İnternet yoksa veya izin kapalıysa buraya düşer
            Clock.schedule_once(lambda dt: self.ui_guncelle(f"Bağlantı hatası! Telefonun internetini veya buildozer izinlerini kontrol et.\nDetay: {str(e)}"), 0)

    def ui_guncelle(self, metin):
        self.label.text = metin

if __name__ == "__main__":
    AsistanApp().run()
