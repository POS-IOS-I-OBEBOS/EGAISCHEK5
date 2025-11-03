@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "LOG_FILE=%SCRIPT_DIR%build_windows.log"
if exist "%LOG_FILE%" del "%LOG_FILE%"

call :log "Starting Windows build script"

if "%PYTHON%"=="" set "PYTHON=python"
call :log "Using Python interpreter: %PYTHON%"

call :log "Upgrading pip"
%PYTHON% -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
if errorlevel 1 goto :error

call :log "Installing project requirements"
%PYTHON% -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
if errorlevel 1 goto :error

call :log "Cleaning previous build artefacts"
if exist build (
    call :log "Removing build directory"
    rmdir /s /q build >> "%LOG_FILE%" 2>&1
)
if exist dist (
    call :log "Removing dist directory"
    rmdir /s /q dist >> "%LOG_FILE%" 2>&1
)

call :log "Running PyInstaller"
%PYTHON% -m PyInstaller --name barcode-reader --onefile --console app\cli.py --paths app >> "%LOG_FILE%" 2>&1
if errorlevel 1 goto :error

call :log "Build complete. The executable is available at dist\barcode-reader.exe"
exit /b 0

:error
call :log "Build failed. See %LOG_FILE% for details"
exit /b 1

:log
set "MESSAGE=%~1"
echo %MESSAGE%
>> "%LOG_FILE%" echo [%DATE% %TIME%] %MESSAGE%
exit /b 0
