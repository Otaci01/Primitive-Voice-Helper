import json, threading, queue, pyaudio, webbrowser, subprocess, os
from vosk import Model, KaldiRecognizer
import pygetwindow as gw
import customtkinter as ctk

#переменные
rucommand_queue = queue.Queue()   # сюда фоновый поток сохраняет распознанный ru текст
encommand_queue = queue.Queue()   # сюда поток сохраняет распознанный англ текст

mode = "commands"             # "commands" — ru модель
                               # "window_name_open" и "window_name_close" — англ модель
mode_lock = threading.Lock()  # защищает переменную mode от гонки между потоками

modelru = Model("Vosk\\model-ru")  # путь к ru модели от Vosk, его нужно будет изменить под себя
recru = KaldiRecognizer(modelru, 16000)
modelen = Model("Vosk\\model-en")  # путь к англ модели от Vosk, его нужно будет изменить под себя
recen = KaldiRecognizer(modelen, 16000)


p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

stream.start_stream()

#функции
def bring_to_front(gpk):
    windows = gw.getWindowsWithTitle(gpk)
    if windows:
        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        return True
    return False

def close(gpk):
    windows = gw.getWindowsWithTitle(gpk)
    if windows:
        win = windows[0]
        if win.isMinimized:
            win.restore()
        win.close()
        return True
    return False

def clear_queue(q):
    
    with q.mutex:
        q.queue.clear()

def listen_loop():
    #читает микрофон и кладёт распознанный текст в очередь на фоне
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if (recru.AcceptWaveform(data)) and (len(data) > 0):
            answerru = json.loads(recru.Result())
            if answerru['text']:
                rucommand_queue.put(answerru['text'])
        if (recen.AcceptWaveform(data)) and (len(data) > 0):
            answeren = json.loads(recen.Result())
            if answeren['text']:
                encommand_queue.put(answeren['text'])

def process_commands():
    #Находится в главном потоке через root.after
    global mode
    try:
        while True:
            with mode_lock:
                current_mode = mode

            if current_mode == "commands":
                text = rucommand_queue.get_nowait()
                label.configure(text=text)  # показываем последнюю распознанную фразу прямо в окне

                if text == 'пока':
                    on_close()
                    return
                elif text == 'гугл':
                    webbrowser.open("https://www.google.com/?hl=ru") #открывает ссылку в браузере
                elif text == 'связь': #фраза запуска
                    subprocess.Popen(r"C:\Users\skril\AppData\Local\Discord\Update.exe --processStart Discord.exe") #открывает приложение(вставить полный путь до файла запуска), но не открывает окна уже запущенных приложений
                elif text == 'обход': #фраза запуска
                    subprocess.Popen(r"C:\Program Files\FlyFrogLLC\Happ\Happ.exe")
                elif text == 'открыть':
                    label.configure(text="Скажите название окна (на английском)...")
                    clear_queue(encommand_queue)  # выкидываем прошлые фразы, что английская модель успела распознать раньше
                    with mode_lock:
                        mode = "window_name_open"
                elif text == 'закрыть':
                    label.configure(text="Скажите название окна (на английском)...")
                    clear_queue(encommand_queue)  # выкидываем прошлые фразы, что английская модель успела распознать раньше
                    with mode_lock:
                        mode = "window_name_close"
               

            elif current_mode == "window_name_open":
                window_title = encommand_queue.get_nowait()
                label.configure(text=f"Ищу окно: {window_title}")
                bring_to_front(window_title)
                clear_queue(rucommand_queue)  # после команды открыть выкидываем ру текст из очереди
                with mode_lock:
                    mode = "commands"  # вернулись к обычным командам

            else:  # current_mode == "window_name_close"
                window_title = encommand_queue.get_nowait()
                label.configure(text=f"Закрываю окно: {window_title}")
                close(window_title)
                clear_queue(rucommand_queue)  # после команды закрыть выкидываем ру текст из очереди
                with mode_lock:
                    mode = "commands"  # вернулись к обычным командам

    except queue.Empty:
        pass
    root.after(100, process_commands)  # проверяем очереди каждые 100мс

def on_close(): #исключение ошибки при закрытии окна
    root.destroy()
    os._exit(0)  # команда остановки процесса


ctk.set_appearance_mode("dark")
root = ctk.CTk()
label = ctk.CTkLabel(root, text="Ассистент активен")
label.pack(padx=20, pady=20)

root.protocol("WM_DELETE_WINDOW", on_close)  

threading.Thread(target=listen_loop, daemon=True).start()  # распознавание речи в фоне
root.after(100, process_commands)  # обработка команд в главном потоке

root.mainloop()
