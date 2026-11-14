
import os
import shutil
import subprocess
import webbrowser
from pathlib import Path


# Only predefined websites are allowed.
WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "wikipedia": "https://www.wikipedia.org",
}


# Only predefined applications are allowed.
APPS = {
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"],
    "file explorer": ["explorer.exe"],
}


# Only predefined folders are allowed.
FOLDERS = {
    "downloads": Path.home() / "Downloads",
    "documents": Path.home() / "Documents",
    "pictures": Path.home() / "Pictures",
    "desktop": Path.home() / "Desktop",
}


def open_chrome():
    """Open Chrome only if its executable can be found."""

    chrome = shutil.which("chrome")

    possible_paths = [
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files"))
        / "Google/Chrome/Application/chrome.exe",

        Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)"))
        / "Google/Chrome/Application/chrome.exe",

        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Google/Chrome/Application/chrome.exe",
    ]

    if chrome:
        subprocess.Popen([chrome])
        return "Chrome open kar raha hoon."

    for path in possible_paths:
        if path.is_file():
            subprocess.Popen([str(path)])
            return "Chrome open kar raha hoon."

    return (
        "Chrome install nahi mila. "
        "Default browser open karne ke liye bolo open browser."
    )


def execute_device_command(command):
    """
    Executes only predefined device actions.
    Returns None if the command is not supported.
    """

    command = command.strip().lower()

    if not command.startswith("open "):
        return None

    target = command[5:].strip()

    # OPEN PREDEFINED WEBSITES
    if target in WEBSITES:
        webbrowser.open(WEBSITES[target])
        return f"{target} open kar raha hoon."

    # OPEN DEFAULT BROWSER
    if target == "browser":
        webbrowser.open("https://www.google.com")
        return "Default browser open kar raha hoon."

    # OPEN CHROME
    if target == "chrome":
        return open_chrome()

    # OPEN PREDEFINED APPLICATIONS
    if target in APPS:
        try:
            subprocess.Popen(APPS[target])
            return f"{target} open kar raha hoon."

        except OSError as error:
            print("App opening error:", error)
            return f"{target} open nahi ho paya."

    # OPEN PREDEFINED FOLDERS
    if target in FOLDERS:
        folder = FOLDERS[target]

        if folder.is_dir():
            try:
                os.startfile(str(folder))
                return f"{target} folder open kar raha hoon."

            except OSError as error:
                print("Folder opening error:", error)
                return f"{target} folder open nahi ho paya."

        return f"{target} folder nahi mila."

    return None
