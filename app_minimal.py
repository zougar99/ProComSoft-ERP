"""
Minimal version - بدون Notebook
"""
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("Email Marketing - MINIMAL TEST")
root.geometry("1200x800")
root.configure(bg='white')

# BIG TITLE
title = tk.Label(root,
                text="📧 EMAIL MARKETING PRO",
                font=('Arial', 60, 'bold'),
                bg='white',
                fg='red',
                pady=50)
title.pack()

# Subtitle
subtitle = tk.Label(root,
                   text="Application is Working!",
                   font=('Arial', 40, 'bold'),
                   bg='white',
                   fg='blue',
                   pady=30)
subtitle.pack()

# Test button
def test():
    messagebox.showinfo("Test", "Button works!")

btn = tk.Button(root,
               text="CLICK ME - TEST",
               font=('Arial', 30, 'bold'),
               bg='green',
               fg='white',
               padx=50,
               pady=30,
               command=test)
btn.pack(pady=50)

# Status
status = tk.Label(root,
                 text="If you see this, everything is working!",
                 font=('Arial', 24),
                 bg='white',
                 fg='green',
                 pady=20)
status.pack()

root.mainloop()

