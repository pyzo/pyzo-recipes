
if defined ProgramFiles(x86) (
    "c:\Program Files\7-Zip\7z.exe" x -otmp -aos scikit-learn-0.15-git.win-amd64-py3.4.exe

) else (
    "c:\Program Files\7-Zip\7z.exe" x -otmp -aos scikit-learn-0.15-git.win32-py3.4.exe

)

xcopy tmp\PLATLIB %SP_DIR% /E /I
REM no scripts for sklearn xcopy tmp\SCRIPTS %SCRIPTS% /E /I

if errorlevel 1 exit 1