import json, pyaudio
from vosk import Model, KaldiRecognizer
import webbrowser
import subprocess
import tkinter
from tkinter import messagebox

#переменные

model = Model("Vosk\small-model") #путь к модели от Vosk
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

stream.start_stream()

#функции

def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if (rec.AcceptWaveform(data)) and (len(data)>0):
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text'] #как варик использовать return, но это хрень делает генератор из-за чего for работает всегда до получения нормального значения

for text in listen():
    if text =='пока':
        messagebox.showinfo("Помощник", f"Пока")
        quit() #выход
    elif text =='гугл':
        webbrowser.open("https://www.google.com/?hl=ru") #открывает ссылку в браузере
    elif text =='': #фраза запуска
        subprocess.Popen(r"") #открывает приложение(вставить полный путь до файла запуска)
    else:
        messagebox.showinfo("Помощник", text) #выдаёт текст в окне
