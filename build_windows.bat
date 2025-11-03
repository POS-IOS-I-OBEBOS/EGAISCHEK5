@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

if "%PYTHON%"=="" set PYTHON=python

%PYTHON% -m pip install --upgrade pip >nul
if errorlevel 1 goto :error

%PYTHON% -m pip install -r requirements.txt >nul
if errorlevel 1 goto :error

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

%PYTHON% -m PyInstaller --name barcode-reader --onefile --console app\cli.py --paths app
if errorlevel 1 goto :error

echo.
echo Build complete. The executable is available at dist\barcode-reader.exe
exit /b 0

:error
echo.
echo Build failed.
exit /b 1
