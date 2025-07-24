@echo off
REM Simple HOI4 Checklist Generator
REM Usage: generate_checklist.bat [optional_file.md]

cd /d "%~dp0..\.."

if "%~1"=="" (
    echo Generating checklists for all .md files...
    python ".github\scripts\generate_simple_checklist.py"
) else (
    echo Generating checklist for %~1...
    python ".github\scripts\generate_simple_checklist.py" "%~1"
)

if %ERRORLEVEL% NEQ 0 (
    echo Error occurred.
    pause
) else (
    echo Done!
)
