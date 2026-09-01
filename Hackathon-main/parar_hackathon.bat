@echo off
echo Encerrando processos do TAGVision PID...

:: Encerrando pelo titulo das janelas abertas pelo start
taskkill /FI "WINDOWTITLE eq Backend" /T /F
taskkill /FI "WINDOWTITLE eq Frontend" /T /F

echo Processos encerrados.
pause
