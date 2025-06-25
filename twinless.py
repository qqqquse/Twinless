import tkinter as tk

output_widget = None  # Связь с интерфейсом

def log(text):
    print(text)
    if output_widget:
        output_widget.insert(tk.END, text + '\n')
        output_widget.see(tk.END)
        output_widget.update()

