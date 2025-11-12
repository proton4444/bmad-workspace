@echo off
REM BMAD Workspace Repository Check Script
REM Launches the PowerShell version for better Windows compatibility

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0check-repo.ps1"
pause
