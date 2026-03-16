import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

BG_MAIN = "#0f172a"
BG_CARD = "#020617"
FG_TEXT = "white"
ACCENT = "#2563eb"

db = sqlite3.connect("muhasebe.db")
cur = db.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS taxes (id INTEGER PRIMARY KEY AUTOINCREMENT, note TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, note TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, note TEXT)")
db.commit()

def open_app():
    root = tk.Tk()
    root.title("Muhasebeci Masaüstü Asistanı")
    root.geometry("1100x650")
    root.configure(bg=BG_MAIN)

    root.option_add("*Background", BG_MAIN)
    root.option_add("*Foreground", FG_TEXT)

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=BG_MAIN)
    style.configure("TLabel", background=BG_MAIN, foreground=FG_TEXT)
    style.configure("TButton", background=ACCENT, foreground="white", padding=8)
    style.map("TButton", background=[("active", "#1d4ed8")])
    style.configure("TNotebook.Tab", background=BG_CARD, foreground=FG_TEXT)
    style.map("TNotebook.Tab", background=[("selected", ACCENT)])

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tab_customer = ttk.Frame(notebook, padding=20)
    tab_tax = ttk.Frame(notebook, padding=20)
    tab_docs = ttk.Frame(notebook, padding=20)
    tab_tasks = ttk.Frame(notebook, padding=20)
    tab_calc = ttk.Frame(notebook, padding=20)

    notebook.add(tab_customer, text="Müşteriler")
    notebook.add(tab_tax, text="Vergi Takibi")
    notebook.add(tab_docs, text="Belge Takibi")
    notebook.add(tab_tasks, text="Günlük İşler")
    notebook.add(tab_calc, text="Hesap Kitap")

    def simple_tab(tab, table):
        entry = tk.StringVar()
        ttk.Entry(tab, textvariable=entry, width=40).pack(anchor="w")
        listbox = tk.Listbox(tab, bg=BG_CARD, fg=FG_TEXT, height=15)
        listbox.pack(fill="both", expand=True, pady=10)

        def load():
            listbox.delete(0, tk.END)
            for r in cur.execute(f"SELECT note FROM {table}"):
                listbox.insert(tk.END, r[0])

        def add():
            if entry.get().strip():
                cur.execute(f"INSERT INTO {table} (note) VALUES (?)", (entry.get(),))
                db.commit()
                entry.set("")
                load()

        ttk.Button(tab, text="Ekle", command=add).pack(anchor="e")
        load()

    simple_tab(tab_tax, "taxes")
    simple_tab(tab_docs, "documents")
    simple_tab(tab_tasks, "tasks")

    ttk.Label(tab_customer, text="Müşteri Adı").pack(anchor="w")
    cust = tk.StringVar()
    ttk.Entry(tab_customer, textvariable=cust, width=30).pack(anchor="w")
    cust_list = tk.Listbox(tab_customer, bg=BG_CARD, fg=FG_TEXT, height=15)
    cust_list.pack(fill="both", expand=True, pady=10)

    def load_cust():
        cust_list.delete(0, tk.END)
        for r in cur.execute("SELECT name FROM customers"):
            cust_list.insert(tk.END, r[0])

    def add_cust():
        if cust.get().strip():
            cur.execute("INSERT INTO customers (name) VALUES (?)", (cust.get(),))
            db.commit()
            cust.set("")
            load_cust()

    ttk.Button(tab_customer, text="Müşteri Ekle", command=add_cust).pack(anchor="e")
    load_cust()

    ttk.Label(tab_calc, text="Tutar (TL)").pack(anchor="w")
    amount = tk.StringVar()
    ttk.Entry(tab_calc, textvariable=amount, width=30).pack(anchor="w")

    ttk.Label(tab_calc, text="Oran (%)").pack(anchor="w")
    rate = tk.StringVar()
    ttk.Entry(tab_calc, textvariable=rate, width=30).pack(anchor="w")

    ttk.Label(tab_calc, text="Maliyet (TL)").pack(anchor="w")
    cost = tk.StringVar()
    ttk.Entry(tab_calc, textvariable=cost, width=30).pack(anchor="w")

    result = tk.StringVar()
    ttk.Label(tab_calc, textvariable=result, font=("Arial", 12)).pack(pady=15)

    def kdv_ekle():
        a = float(amount.get())
        r = float(rate.get()) / 100
        result.set(f"KDV: {a*r:.2f} TL\nToplam: {a*(1+r):.2f} TL")

    def kdv_cikar():
        t = float(amount.get())
        r = float(rate.get()) / 100
        net = t / (1+r)
        result.set(f"Net: {net:.2f} TL\nKDV: {t-net:.2f} TL")

    def yuzde_hesapla():
        a = float(amount.get())
        r = float(rate.get()) / 100
        result.set(f"%{rate.get()} = {a*r:.2f} TL")

    def indirim():
        a = float(amount.get())
        r = float(rate.get()) / 100
        result.set(f"İndirimli Tutar: {a-(a*r):.2f} TL")

    def kar_zarar():
        s = float(amount.get())
        m = float(cost.get())
        fark = s - m
        durum = "Kar" if fark >= 0 else "Zarar"
        result.set(f"{durum}: {fark:.2f} TL")

    for text, cmd in [
        ("KDV Ekle", kdv_ekle),
        ("KDV Çıkar", kdv_cikar),
        ("% Hesapla", yuzde_hesapla),
        ("İndirim", indirim),
        ("Kar / Zarar", kar_zarar)
    ]:
        ttk.Button(tab_calc, text=text, command=cmd).pack(fill="x", pady=3)

    root.mainloop()

def login():
    if user.get() == "admin" and pwd.get() == "1234":
        login_win.destroy()
        open_app()
    else:
        messagebox.showerror("Hata", "Hatalı giriş")

login_win = tk.Tk()
login_win.title("Giriş")
login_win.geometry("400x300")
login_win.configure(bg=BG_MAIN)

tk.Label(login_win, text="Kullanıcı Adı", fg=FG_TEXT, bg=BG_MAIN).pack(pady=10)
user = tk.StringVar()
tk.Entry(login_win, textvariable=user, bg=BG_CARD, fg=FG_TEXT, insertbackground="white").pack()

tk.Label(login_win, text="Şifre", fg=FG_TEXT, bg=BG_MAIN).pack(pady=10)
pwd = tk.StringVar()
tk.Entry(login_win, textvariable=pwd, show="*", bg=BG_CARD, fg=FG_TEXT, insertbackground="white").pack()

tk.Button(login_win, text="Giriş Yap", bg=ACCENT, fg="white", command=login).pack(pady=20)

login_win.mainloop()
