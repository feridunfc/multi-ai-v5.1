import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self):
        self.root = tk.Tk()
        
        try:
            from calculator_module import buttons  # Kullanıcının kendi modülünde tanımladığı butonlar için
        except ModuleNotFoundError:
            messagebox.showwarning("Uyarı", "calculator_module bulunamadı")  # Modül eksik uyarısı
            buttons = ['0', '1', '2', '3', '/', '4', '5', '6', '*', '7', '8', '9', '-', '=', '.', '+']  # Varsayılan butonlar
        
        for i, button in enumerate(buttons):
            try:
                tk.Button(self.root, text=button, command=lambda button=button: self.func(button)).grid(row=i//4, column=i%4)  # Butonların koordinatlarına göre grid yerleştirme
            except (KeyError, IndexError):  
                print("Hatalı buton:", button)
        
        self.root.mainloop()
    
    def func(self, button):  # Buton tiklandığında ne olacağını belirlemek için
        pass