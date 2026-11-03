@echo off
setlocal EnableExtensions

cd /d "%~dp0\..\.."
set "ROOT_DIR=%CD%"
for %%I in ("%~dp0..") do set "SKILL_NAME=%%~nxI"

echo Working directory: %ROOT_DIR%

if not exist "%SKILL_NAME%\" (
  echo Error: %SKILL_NAME% directory not found under %ROOT_DIR%
  exit /b 1
)

echo Starting backup for %SKILL_NAME% ...
tar --format=zip -cf "%SKILL_NAME%.bak" "%SKILL_NAME%"
if errorlevel 1 (
  echo Backup failed. This script requires Windows tar with --format=zip support.
  exit /b 1
)

echo Backup complete, removing original directory ...
rmdir /s /q "%SKILL_NAME%"
if errorlevel 1 (
  echo Failed to remove %SKILL_NAME%.
  exit /b 1
)

set "TMP_ZIP=%TEMP%\%SKILL_NAME%_%RANDOM%.zip"
echo Downloading latest %SKILL_NAME%.zip from remote ...
curl -fSL "https://gts-download.obs.myhuaweicloud.com/skills/%SKILL_NAME%.zip" -o "%TMP_ZIP%"
if errorlevel 1 (
  echo Download failed.
  del /f /q "%TMP_ZIP%" 2>nul
  exit /b 1
)

echo Extracting to %ROOT_DIR% ...
tar -xf "%TMP_ZIP%"
if errorlevel 1 (
  echo Extract failed.
  del /f /q "%TMP_ZIP%" 2>nul
  exit /b 1
)

del /f /q "%TMP_ZIP%" 2>nul
echo Update completed.
exit /b 0
