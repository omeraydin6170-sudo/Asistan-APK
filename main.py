from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import requests
import threading

android_hazir = False
try:
    from jnius import autoclass, activity
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    RecognizerIntent = autoclass('android.speech.RecognizerIntent')
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    Locale = autoclass('java.util.Locale')
    android_hazir = True
except Exception as e:
    print("Android kütüphaneleri yüklenemedi, simüle ediliyor.")

class AsistanApp(App):
    def build(self):
        self.tts = None
        # Çalışan gsk_... anahtarını BURAYA yapıştır
        self.api_key = "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" 
        
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        scroll = ScrollView(size_hint=(1, 0.5))
        self.label = Label(
            text="Poco C65 Jarvis Hazır!\nYazın veya mikrofon butonuna basıp konuşun.",
            font_size='16sp', halign='center', valign='middle', size_hint_y=None
        )
        self.label.bind(size=lambda s, w: setattr(self.label, 'text_size', (w[0] - 20, None)))
        self.label.bind(texture_size=lambda s, t: setattr(self.label, 'height', t[1]))
        scroll.add_widget(self.label)
        main_layout.add_widget(scroll)
        
        self.input_box = TextInput(
            hint_text="Buraya yazabilirsiniz...",
            size_hint=(1, 0.15), multiline=False, font_size='16sp'
        )
        main_layout.add_widget(self.input_box)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        self.btn_send = Button(text="Yazıyı Gönder", background_color=(0.2, 0.6, 1, 1))
        self.btn_send.bind(on_press=self.metin_gonder)
        
        self.btn_mic = Button(text="🎙 Konuş", background_color=(0.2, 0.8, 0.2, 1))
        self.btn_mic.bind(on_press=self.sesi_baslat)
        
        button_layout.add_widget(self.btn_send)
        button_layout.add_widget(self.btn_mic)
        main_layout.add_widget(button_layout)
        
        if android_hazir:
            # Android'in ses sonucunu dinleyen mekanizmayı bağlıyoruz
            activity.bind(on_activity_result=self.ses_sonucunu_yakala)
            Clock.schedule_once(lambda dt: self.tts_hazirla(), 1)
        
        return main_layout

    def tts_hazirla(self):
        if android_hazir:
            try:
                current_activity = PythonActivity.mActivity
                self.tts = TextToSpeech(current_activity, None)
                self.tts.setLanguage(Locale("tr", "TR"))
            except:
                pass

    def konustur(self, metin):
        if android_hazir and self.tts:
            try:
                self.tts.speak(metin, TextToSpeech.QUEUE_FLUSH, None, None)
            except:
                pass

    def metin_gonder(self, instance):
        soru = self.input_box.text.strip()
        if soru:
            self.label.text = f"Soru: {soru}\n\nJarvis düşünüyor..."
            self.input_box.text = ""
            threading.Thread(target=self.groq_sorgula, args=(soru,)).start()

    def sesi_baslat(self, instance):
        if android_hazir:
            self.label.text = "Dinleniyor... Konuşun..."
            try:
                current_activity = PythonActivity.mActivity
                intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "tr-TR")
                # 100 istek koduyla ses ekranını açıyoruz
                current_activity.startActivityForResult(intent, 100)
            except Exception as e:
                self.label.text = f"Mikrofon başlatılamadı:\n{str(e)}"

    # Google sesi yazıya döküp bitirdiğinde burası tetiklenir
    def ses_sonucunu_yakala(self, request_code, result_code, intent_data):
        if request_code == 100:
            # RESULT_OK genelde -1'dir Android dünyasında
            try:
                matches = intent_data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                if matches and matches.size() > 0:
                    soru = matches.get(0) # Google'ın anladığı ilk ve en doğru cümleyi alıyoruz
                    Clock.schedule_once(lambda dt: self.sesli_soruyu_gonder(soru), 0)
                else:
                    self.label.text = "Ses anlaşılamadı, lütfen tekrar deneyin."
            except Exception as e:
                self.label.text = "Ses verisi alınırken hata oluştu."

    def sesli_soruyu_gonder(self, soru):
        self.label.text = f"Soru (Sesli): {soru}\n\nJarvis düşünüyor..."
        threading.Thread(target=self.groq_sorgula, args=(soru,)).start()

    def groq_sorgula(self, soru):
        try:
            if self.api_key == "YOUR_GROQ_API_KEY":
                Clock.schedule_once(lambda dt: self.ui_guncelle("Hata: Lütfen Groq API anahtarını girin."), 0)
                return

            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": soru}]
            }

            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                cevap = response.json()['choices'][0]['message']['content']
                Clock.schedule_once(lambda dt: self.ui_guncelle(cevap), 0)
                self.konustur(cevap)
            else:
                Clock.schedule_once(lambda dt: self.ui_guncelle(f"Hata Kodu: {response.status_code}\nDetay: {response.text[:100]}"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.ui_guncelle(f"Bağlantı hatası:\n{str(e)}"), 0)

    def ui_guncelle(self, metin):
        self.label.text = metin

if __name__ == "__main__":
    AsistanApp().run()
