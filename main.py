
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class AsistanApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.label = Label(text="Poco C65 Asistan Hazır!", font_size='20sp')
        btn = Button(text="Tıkla", size_hint=(1, 0.2))
        btn.bind(on_press=self.degistir)
        layout.add_widget(self.label)
        layout.add_widget(btn)
        return layout

    def degistir(self, instance):
        self.label.text = "Asistan Çalışıyor!"

if __name__ == "__main__":
    AsistanApp().run()
