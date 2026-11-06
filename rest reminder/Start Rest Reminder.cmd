@echo off
setlocal

if exist "%~dp0.venv\Scripts\python.exe" goto existing
where py >nul 2>nul
if not errorlevel 1 goto python_launcher
where python >nul 2>nul
if not errorlevel 1 goto python
echo Python 3 was not found. Install Python 3, then open this launcher again.
echo See the README in this folder.
pause
exit /b 1

:existing
"%~dp0.venv\Scripts\python.exe" -X utf8 -I "%~dp0launch.py" %*
goto finished

:python_launcher
py -3 -X utf8 -I "%~dp0launch.py" %*
goto finished

:python
python -X utf8 -I "%~dp0launch.py" %*

:finished
set "status=%errorlevel%"
if not "%status%"=="0" pause
exit /b %status%
