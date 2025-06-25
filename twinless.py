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

def find_and_handle_duplicates(folder, app=None):
    fingerprints = {}
    duplicates_folder = os.path.join(folder, "duplicates_backup")
    total_files = 0
    duplicates_found = 0

    # Сбор изображений
    all_images = []
    for root, _, files in os.walk(folder):
        for name in files:
            if name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')):
                all_images.append(os.path.join(root, name))

    total_files = len(all_images)
    log(f"Всего изображений для обработки: {total_files}\n")

    for i, file_path in enumerate(all_images, 1):
        if os.path.abspath(os.path.dirname(file_path)) == os.path.abspath(duplicates_folder):
            continue

        log(f"[{i}/{total_files}] Проверка: {file_path}")
        if app:
            app.update()

        fingerprint = get_image_fingerprint(file_path)
        if fingerprint:
            if fingerprint in fingerprints:
                move_file_to_backup(file_path, duplicates_folder)
                duplicates_found += 1
            else:
                fingerprints[fingerprint] = file_path
                
    log("\n=== РЕЗУЛЬТАТ ===")
    log(f"Всего изображений обработано: {total_files}")
    log(f"Дубликатов найдено и перемещено: {duplicates_found}")
    log(f"Дубликаты перемещены в: {duplicates_folder}")
    log("Ничего не удалено без копии! Проверь backup и при желании очисти вручную.")
