@echo off
setlocal enabledelayedexpansion

REM ---------------------------------------------------------------------------
REM build_windows.bat — Build the Urban's Cannon Windows executable
REM
REM Usage:
REM   build_windows.bat
REM
REM Output:
REM   dist\Urban's Cannon\Urban's Cannon.exe
REM ---------------------------------------------------------------------------

set "APP_NAME=Urban's Cannon"
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ============================================
echo  Building: %APP_NAME% (Windows)
echo ============================================
echo.

REM --- 1. Create / activate virtual environment ---
if not exist ".venv" (
    echo [1/5] Creating Python virtual environment...
    python -m venv .venv
) else (
    echo [1/5] Virtual environment already exists.
)

echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat

REM --- 2. Install dependencies ---
echo [3/5] Installing dependencies...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

REM --- 3. Generate Windows icon ---
echo [4/5] Generating Windows icon...
python resources\generate_icon_win.py

REM --- 4. Build with PyInstaller ---
echo [5/5] Building with PyInstaller...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
pyinstaller "Urban's Cannon (Windows).spec" --noconfirm --clean

echo.
echo ============================================
echo  Build Complete
echo ============================================
echo.
echo  Output: %SCRIPT_DIR%dist\%APP_NAME%\
echo.
echo  To create an installer, install Inno Setup 6 and run:
echo    iscc installer.iss
echo.
endlocal
