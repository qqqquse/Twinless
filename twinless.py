import tkinter as tk
import hashLin
from PIL import Image

def log(text):
    print(text)
    if output_widget:
        output_widget.insert(tk.END, text + '\n')
        output_widget.see(tk.END)
        output_widget.update()
output_widget = None  # Связь с интерфейсом

def get_image_fingerprint(path):
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            size = img.size
            pixels = img.tobytes()
            return hashlib.sha256(pixels + str(size).encode()).hexdigest()
    except Exception as e:
        log(f"[Ошибка] Не удалось обработать файл {path}: {e}")
        return None
