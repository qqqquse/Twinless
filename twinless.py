import os
import hashlib
import shutil
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import Image
import subprocess
import platform

output_widget = None
progress_bar = None
progress_label = None
status_label = None
open_folder_btn = None
duplicates_folder_global = None


def log(text, tag=None):
    print(text)
    if output_widget:
        tag_map = {
            "info": "info",
            "success": "success",
            "error": "error",
            None: "default"
        }
        used_tag = tag_map.get(tag, "default")
        output_widget.insert("end", text + "\n", used_tag)
        output_widget.see("end")
        output_widget.update()


def get_image_fingerprint(path):
    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            size = img.size
            pixels = img.tobytes()
            return hashlib.sha256(pixels + str(size).encode()).hexdigest()
    except Exception as e:
        log(f"[Ошибка] {path}: {e}", tag="error")
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
    log(f"[Дубликат] {file_path} → backup", tag="success")


def open_folder(path):
    """Открыть папку в проводнике ОС"""
    if not os.path.exists(path):
        log("[Ошибка] Папка не найдена", tag="error")
        return

    system_name = platform.system()
    try:
        if system_name == "Windows":
            os.startfile(path)
        elif system_name == "Darwin":  # MacOS
            subprocess.Popen(["open", path])
        else:  # Linux и другие
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        log(f"[Ошибка] Не удалось открыть папку: {e}", tag="error")


def find_and_handle_duplicates(folder, app=None):
    global duplicates_folder_global, open_folder_btn

    duplicates_folder_global = os.path.join(folder, "duplicates_backup")
    open_folder_btn.configure(state="disabled")  # деактивируем кнопку во время работы

    fingerprints = {}

    all_images = [
        os.path.join(root, name)
        for root, _, files in os.walk(folder)
        for name in files
        if name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'))
    ]

    total_files = len(all_images)
    duplicates_found = 0

    log(f"🔍 Найдено изображений: {total_files}\n", tag="info")
    progress_bar.configure(mode="determinate", maximum=total_files, value=0)
    progress_label.config(text="0 / 0")

    for i, file_path in enumerate(all_images, 1):
        if os.path.abspath(os.path.dirname(file_path)) == os.path.abspath(duplicates_folder_global):
            continue

        log(f"[{i}/{total_files}] Проверка: {file_path}", tag="info")
        fingerprint = get_image_fingerprint(file_path)

        if fingerprint:
            if fingerprint in fingerprints:
                move_file_to_backup(file_path, duplicates_folder_global)
                duplicates_found += 1
            else:
                fingerprints[fingerprint] = file_path

        progress_bar.configure(value=i)
        progress_label.config(text=f"{i} / {total_files}")
        status_label.config(text=f"Обработка: {os.path.basename(file_path)}")
        app.update_idletasks()

    log("\n=== ✅ РЕЗУЛЬТАТ ===", tag="success")
    log(f"📦 Перемещено дубликатов: {duplicates_found}", tag="success")
    log(f"💾 Backup: {duplicates_folder_global}", tag="info")
    log("🛑 Удаления не было — только перенос в backup", tag="info")
    status_label.config(text="Готово ✅", foreground="#28a745")  # зелёный

    # Активируем кнопку открыть папку
    open_folder_btn.configure(state="normal")


def choose_folder(app):
    folder = filedialog.askdirectory()
    if folder:
        output_widget.delete("1.0", "end")
        log(f"📁 Папка выбрана: {folder}\n", tag="info")
        status_label.config(text="Ожидание...", foreground="#ffc107")  # жёлтый
        find_and_handle_duplicates(folder, app)


def start_gui():
    global output_widget, progress_bar, progress_label, status_label, open_folder_btn

    app = tb.Window(themename="darkly")
    app.title("Twinless")
    app.geometry("940x700")
    app.resizable(False, False)

    tb.Label(app, text="Twinless", font=("Segoe UI", 36, "bold"), foreground="white").pack(pady=(20, 5))
    tb.Label(app,
             text="Найдите и переместите дубликаты изображений",
             font=("Segoe UI", 12),
             foreground="white").pack()

    tb.Button(app,
              text="Выбрать папку и начать",
              bootstyle="info-outline",
              width=30,
              padding=10,
              command=lambda: choose_folder(app)).pack(pady=20)

    progress_frame = tb.Frame(app)
    progress_frame.pack(pady=(10, 5))

    progress_bar = tb.Progressbar(progress_frame, orient="horizontal", length=600, mode="determinate", bootstyle="info")
    progress_bar.pack(side="left", padx=(10, 10))

    progress_label = tb.Label(progress_frame, text="0 / 0", font=("Segoe UI", 10), foreground="white")
    progress_label.pack(side="left")

    status_label = tb.Label(app, text="Ожидание...", font=("Segoe UI", 10))
    status_label.pack(pady=(0, 10))

    open_folder_btn = tb.Button(app,
                               text="Открыть папку",
                               bootstyle="secondary",
                               width=25,
                               padding=8,
                               state="disabled",
                               command=lambda: open_folder(duplicates_folder_global))
    open_folder_btn.pack(pady=(0, 15))

    log_frame = tb.Frame(app)
    log_frame.pack(padx=20, pady=10, fill="both", expand=True)

    output_widget = ScrolledText(log_frame, wrap="word", font=("Consolas", 10), height=20, bg="#222222", fg="white", insertbackground="white")
    output_widget.pack(fill="both", expand=True)

    output_widget.tag_config("info", foreground="#007ACC")      # синий
    output_widget.tag_config("success", foreground="#28a745")   # насыщенный зелёный
    output_widget.tag_config("error", foreground="#ff6c6b")     # красный
    output_widget.tag_config("default", foreground="#ffffff")   # белый

    app.mainloop()


if __name__ == "__main__":
    start_gui()
