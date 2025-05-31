import keyboard
import tkinter as tk
import threading
import pyperclip
import time
import pystray
from PIL import Image, ImageDraw
from tkinter import messagebox
import sys
import tempfile
import os
from tkinter import colorchooser
import json
import winreg
import webbrowser

CONFIG_FILE = "notifier_config.json"

default_config = {
    "notif_position": {"x": None, "y": None},
    "notif_colors": {"bg": "black", "fg": "white"},
    "opacity": 0.40
}

# This will be updated on load
app_config = default_config.copy()

# App State
is_listening = True
icon_ref = None

notif_opacity = 0.40  # default opacity

def load_config():
    global app_config
    try:
        with open(CONFIG_FILE, "r") as f:
            app_config.update(json.load(f))
    except FileNotFoundError:
        save_config()  # Create default if not exists


def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(app_config, f, indent=4)



APP_NAME = "Hotkey Notifier"
STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

def get_script_path():
    # Return full path to the script or executable
    return os.path.abspath(sys.argv[0])

def is_startup_enabled():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return value == get_script_path()
    except FileNotFoundError:
        return False

def enable_startup():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, get_script_path())

def disable_startup():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_WRITE) as key:
            winreg.DeleteValue(key, APP_NAME)
    except FileNotFoundError:
        pass



