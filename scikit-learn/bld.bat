
if defined ProgramFiles(x86) (
    "c:\Program Files\7-Zip\7z.exe" x -otmp -aos scikit-learn-0.14.1.win-amd64-py3.3.exe

) else (
    "c:\Program Files\7-Zip\7z.exe" x -otmp -aos scikit-learn-0.14.1.win32-py3.3.exe

)

xcopy tmp\PLATLIB %SP_DIR% /E /I
REM no scripts for sklearn xcopy tmp\SCRIPTS %SCRIPTS% /E /I
