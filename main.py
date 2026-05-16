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
    from jnius import autoclass, PythonJavaClass, java_method
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    RecognizerIntent = autoclass('android.speech.RecognizerIntent')
    SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
    TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
    Locale = autoclass('java.util.Locale')
    AudioManager = autoclass('android.media.AudioManager')
    android_hazir = True
except Exception as e:
    print("Android kütüphane yükleme hatası:", e)

if android_hazir:
    class RecognitionListener(PythonJavaClass):
        __javainterfaces__ = ['android/speech/RecognitionListener']
        
        def __init__(self, callback):
            super(RecognitionListener, self).__init__()
            self.callback = callback
            
        @java_method('([Ljava/lang/String;)v')
        def onResults(self, results):
            matches = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
            if matches and matches.size() > 0:
                self.callback(str(matches.get(0)))
                
        @java_method('(I)v')
        def onError(self, error):
            self.callback(f"HATA_KODU_{error}")
            
        @java_method('(Landroid/os/Bundle;)v')
        def onReadyForSpeech(self, params): pass
        @java_method('()v')
        def onBeginningOfSpeech(self): pass
        @java_method('([B)v')
        def onRmsChanged(self, rmsdB): pass
        @java_method('()v')
        def onBufferReceived(self): pass
        @java_method('()v')
        def onEndOfSpeech(self): pass
        @java_method('(ILandroid/os/Bundle;)v')
        def onPartialResults(self, partialResults): pass
        @java_method('(ILandroid/os/Bundle;)v')
        def onEvent(self, eventType, params): pass

class AsistanApp(App):
    def build(self):
        self.tts = None
        self.speech_recognizer = None
        self.api_key = "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" 
        
        self.gecmis = [
            {"role": "system", "content": "Sen Poco C65 telefonunda çalışan, çok samimi, zeki, esprili ve Türkçe konuşan bir sesli asistansın. Adın Jarvis. Cümlelerini bir sesli asistan gibi kısa, net ve akıcı tut ki seni dinlemek keyifli olsun. Uzun paragraflar yazma."}
        ]
        
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        scroll = ScrollView(size_hint=(1, 0.5))
        self.label = Label(
            text="Jarvis Sesli Sistemi Aktif!\nButona basın, konuşun ve beni dinleyin.",
            font_size='16sp', halign='center', valign='middle', size_hint_y=None
        )
        self.label.bind(size=lambda s, w: setattr(self.label, 'text_size', (w[0] - 20, None)))
        self.label.bind(texture_size=lambda s, t: setattr(self.label, 'height', t[1]))
        scroll.add_widget(self.label)
        main_layout.add_widget(scroll)
        
        self.input_box = TextInput(
            hint_text="Buraya da yazabilirsiniz...",
            size_hint=(1, 0.15), multiline=False, font_size='16sp'
        )
        main_layout.add_widget(self.input_box)
        
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=10)
        
        self.btn_send = Button(text="Yazıyı Gönder", background_color=(0.2, 0.6, 1, 1))
        self.btn_send.bind(on_press=self.metin_gonder)
        
        self.btn_mic = Button(text="🎙 KONUŞ VE DİNLE", background_color=(0.2, 0.8, 0.2, 1))
        self.btn_mic.bind(on_press=self.sesi_baslat)
        
        button_layout.add_widget(self.btn_send)
        button_layout.add_widget(self.btn_mic)
        main_layout.add_widget(button_layout)
        
        if android_hazir:
            Clock.schedule_once(lambda dt: self.sistemleri_hazirla(), 1)
        
        return main_layout

    def sistemleri_hazirla(self):
        try:
            activity = PythonActivity.mActivity
            self.tts = TextToSpeech(activity, None)
            self.tts.setLanguage(Locale("tr", "TR"))
            
            audio_manager = activity.getSystemService(Context.AUDIO_SERVICE)
            max_volume = audio_manager.getStreamMaxVolume(AudioManager.STREAM_MUSIC)
            audio_manager.setStreamVolume(AudioManager.STREAM_MUSIC, int(max_volume * 0.8), 0)

            activity.runOnUiThread(threading.Thread(target=self.recognizer_kur).start)
        except Exception as e:
            self.label.text = f"Ses motoru hazır değil: {e}"

    def recognizer_kur(self):
        activity = PythonActivity.mActivity
        self.speech_recognizer = SpeechRecognizer.createSpeechRecognizer(activity)
        self.listener = RecognitionListener(self.ses_sonucu_geldi)
        self.speech_recognizer.setRecognitionListener(self.listener)

    def konustur(self, metin):
        if android_hazir and self.tts:
            try:
                self.tts.speak(metin, TextToSpeech.QUEUE_FLUSH, None, None)
            except Exception as e:
                print("Konuşma hatası:", e)

    def metin_gonder(self, instance):
        soru = self.input_box.text.strip()
        if soru:
            self.label.text = f"Soru: {soru}\n\nJarvis düşünüyor..."
            self.input_box.text = ""
            self.gecmis.append({"role": "user", "content": soru})
            threading.Thread(target=self.groq_sorgula).start()

    def sesi_baslat(self, instance):
        if android_hazir and self.speech_recognizer:
            self.label.text = "Dinleniyor... Konuşun..."
            try:
                intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "tr-TR")
                
                PythonActivity.mActivity.runOnUiThread(lambda: self.speech_recognizer.startListening(intent))
            except Exception as e:
                self.label.text = f"Mikrofon hatası:\n{str(e)}"

    def ses_sonucu_geldi(self, sonuc):
        if sonuc.startswith("HATA_KODU_"):
            self.label.text = "Sesi tam alamadım, tekrar basıp konuşur musun?"
        else:
            self.label.text = f"Soru (Sesli): {sonuc}\n\nJarvis düşünüyor..."
            self.gecmis.append({"role": "user", "content": sonuc})
            threading.Thread(target=self.groq_sorgula).start()

    def groq_sorgula(self):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": self.gecmis
            }

            response = requests.post(url, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                cevap = response.json()['choices'][0]['message']['content']
                self.gecmis.append({"role": "assistant", "content": cevap})
                Clock.schedule_once(lambda dt: self.ui_guncelle(cevap), 0)
                self.konustur(cevap)
            else:
                Clock.schedule_once(lambda dt: self.ui_guncelle(f"Hata: {response.status_code}"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.ui_guncelle(f"Bağlantı kesildi:\n{str(e)}"), 0)

    def ui_guncelle(self, metin):
        self.label.text = metin

if __name__ == "__main__":
    AsistanApp().run()
