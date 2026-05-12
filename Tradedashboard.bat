@echo off
setlocal
pushd "%~dp0"

if not exist venv\Scripts\activate.bat (
    echo ERROR: venv not found in "%~dp0\venv\Scripts"
    pause
    popd
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate venv
    pause
    popd
    exit /b 1
)

echo Starting Flask app...
start "" "%~dp0venv\Scripts\python.exe" app.py
if errorlevel 1 (
    echo ERROR: Failed to start app.py
    pause
    popd
    exit /b 1
)

echo Flask app started.
popd
endlocal
