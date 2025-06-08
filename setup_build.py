from cx_Freeze import setup, Executable

# Build options
build_exe_options = {
    "packages": ["tkinter", "pystray", "keyboard", "pyperclip", "os", "sys", "time", "threading", "PIL", "tempfile", "json", "winreg", "webbrowser"],
    "include_files": ["notifier_config.json", "app_icon.ico", "LICENSE"]
}

bdist_msi_options = {
    "upgrade_code": "{a1f1e6f2-6c52-451b-b70d-0705d42ae234}",  
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\HotkeyNotifier"
}

setup(
    name="Hotkey Notifier",
    version="1.2",
    description="Custom popup notifier for hotkeys",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[Executable("hot_key.py", base="Win32GUI", icon="app_icon.ico")]
)
