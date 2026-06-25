@echo off

REM Create zip file from gisnet_qtools folder
set SOURCE_FOLDER=..\gisnet_qtools
set ZIP_FILE=gisnet_qtools.zip

if not exist "%SOURCE_FOLDER%" (
    echo Error: Folder "%SOURCE_FOLDER%" not found
    exit /b 1
)

REM Copy LICENSE file to source folder to include it in the zip
copy /Y "..\LICENSE" "%SOURCE_FOLDER%\LICENSE"

REM Create zip file using PowerShell available on Windows
if exist "%ZIP_FILE%" del /f /q "%ZIP_FILE%"
powershell -NoProfile -Command "Compress-Archive -Path '%SOURCE_FOLDER%' -DestinationPath '%ZIP_FILE%' -Force"

REM Clean up the copied LICENSE file
del /f /q "%SOURCE_FOLDER%\LICENSE"

if errorlevel 1 (
    echo Error: Failed to create zip file
    exit /b 1
)

echo Successfully created %ZIP_FILE%
