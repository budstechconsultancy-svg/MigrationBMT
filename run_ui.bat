@echo off
title RIM-BMT (Business Migration Tool) V3 Server
echo ===================================================
echo   RIM-BMT (Business Migration Tool) - V3.0
echo   Enterprise Tally-to-FinPixe Migration Engine
echo ===================================================
echo Launching Server on http://localhost:8888 ...
python -m uvicorn finfixe_migration_ui:app --host 0.0.0.0 --port 8888
pause
