import json, pyaudio, pygetwindow, webbrowser, subprocess, tkinter
from vosk import Model, KaldiRecognizer
from tkinter import messagebox
import pygetwindow as gw

#переменные
gpk = "" #переменная с названием интересующего окна

model = Model("Vosk\small-model") #путь к модели от Vosk его нужно будет изменить под себя
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

stream.start_stream()

#функции
def bring_to_front(gpk): #функция для открытия свёрнутого окна 
    windows = gw.getWindowsWithTitle(gpk)
    if windows:
        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        return True
    return False

def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if (rec.AcceptWaveform(data)) and (len(data)>0):
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text'] #как варик использовать return, но yield делает генератор из-за чего for text in listen() работает до получения нормального значения которое модель может обработать

for text in listen():
    if text =='пока':
        messagebox.showinfo("Помощник", f"Пока")
        quit() #выход
    elif text =='гугл':
        webbrowser.open("https://www.google.com/?hl=ru") #открывает ссылку в браузере
    elif text =='связь': #фраза запуска
        subprocess.Popen(r"") #открывает приложение(вставить полный путь до файла запуска), но не открывает окна уже запущенных приложений
    elif text =='открыть': 
        bring_to_front(gpk)    
    else:
        messagebox.showinfo("Помощник", text) #выдаёт текст в окне
