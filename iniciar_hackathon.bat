@echo off
echo Iniciando o ambiente TAGVision PID...

:: Verificacoes simples
if not exist .venv (
    echo [ERRO] .venv nao encontrado!
    pause
    exit /b
)
if not exist frontend (
    echo [ERRO] Pasta frontend nao encontrada!
    pause
    exit /b
)
if not exist frontend\package.json (
    echo [ERRO] frontend\package.json nao encontrado!
    pause
    exit /b
)

echo Iniciando backend...
start "Backend" .\.venv\Scripts\python.exe -m uvicorn projeto.api:app --reload

echo Iniciando frontend...
cd frontend
start "Frontend" npm run dev

echo Aguardando inicializacao...
timeout /t 5 >nul

echo Abrindo navegador...
start http://localhost:5173

echo.
echo ==================================================
echo Sistema TAGVision PID iniciado com sucesso!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ==================================================
pause
