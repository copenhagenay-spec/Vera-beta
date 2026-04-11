@echo off
setlocal
cd /d "%~dp0"

set PYTHON=
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python314\pythonw.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\pythonw.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\pythonw.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe"
    "%ProgramFiles%\Python314\pythonw.exe"
    "%ProgramFiles%\Python313\pythonw.exe"
    "%ProgramFiles%\Python312\pythonw.exe"
    "%ProgramFiles%\Python311\pythonw.exe"
) do (
    if exist %%P (
        set PYTHON=%%P
        goto :found
    )
)
where pythonw >nul 2>&1 && set PYTHON=pythonw && goto :found
where python  >nul 2>&1 && set PYTHON=python  && goto :found
echo ERROR: Python 3.11+ not found. Install from python.org.
pause
exit /b 1

:found
%PYTHON% assistant.py