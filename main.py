from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from jnius import autoclass
import requests
import threading

# Android yerel Ses ve Konuşma sınıflarını çağırıyoruz
try:
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    RecognizerIntent = autoclass('android.speech.RecognizerIntent')
    SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    Locale = autoclass('java.util.Locale')
except Exception as e:
    print("Android sınıfları sadece telefonda yüklenebilir:", e)

class AsistanApp(App):
    def build(self):
        self.tts = None
        self.api_key = "AIzaSyBi5-oS8jxZJDhZxljhpMVoalWFQ9UxfCw" # <--- KENDİ GEMINI KEY'İNİ BURAYA YAPIŞTIR
        
        # Ana Dikey Arayüz
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        # 1. Cevap Alanı (Kaydırılabilir Uzun Metinler İçin)
        scroll = ScrollView(size_hint=(1, 0.5))
        self.label = Label(
            text="Poco C65 Jarvis Asistan Hazır!\nİster yazın, ister mikrofon butonuna basıp konuşun.",
            font_size='16sp', halign='center', valign='middle', size_hint_y=None
        )
        self.label.bind(size=lambda s, w: setattr(self.label, 'text_size', (w[0] - 20, None)))
        self.label.bind(texture_size=lambda s, t: setattr(self.label, 'height', t[1]))
        scroll.add_widget(self.label)
        main_layout.add_widget(scroll)
        
        # 2. Yazarak İletişim İçin Girdi Kutusu
        self.input_box = TextInput(
            hint_text="Buraya yazabilirsiniz...",
            size_hint=(1, 0.15), multiline=False, font_size='16sp'
        )
        main_layout.add_widget(self.input_box)
        
        # 3. Butonlar Paneli (Yan yana)
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        self.btn_send = Button(text="Yazıyı Gönder", background_color=(0.2, 0.6, 1, 1))
        self.btn_send.bind(on_press=self.metin_gonder)
        
        self.btn_mic = Button(text="🎙 Konuş", background_color=(0.2, 0.8, 0.2, 1))
        self.btn_mic.bind(on_press=self.sesi_baslat)
        
        button_layout.add_widget(self.btn_send)
        button_layout.add_widget(self.btn_mic)
        main_layout.add_widget(button_layout)
        
        # Android TTS (Konuşma) Motorunu Arka Planda Başlat
        Clock.schedule_once(lambda dt: self.tts_hazirla(), 1)
        
        return main_layout

    def tts_hazirla(self):
        try:
            activity = PythonActivity.mActivity
            self.tts = TextToSpeech(activity, None)
            # Varsayılan dili Türkçe yapıyoruz
            self.tts.setLanguage(Locale("tr", "TR"))
        except:
            pass

    def konustur(self, metin):
        if self.tts:
            try:
                # Yapay zekadan gelen cevabı telefona sesli okutuyoruz
                self.tts.speak(metin, TextToSpeech.QUEUE_FLUSH, None, None)
            except:
                pass

    def metin_gonder(self, instance):
        soru = self.input_box.text.strip()
        if soru:
            self.label.text = f"Soru: {soru}\n\nAsistan düşünüyor..."
            self.input_box.text = ""
            threading.Thread(target=self.gemini_sorgula, args=(soru,)).start()

    def sesi_baslat(self, instance):
        self.label.text = "Dinleniyor... Konuşun..."
        try:
            activity = PythonActivity.mActivity
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "tr-TR")
            # Android'in ses tanıma ekranını tetikliyoruz
            activity.startActivityForResult(intent, 100)
            # NOT: Android sonuç döndürdüğünde Kivy activity_result mekanizmasıyla bunu yakalayabiliriz.
            # Şimdilik stabilite için arayüz kilitlenmesini bu butonla çözüyoruz.
        except Exception as e:
            self.label.text = f"Mikrofon başlatılamadı (Sadece Android'de çalışır):\n{str(e)}"

    def gemini_sorgula(self, soru):
        try:
            if self.api_key == "YOUR_GEMINI_API_KEY":
                Clock.schedule_once(lambda dt: self.ui_guncelle("Hata: Lütfen kodun içine API anahtarını gir."), 0)
                return

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            headers = {'Content-Type': 'application/json'}
            data = {"contents": [{"parts": [{"text": soru}]}]}

            response = requests.post(url, headers=headers, json=data, timeout=12)
            
            if response.status_code == 200:
                cevap = response.json()['candidates'][0]['content']['parts'][0]['text']
                Clock.schedule_once(lambda dt: self.ui_guncelle(cevap), 0)
                # Ekstra Özellik: Yapay zeka cevabı hem yazacak hem de sesli okuyacak!
                self.konustur(cevap)
            else:
                Clock.schedule_once(lambda dt: self.ui_guncelle(f"Hata Kodu: {response.status_code}"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.ui_guncelle(f"Bağlantı hatası:\n{str(e)}"), 0)

    def ui_guncelle(self, metin):
        self.label.text = metin

if __name__ == "__main__":
    AsistanApp().run()
