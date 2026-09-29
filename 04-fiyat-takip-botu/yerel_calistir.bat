@echo off
rem Botu bu bilgisayarda calistirir (Windows Gorev Zamanlayici icin).
rem GitHub'daki veritabanina karismasin diye ayri bir dosya kullanir: veri\yerel.sqlite
cd /d "%~dp0"
set FIYAT_DB=%~dp0veri\yerel.sqlite
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\.venv\Scripts\python.exe"
if not exist "%FIYAT_DB%" %PY% gecmis_yukle.py >> "%~dp0veri\yerel_kayit.txt" 2>&1
echo ===== %date% %time% >> "%~dp0veri\yerel_kayit.txt"
%PY% fiyat_takip.py >> "%~dp0veri\yerel_kayit.txt" 2>&1
