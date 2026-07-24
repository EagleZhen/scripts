@echo off

:: %~1 is the first parameter, which is the file path of the dragged file
if "%~1"=="" (
    echo Please drag and drop a .pbf file onto this script.
    pause
    exit /b
)

set "filename=%~1"

python "%~dp0convert potplayer bookmark file to youtube timestamps.py" "%filename%"