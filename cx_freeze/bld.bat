
if defined ProgramFiles(x86) (
    "c:\Program Files\7-Zip\7z.exe" x -otmp -aos cx_Freeze-4.3.3.win-amd64-py3.4.exe

) else (
    "c:\Program Files\7-Zip\7z.exe" x -otmp -aos cx_Freeze-4.3.3.win32-py3.4.exe

)

xcopy tmp\PLATLIB %SP_DIR% /E /I
xcopy tmp\SCRIPTS %SCRIPTS% /E /I
