@echo off
INNOSETUP_DIR="C:\Program Files (x86)\Inno Setup 6"

pyinstaller rekhtanavees.app.spec

%INNOSETUP_DIR%\ISCC.exe installer\rekhtanavees-installer.iss
