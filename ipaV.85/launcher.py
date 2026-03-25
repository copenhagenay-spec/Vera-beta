"""VERA launcher — finds pythonw.exe and runs assistant.py with no console window."""
import os
import sys
import subprocess

base = os.path.dirname(os.path.abspath(__file__))
pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(pythonw):
    pythonw = sys.executable
assistant = os.path.join(base, "assistant.py")
subprocess.Popen([pythonw, assistant], cwd=base)
