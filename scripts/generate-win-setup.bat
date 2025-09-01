@echo off
set INNOSETUP_DIR="C:\Program Files (x86)\Inno Setup 6"

cd docs
call make html
cd ..

pyinstaller --clean --noconfirm rekhtanavees.app.spec

%INNOSETUP_DIR%\ISCC.exe installer\rekhtanavees-installer.iss
