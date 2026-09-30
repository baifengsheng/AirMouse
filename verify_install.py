import importlib
import platform
import py_compile
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

REQUIRED_MODULES = [
    "flask",
    "flask_socketio",
    "OpenSSL",
    "psutil",
    "pyautogui",
    "pynput",
]

if platform.system() == "Windows":
    REQUIRED_MODULES.extend(["comtypes", "uiautomation"])
else:
    REQUIRED_MODULES.append("inputs")

REQUIRED_FILES = [
    "cert.pem",
    "key.pem",
    "server.py",
    "ime_candidate_service.py",
    "templates/keyboard.html",
    "static/js/t9-pinyin.js",
]

PYTHON_FILES = [
    "server.py",
    "web_app.py",
    "mouse_service.py",
    "keyboard_service.py",
    "gamepad_service.py",
    "config_manager.py",
    "ime_candidate_service.py",
]


def main():
    errors = []

    if sys.version_info < (3, 11):
        errors.append(
            f"Python 3.11 or newer is required; found {platform.python_version()}."
        )

    for module_name in REQUIRED_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            errors.append(f"Cannot import {module_name}: {exc}")

    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            errors.append(f"Required file is missing: {relative_path}")

    for relative_path in PYTHON_FILES:
        try:
            py_compile.compile(
                str(ROOT / relative_path),
                doraise=True,
            )
        except Exception as exc:
            errors.append(f"Cannot compile {relative_path}: {exc}")

    if errors:
        print("AirMouse installation verification failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "AirMouse installation verified: "
        f"Python {platform.python_version()} on {platform.system()}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
