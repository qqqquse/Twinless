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

# === Обработка изображений ===

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

def move_file_to_backup(file_path, backup_folder):
    os.makedirs(backup_folder, exist_ok=True)
    filename = os.path.basename(file_path)
    destination = os.path.join(backup_folder, filename)

    counter = 1
    while os.path.exists(destination):
        name, ext = os.path.splitext(filename)
        destination = os.path.join(backup_folder, f"{name}_{counter}{ext}")
        counter += 1

    shutil.move(file_path, destination)
    log(f"[Дубликат] Перемещён в backup: {file_path}")


