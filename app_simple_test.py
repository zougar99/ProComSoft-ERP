"""
Simple test version - نسخة اختبار بسيطة
"""
import tkinter as tk
from tkinter import ttk, messagebox

root = tk.Tk()
root.title("Email Marketing - Test")
root.geometry("1000x700")
root.configure(bg='white')  # White background for maximum visibility

# BIG TEST LABEL - Must see this!
test_label = tk.Label(root,
                      text="✅ APPLICATION IS WORKING!",
                      font=('Arial', 48, 'bold'),
                      bg='white',
                      fg='red',
                      pady=50)
test_label.pack()

# Second test
test_label2 = tk.Label(root,
                      text="If you see this, tkinter is working!",
                      font=('Arial', 24),
                      bg='white',
                      fg='blue',
                      pady=20)
test_label2.pack()

# Test button
def test_click():
    messagebox.showinfo("Test", "Button works!")

test_btn = tk.Button(root,
                    text="CLICK ME - TEST BUTTON",
                    font=('Arial', 20, 'bold'),
                    bg='green',
                    fg='white',
                    padx=30,
                    pady=20,
                    command=test_click)
test_btn.pack(pady=30)

# Notebook test
nb = ttk.Notebook(root)
nb.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Tab 1 - Simple
frame1 = tk.Frame(nb, bg='lightblue')
nb.add(frame1, text="Tab 1")
label1 = tk.Label(frame1, text="TAB 1 CONTENT", bg='lightblue', fg='black', font=('Arial', 30))
label1.pack(pady=100)

# Tab 2 - Simple
frame2 = tk.Frame(nb, bg='lightgreen')
nb.add(frame2, text="Tab 2")
label2 = tk.Label(frame2, text="TAB 2 CONTENT", bg='lightgreen', fg='black', font=('Arial', 30))
label2.pack(pady=100)

root.mainloop()

