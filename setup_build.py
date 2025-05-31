from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": ["tkinter", "pystray", "keyboard", "pyperclip", "os", "sys","time","threading","PIL","tempfile","json","winreg","webbrowser"],
    "include_files": ["app_icon.ico","LICENSE"]
}

setup(
    name="Hotkey Notifier",
    version="1.1",
    description="Custom popup notifier for hotkeys",
    options={"build_exe": build_exe_options},
    executables=[Executable("hot_key.py", base="Win32GUI", icon="app_icon.ico")]
)
