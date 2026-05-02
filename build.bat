@echo off
echo ================================
echo  Rummage - Windows Build Script
echo ================================
echo.

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Locating customtkinter...
for /f "delims=" %%i in ('python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))"') do set CTK_PATH=%%i

echo Found customtkinter at: %CTK_PATH%
echo.

echo Building executable...
pyinstaller --onefile --windowed --name Rummage --add-data "%CTK_PATH%;customtkinter" src/gui.py
if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo.
echo ================================
echo  Build complete!
echo  Rummage.exe is in dist/
echo ================================
pause