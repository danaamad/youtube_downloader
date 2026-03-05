#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess, sys, os, threading, tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Install yt-dlp if needed
def install_yt_dlp():
    try:
        import yt_dlp
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("מוריד סרטוני YouTube")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Colors
        BG = "#1e1e2e"
        CARD = "#2a2a3e"
        ACC = "#e63946"
        TXT = "#ffffff"
        SUB = "#aaaacc"
        INP = "#33334a"

        # Title
        tk.Label(root, text="🎬 מוריד סרטוני YouTube", font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=TXT).pack(pady=(20, 5))
        tk.Label(root, text="הורד סרטונים בקלות", font=("Segoe UI", 10),
                 bg=BG, fg=SUB).pack(pady=(0, 15))

        # Card frame
        card = tk.Frame(root, bg=CARD, padx=20, pady=20)
        card.pack(padx=20, fill="x")

        # URL input
        tk.Label(card, text=":קישור לסרטון", font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TXT, anchor="e").pack(fill="x")
        self.url_var = tk.StringVar()
        url_entry = tk.Entry(card, textvariable=self.url_var, font=("Segoe UI", 11),
                             bg=INP, fg=TXT, insertbackground=TXT, relief="flat",
                             highlightthickness=1, highlightcolor=ACC)
        url_entry.pack(fill="x", ipady=6, pady=(4, 12))
        for seq in ("<Control-v>", "<Control-V>", "<Control-KeyPress-v>"):
            url_entry.bind(seq, lambda e: self.paste_url(url_entry, e))
        url_entry.bind("<Control-KeyPress>", lambda e: self.paste_url(url_entry, e) if e.keycode == 86 else None)
        url_entry.bind("<Button-3>", lambda e: self.right_click_paste(url_entry, e))

        # Quality
        tk.Label(card, text=":איכות", font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TXT, anchor="e").pack(fill="x")
        self.quality_var = tk.StringVar(value="best")
        quality_frame = tk.Frame(card, bg=CARD)
        quality_frame.pack(fill="x", pady=(4, 12))
        qualities = [("הכי טובה", "best"), ("1080p", "1080"), ("720p", "720"),
                     ("480p", "480"), ("360p", "360")]
        for label, val in qualities:
            rb = tk.Radiobutton(quality_frame, text=label, variable=self.quality_var,
                                value=val, bg=CARD, fg=TXT, selectcolor=INP,
                                activebackground=CARD, activeforeground=TXT,
                                font=("Segoe UI", 9))
            rb.pack(side="left", padx=5)

        # Output folder
        tk.Label(card, text=":תיקיית שמירה", font=("Segoe UI", 10, "bold"),
                 bg=CARD, fg=TXT, anchor="e").pack(fill="x")
        folder_frame = tk.Frame(card, bg=CARD)
        folder_frame.pack(fill="x", pady=(4, 0))
        self.folder_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        folder_entry = tk.Entry(folder_frame, textvariable=self.folder_var,
                                font=("Segoe UI", 10), bg=INP, fg=TXT,
                                insertbackground=TXT, relief="flat")
        folder_entry.pack(side="left", fill="x", expand=True, ipady=5)
        tk.Button(folder_frame, text="📁 בחר", bg=ACC, fg=TXT, relief="flat",
                  font=("Segoe UI", 9), command=self.choose_folder,
                  cursor="hand2", padx=8).pack(side="left", padx=(6, 0))

        # Buttons
        btn_frame = tk.Frame(root, bg=BG)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="⬇️  הורד סרטון", font=("Segoe UI", 12, "bold"),
                  bg=ACC, fg=TXT, relief="flat", padx=20, pady=8,
                  cursor="hand2", command=self.start_download).pack(side="left", padx=8)

        tk.Button(btn_frame, text="🎵  שמע בלבד (MP3)", font=("Segoe UI", 12),
                  bg="#6a4c93", fg=TXT, relief="flat", padx=20, pady=8,
                  cursor="hand2", command=self.start_audio).pack(side="left", padx=8)

        # Progress
        self.status_var = tk.StringVar(value="מוכן להורדה ✓")
        tk.Label(root, textvariable=self.status_var, font=("Segoe UI", 10),
                 bg=BG, fg=SUB).pack()

        self.progress = ttk.Progressbar(root, mode="indeterminate", length=560)
        self.progress.pack(pady=(5, 0), padx=20)

        # Log box
        log_frame = tk.Frame(root, bg=BG)
        log_frame.pack(padx=20, pady=10, fill="both", expand=True)
        self.log = tk.Text(log_frame, height=5, bg=CARD, fg="#88ff88",
                           font=("Consolas", 9), relief="flat", state="disabled")
        self.log.pack(fill="both", expand=True)

    def paste_url(self, entry, event=None):
        try:
            text = self.root.clipboard_get()
            entry.delete(0, "end")
            entry.insert(0, text)
        except:
            pass
        return "break"

    def right_click_paste(self, entry, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="הדבק", command=lambda: self.paste_url(entry))
        menu.add_command(label="נקה", command=lambda: entry.delete(0, "end"))
        menu.tk_popup(event.x_root, event.y_root)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def log_msg(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start_download(self):
        self._run(audio_only=False)

    def start_audio(self):
        self._run(audio_only=True)

    def _run(self, audio_only):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("שגיאה", "אנא הכנס קישור YouTube")
            return
        folder = self.folder_var.get().strip() or "downloads"
        quality = self.quality_var.get()
        threading.Thread(target=self._download,
                         args=(url, quality, folder, audio_only),
                         daemon=True).start()

    def _download(self, url, quality, output_dir, audio_only):
        import yt_dlp
        self.progress.start(10)
        self.status_var.set("...מוריד")
        os.makedirs(output_dir, exist_ok=True)
        output_template = os.path.join(output_dir, '%(title)s.%(ext)s')

        def progress_hook(d):
            if d['status'] == 'downloading':
                pct = d.get('_percent_str', '').strip()
                speed = d.get('_speed_str', '').strip()
                self.status_var.set(f"מוריד... {pct} | {speed}")
            elif d['status'] == 'finished':
                self.log_msg(f"✅ הסתיים: {os.path.basename(d['filename'])}")

        if audio_only:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'progress_hooks': [progress_hook],
                'postprocessors': [{'key': 'FFmpegExtractAudio',
                                    'preferredcodec': 'mp3', 'preferredquality': '192'}],
            }
        elif quality == 'best':
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'progress_hooks': [progress_hook],
            }
        else:
            ydl_opts = {
                'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best',
                'outtmpl': output_template,
                'progress_hooks': [progress_hook],
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_var.set(f"ההורדה הושלמה! ✅ נשמר ב: {output_dir}")
            self.log_msg(f"📁 נשמר בתיקייה: {output_dir}")
            messagebox.showinfo("הצלחה!", f"הסרטון הורד בהצלחה!\nנשמר ב:\n{output_dir}")
        except Exception as e:
            self.status_var.set("שגיאה בהורדה ❌")
            self.log_msg(f"❌ שגיאה: {e}")
            messagebox.showerror("שגיאה", str(e))
        finally:
            self.progress.stop()

if __name__ == '__main__':
    install_yt_dlp()
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