def show_custom_notification(title, message, duration=2):
    def popup():
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", app_config["opacity"])

        width, height = 200, 100
        screen_width = root.winfo_screenwidth()

        # Use saved position if available
        notif_position = app_config["notif_position"]
        x = notif_position["x"] if notif_position["x"] is not None else (screen_width // 2 - width // 2)
        y = notif_position["y"] if notif_position["y"] is not None else 50
        root.geometry(f"{width}x{height}+{x}+{y}")

        notif_colors = app_config["notif_colors"]
        frame = tk.Frame(root, bg=notif_colors["bg"])
        frame.pack(fill="both", expand=True)

        root._dragging = False

        def start_move(event):
            root._drag_start_x = event.x
            root._drag_start_y = event.y
            root._dragging = True
            # Cancel any scheduled close while dragging
            root.after_cancel(getattr(root, "_close_id", None))

        def do_move(event):
            dx = event.x - root._drag_start_x
            dy = event.y - root._drag_start_y
            new_x = root.winfo_x() + dx
            new_y = root.winfo_y() + dy
            root.geometry(f"+{new_x}+{new_y}")
            app_config["notif_position"]["x"] = new_x
            app_config["notif_position"]["y"] = new_y
            save_config()

        def end_move(event):
            root._dragging = False
            schedule_close()

        def bind_drag(widget):
            widget.bind("<Button-1>", start_move)
            widget.bind("<B1-Motion>", do_move)
            widget.bind("<ButtonRelease-1>", end_move)

        bind_drag(frame)

        # Create labels
        title_label = tk.Label(
            frame, text=title, font=("Helvetica", 10, "bold"),
            fg=notif_colors["fg"], bg=notif_colors["bg"])
        title_label.pack(pady=(5, 0))
        bind_drag(title_label)

        message_label = tk.Label(
            frame, text=message, font=("Helvetica", 8),
            fg=notif_colors["fg"], bg=notif_colors["bg"],
            width=180, wraplength=170, justify="left")
        message_label.pack()
        bind_drag(message_label)

        def schedule_close():
            root._close_id = root.after(duration * 1000, root.destroy)

        schedule_close()
        root.mainloop()

    threading.Thread(target=popup).start()

def reset_notification_position():
    app_config["notif_position"]["x"] = None
    app_config["notif_position"]["y"] = None
    save_config()
    show_custom_notification("Position Reset", "Notification position reset to default.")

def get_clipboard_preview():
    try:
        text = pyperclip.paste()
        if text.strip():
            preview = text.strip().replace("\n", " ")
            if len(preview) > 80:
                preview = preview[:77] + "..."
            return preview
        else:
            return "[Non-text content or empty]"
    except Exception as e:
        return f"[Clipboard error: {str(e)}]"

def handle_hotkey(action_name, key_combo, show_clipboard=False):
    def handler():
        temp_action_name = action_name
        message = ""
        if not is_listening:
            return
        temp_action_name = action_name + "\n" + key_combo
        if show_clipboard:
            time.sleep(0.2)
            message = get_clipboard_preview()
        show_custom_notification(f"{temp_action_name}", message)
    return handler

def register_hotkeys():
    for combo, info in hotkeys.items():
        keyboard.add_hotkey(combo, handle_hotkey(info['name'], combo, info['show_clipboard']), suppress=False)

def create_image():
    try:
        return Image.open("app_icon.ico")  # your icon filename here
    except Exception as e:
        print(f"Failed to load icon: {e}")
        # fallback to simple icon:
        image = Image.new('RGB', (64, 64), "black")
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")
        return image

def get_icon_path():
    image = create_image()
    temp_dir = tempfile.gettempdir()
    icon_path = os.path.join(temp_dir, "temp_app_icon.ico")
    image.save(icon_path, format='ICO')
    return icon_path

def toggle_listening(icon, item):
    global is_listening
    is_listening = not is_listening
    icon.update_menu()

def show_status():
    show_custom_notification("Hotkey Tracker", "Running in background...")

def quit_app(icon, item):
    icon.stop()

def quit_full_app(home_window):
    if icon_ref:
        icon_ref.stop()  # stop system tray icon
    home_window.destroy()
    sys.exit(0)

def show_help_page():
    help_text = (
        "✨  𝗛𝗼𝘁𝗸𝗲𝘆 𝗡𝗼𝘁𝗶𝗳𝗶𝗲𝗿 𝗛𝗲𝗹𝗽 𝗚𝘂𝗶𝗱𝗲  ✨\n"
        "────────────────────────────────────────────\n"
        "\n"
        "🛠️  𝗪𝗵𝗮𝘁 𝗶𝘁 𝗱𝗼𝗲𝘀:\n"
        "  Displays beautiful popup notifications when you use common keyboard shortcuts.\n"
        "\n"
        "🎯  𝗗𝗲𝗳𝗮𝘂𝗹𝘁 𝗛𝗼𝘁𝗸𝗲𝘆𝘀:\n"
        "  •  Ctrl + C   →   Copy   (shows copied text)\n"
        "  •  Ctrl + X   →   Cut    (shows cut text)\n"
        "  •  Ctrl + V   →   Paste\n"
        "  •  Ctrl + Z   →   Undo\n"
        "  •  Ctrl + Y   →   Redo\n"
        "  •  Ctrl + A   →   Select All\n"
        "  •  Ctrl + S   →   Save\n"
        "  •  Ctrl + P   →   Print\n"
        "  •  Ctrl + N   →   New Document\n"
        "  •  Ctrl + O   →   Open File\n"
        "  •  Ctrl + F   →   Find\n"
        "\n"
        "🎨  𝗖𝘂𝘀𝘁𝗼𝗺𝗶𝘇𝗮𝘁𝗶𝗼𝗻:\n"
        "  • Drag the notification popup to reposition it anywhere on your screen.\n"
        "  • Use 'Reset Notification Position' in the Home menu to restore default.\n"
        "  • Adjust popup transparency with the Opacity slider.\n"
        "  • Pick your favorite background and text colors.\n"
        "  • Enable or disable it to start on Windows start up.\n"
        "  • All settings are saved automatically and persist across restarts.\n"
        "\n"
        "🧲  𝗦𝘆𝘀𝘁𝗲𝗺 𝗧𝗿𝗮𝘆 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:\n"
        "  • Right-click the tray icon for: Pause/Resume, Status, Home, or Quit.\n"
        "  • The app runs quietly in the background—no need to keep the Home window open.\n"
        "\n"
        "❓  𝗛𝗮𝘃𝗲 𝗶𝘀𝘀𝘂𝗲𝘀 𝗼𝗿 𝘀𝘂𝗴𝗴𝗲𝘀𝘁𝗶𝗼𝗻𝘀?\n"
        "  • See the About section for GitHub and contact info.\n"
        "\n"
        "────────────────────────────────────────────"
    )
    messagebox.showinfo("✨ Hotkey Notifier Help", help_text)

def show_about_info():
    about_text = (
        "✨ Hotkey Notifier v1.1\n"
        "─────────────────────────────\n"
        "👨‍💻 Developed by Jamal Uddin Tanvin\n"
        "📬 Email: jamaluddintanvin@hotmail.com\n"
        "🌐 GitHub: https://github.com/tanvin420\n\n"
        "📝 A simple, elegant tool to display notifications for common keyboard shortcuts.\n"
        "🎨 Customize popup position, colors, and opacity.\n\n"
        "💡 Open source. Contributions welcome!\n"
        "© 2025 Jamal Uddin Tanvin"
    )
    messagebox.showinfo("About", about_text)
    
def show_home_menu():
    home = tk.Tk()
    home.title("Hotkey Notifier")
    home.geometry("340x500")
    home.attributes("-topmost", True)
    home.resizable(False, False)

    # Set icon
    icon_path = get_icon_path()
    home.iconbitmap(icon_path)

    # Colors and styles
    main_bg = "#23272e"
    accent = "#4f8cff"
    btn_bg = "#31363f"
    btn_fg = "#ffffff"
    label_fg = "#e0e0e0"
    home.configure(bg=main_bg)

    # Title
    title = tk.Label(
        home, text="Hotkey Notifier", font=("Segoe UI", 18, "bold"),
        bg=main_bg, fg=accent
    )
    title.pack(pady=(18, 8))

    # Status
    status_text = tk.StringVar()
    status_text.set("▶ Listening" if is_listening else "⏸ Paused")
    status_label = tk.Label(
        home, textvariable=status_text, font=("Segoe UI", 12, "bold"),
        bg=main_bg, fg=label_fg
    )
    status_label.pack(pady=(0, 8))

    # Pause/Resume Button
    def toggle():
        global is_listening
        is_listening = not is_listening
        status_text.set("▶ Listening" if is_listening else "⏸ Paused")

    pause_btn = tk.Button(
        home, text="Pause/Resume", command=toggle,
        bg=btn_bg, fg=btn_fg, font=("Segoe UI", 11, "bold"),
        activebackground=accent, activeforeground="#fff", bd=0, relief="flat", cursor="hand2"
    )
    pause_btn.pack(pady=4, ipadx=10, ipady=3)

    # Reset Position Button
    reset_btn = tk.Button(
        home, text="Reset Notification Position", command=reset_notification_position,
        bg=btn_bg, fg=btn_fg, font=("Segoe UI", 10),
        activebackground=accent, activeforeground="#fff", bd=0, relief="flat", cursor="hand2"
    )
    reset_btn.pack(pady=4, ipadx=6, ipady=2)

    # Opacity
    tk.Label(
        home, text="Notification Opacity", font=("Segoe UI", 11, "bold"),
        bg=main_bg, fg=label_fg
    ).pack(pady=(18, 2))

    def on_opacity_change(val):
        app_config["opacity"] = float(val)
        save_config()

    opacity_slider = tk.Scale(
        home, from_=0.1, to=1.0, resolution=0.05, orient="horizontal",
        bg=main_bg, fg=accent, troughcolor=btn_bg, highlightthickness=0,
        font=("Segoe UI", 10), length=180
    )
    opacity_slider.set(app_config["opacity"])
    opacity_slider.config(command=on_opacity_change)
    opacity_slider.pack(pady=(0, 10))

    # Color pickers
    tk.Label(
        home, text="Notification Colors", font=("Segoe UI", 12, "bold"),
        bg=main_bg, fg=label_fg
    ).pack(pady=(10, 2))

    def pick_bg_color():
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            app_config["notif_colors"]["bg"] = color
            save_config()
            bg_btn.config(bg=app_config["notif_colors"]["bg"])

    def pick_fg_color():
        color = colorchooser.askcolor(title="Choose Text Color")[1]
        if color:
            app_config["notif_colors"]["fg"] = color
            save_config()
            fg_btn.config(bg=app_config["notif_colors"]["fg"])

    def reset_colors():
        app_config["notif_colors"]["bg"] = default_config["notif_colors"]["bg"]
        app_config["notif_colors"]["fg"] = default_config["notif_colors"]["fg"]
        save_config()
        bg_btn.config(bg=app_config["notif_colors"]["bg"])
        fg_btn.config(bg=app_config["notif_colors"]["fg"])

    color_frame = tk.Frame(home, bg=main_bg)
    color_frame.pack(pady=2)

    bg_btn = tk.Button(
        color_frame, text="Background", command=pick_bg_color,
        bg=app_config["notif_colors"]["bg"], fg=btn_fg, font=("Segoe UI", 10, "bold"),
        activebackground=accent, activeforeground="#fff", bd=0, relief="flat", cursor="hand2", width=12
    )
    bg_btn.grid(row=0, column=0, padx=6, pady=2)

    fg_btn = tk.Button(
        color_frame, text="Text", command=pick_fg_color,
        bg=app_config["notif_colors"]["fg"], fg=btn_bg, font=("Segoe UI", 10, "bold"),
        activebackground=accent, activeforeground="#fff", bd=0, relief="flat", cursor="hand2", width=12
    )
    fg_btn.grid(row=0, column=1, padx=6, pady=2)

    reset_colors_btn = tk.Button(
        color_frame, text="Reset Colors", command=reset_colors,
        bg=btn_bg, fg=accent, font=("Segoe UI", 10, "bold"),
        activebackground=accent, activeforeground="#fff", bd=0, relief="flat", cursor="hand2", width=12
    )
    reset_colors_btn.grid(row=0, column=2, padx=6, pady=2)

    # Startup toggle frame
    startup_frame = tk.Frame(home, bg=main_bg)
    startup_frame.pack(pady=(10, 0))

    startup_var = tk.BooleanVar(value=is_startup_enabled())

    def toggle_startup():
        if startup_var.get():
            enable_startup()
        else:
            disable_startup()

    startup_checkbox = tk.Checkbutton(
        startup_frame,
        text="Start on Windows startup",
        variable=startup_var,
        onvalue=True,
        offvalue=False,
        command=toggle_startup,
        bg=main_bg,
        fg=label_fg,
        activebackground=main_bg,
        activeforeground=label_fg,
        font=("Segoe UI", 10),
        selectcolor=accent
    )
    startup_checkbox.pack()

    # Separator
    sep = tk.Frame(home, bg=accent, height=2)
    sep.pack(fill="x", pady=(18, 10), padx=18)

    # Bottom buttons
    btn_frame = tk.Frame(home, bg=main_bg)
    btn_frame.pack(pady=2)

    help_btn = tk.Button(
        btn_frame, text="Help", command=show_help_page,
        bg=btn_bg, fg=btn_fg, font=("Segoe UI", 10),
        activebackground=accent, activeforeground="#fff", bd=0, relief="flat", cursor="hand2", width=10
    )
    help_btn.grid(row=0, column=0, padx=4, pady=2)

    about_btn = tk.Button(
        btn_frame, text="About", command=show_about_info,
        bg=btn_bg, fg=btn_fg, font=("Segoe UI", 10),
        activebackground=accent, activeforeground="#fff", bd=0, relief="flat", cursor="hand2", width=10
    )
    about_btn.grid(row=0, column=1, padx=4, pady=2)

    quit_btn = tk.Button(
        btn_frame, text="Quit", command=lambda: quit_full_app(home),
        bg="#e74c3c", fg="#fff", font=("Segoe UI", 10, "bold"),
        activebackground="#c0392b", activeforeground="#fff", bd=0, relief="flat", cursor="hand2", width=10
    )
    quit_btn.grid(row=0, column=2, padx=4, pady=2)

    # Add clickable link after Quit button
    def open_github():
        try:
            webbrowser.open("https://github.com/tanvin420")
        except Exception as e:
            pass

    # Add separator above the GitHub link
    sep.pack(fill="x", pady=(18, 10), padx=18)

    link = tk.Label(
        home, text="GitHub: Tanvin420", fg=accent, bg=main_bg, cursor="hand2",
        font=("Segoe UI", 9, "underline")
    )
    link.pack(pady=(12, 0))  # Increase vertical padding

    def on_hover(event):
        link.config(font=("Segoe UI", 9, "underline"), fg="#4f8cff")

    def on_leave(event):
        link.config(font=("Segoe UI", 9), fg=accent)

    link.bind("<Button-1>", lambda e: open_github())
    link.bind("<Enter>", on_hover)
    link.bind("<Leave>", on_leave)
  

    home.mainloop()


def tray_icon():
    global icon_ref
    icon_image = create_image()
    icon_ref = pystray.Icon("HotkeyNotify", icon_image, "Hotkey Notifier")

    icon_ref.menu = pystray.Menu(
        pystray.MenuItem("Option", lambda: threading.Thread(target=show_home_menu).start()),
        pystray.MenuItem("Show Status", lambda: show_status()),
        pystray.MenuItem("Reset Notification Position", lambda: reset_notification_position()),
        pystray.MenuItem(
            lambda item: "⏸ Pause" if is_listening else "▶ Resume",
            toggle_listening
        ),
        pystray.MenuItem("Help", show_help_page),
        pystray.MenuItem("About", show_about_info),
        pystray.MenuItem("Quit", quit_app)
    )

    icon_ref.run()

def main():
    load_config()
    register_hotkeys()
    threading.Thread(target=tray_icon).start()

hotkeys = {
    'ctrl+c': {'name': 'Copy', 'show_clipboard': True},
    'ctrl+v': {'name': 'Paste', 'show_clipboard': False},
    'ctrl+x': {'name': 'Cut', 'show_clipboard': True},
    'ctrl+z': {'name': 'Undo', 'show_clipboard': False},
    'ctrl+y': {'name': 'Redo', 'show_clipboard': False},
    'ctrl+a': {'name': 'Select All', 'show_clipboard': False},
    'ctrl+s': {'name': 'Save', 'show_clipboard': False},
    'ctrl+p': {'name': 'Print', 'show_clipboard': False},
    'ctrl+n': {'name': 'New Document', 'show_clipboard': False},
    'ctrl+o': {'name': 'Open File', 'show_clipboard': False},
    'ctrl+f': {'name': 'Find', 'show_clipboard': False},
}

if __name__ == "__main__":
    main()