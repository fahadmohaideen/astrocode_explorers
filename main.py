import tkinter as tk
from tkinter import messagebox
import json
import os
import subprocess

USER_DB = "users.json"

if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({}, f)

def register():
    username = entry_user.get()
    password = entry_pass.get()
    with open(USER_DB, "r") as f:
        users = json.load(f)

    if username in users:
        messagebox.showerror("Error", "Username already exists.")
    else:
        users[username] = password
        with open(USER_DB, "w") as f:
            json.dump(users, f)
        messagebox.showinfo("Success", "Account created!")

def login():
    username = entry_user.get()
    password = entry_pass.get()
    with open(USER_DB, "r") as f:
        users = json.load(f)

    if users.get(username) == password:
        messagebox.showinfo("Login Success", f"Welcome {username}!")
        root.destroy()
        subprocess.run(["python", "game.py"])
    else:
        messagebox.showerror("Error", "Invalid username or password.")

root = tk.Tk()
root.title("AstroCode Explorers - Login")

tk.Label(root, text="Username").grid(row=0, column=0, padx=10, pady=5)
entry_user = tk.Entry(root)
entry_user.grid(row=0, column=1)

tk.Label(root, text="Password").grid(row=1, column=0, padx=10, pady=5)
entry_pass = tk.Entry(root, show="*")
entry_pass.grid(row=1, column=1)

tk.Button(root, text="Login", command=login).grid(row=2, column=0, pady=10)
tk.Button(root, text="Register", command=register).grid(row=2, column=1)

root.mainloop()





