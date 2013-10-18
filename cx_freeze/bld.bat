"c:\Program Files\7-Zip\7z.exe" x -otmp -aos cx_Freeze-4.3.1.win32-py3.3.exe

xcopy tmp\PLATLIB %SP_DIR% /E /I
xcopy tmp\SCRIPTS %SCRIPTS% /E /I

REM if "%PY3K%"=="1" (
REM     %SYS_PREFIX%\Scripts\prepend-dlls %SP_DIR%\cx_Freeze\__init__.py
REM     if errorlevel 1 exit 1
REM )
